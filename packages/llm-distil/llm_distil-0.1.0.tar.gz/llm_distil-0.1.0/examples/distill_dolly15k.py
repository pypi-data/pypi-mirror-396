"""
Dolly-15k Knowledge Distillation Example
=========================================

This example demonstrates how to use llm_distil to distill a GPT-2 Medium teacher
into a GPT-2 Small student using the Databricks Dolly-15k instruction dataset.

We compare four approaches:
1. Baseline: Student trained from scratch (no distillation)
2. KD: Standard knowledge distillation (forward KL)
3. RevKD: Reverse knowledge distillation (reverse KL)
4. GKD: Generalized knowledge distillation (JSD with on-policy generation)

Dataset: Databricks Dolly-15k (15,000 instruction-response pairs)
Teacher: GPT-2 Medium (345M parameters)
Student: GPT-2 Small (117M parameters)
Evaluation: ROUGE-L and Perplexity
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
import pandas as pd
from pathlib import Path
import logging

from llm_distil import (
    KnowledgeDistillation,
    ReverseKnowledgeDistillation,
    GeneralizedKnowledgeDistillation,
    DistillationConfig
)
from llm_distil.metrics import compute_perplexity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main training and evaluation pipeline."""
    
    print("=" * 80)
    print("Dolly-15k Knowledge Distillation Comparison")
    print("=" * 80)
    
    # ============================================================
    # 1. Setup: Load Dataset and Models
    # ============================================================
    print("\n[Step 1] Loading dataset and models...")
    
    # Configuration
    teacher_name = 'gpt2-medium'
    student_name = 'gpt2'
    max_length = 256
    batch_size = 4  # Adjust based on GPU memory
    epochs = 1  # Quick demo - increase for better results
    
    # Load dataset
    print(f"\nLoading Dolly-15k dataset...")
    dataset = load_dataset("databricks/databricks-dolly-15k", split="train[:200]")
    
    print(f"✓ Loaded {len(dataset)} examples")
    
    # Load tokenizer
    print("\nLoading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(student_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    # Tokenize dataset
    def tokenize_function(examples):
        texts = [f"{inst}\n{resp}" for inst, resp in zip(examples["instruction"], examples["response"])]
        return tokenizer(
            texts,
            truncation=True,
            padding="max_length",
            max_length=max_length
        )
    
    print("Tokenizing dataset...")
    tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=dataset.column_names)
    
    # Split into train/eval
    train_dataset = tokenized_dataset.select(range(160))
    eval_dataset = tokenized_dataset.select(range(160, 200))
    
    print(f"✓ Train: {len(train_dataset)} examples")
    print(f"✓ Eval: {len(eval_dataset)} examples")
    
    # Load models
    print(f"\nLoading teacher model: {teacher_name}...")
    teacher_model = AutoModelForCausalLM.from_pretrained(teacher_name)
    print(f"✓ Teacher params: {teacher_model.num_parameters():,}")
    
    print(f"\nLoading student models: {student_name}...")
    student_model_baseline = AutoModelForCausalLM.from_pretrained(student_name)
    student_model_kd = AutoModelForCausalLM.from_pretrained(student_name)
    student_model_revkd = AutoModelForCausalLM.from_pretrained(student_name)
    student_model_gkd = AutoModelForCausalLM.from_pretrained(student_name)
    print(f"✓ Student params: {student_model_baseline.num_parameters():,}")
    
    print(f"\n📊 Compression ratio: {teacher_model.num_parameters() / student_model_baseline.num_parameters():.2f}x")
    print("\n✓ Dataset and models loaded!")
    
    # ============================================================
    # 2. Baseline: Train Student Without Distillation
    # ============================================================
    print("\n" + "=" * 80)
    print("[Step 2] Training Baseline Student (No Distillation)")
    print("=" * 80)
    
    # Create a dummy config with zero KD loss weight (pure task loss)
    baseline_config = DistillationConfig(
        teacher_model_name=teacher_name,
        student_model_name=student_name,
        temperature=1.0,
        kd_loss_weight=0.0,  # No distillation
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=2e-5,
        max_length=max_length,
        output_dir='./outputs/dolly_baseline',
        save_checkpoints=True,
        logging_steps=10,
        save_steps=500,
        seed=42
    )
    
    baseline_kd = KnowledgeDistillation(teacher_model, student_model_baseline, baseline_config)
    baseline_history = baseline_kd.train(train_dataset, eval_dataset)
    
    print("\n✓ Baseline training complete!")
    
    # ============================================================
    # 3. Standard Knowledge Distillation (KD)
    # ============================================================
    print("\n" + "=" * 80)
    print("[Step 3] Training with Standard KD (Forward KL)")
    print("=" * 80)
    
    kd_config = DistillationConfig(
        teacher_model_name=teacher_name,
        student_model_name=student_name,
        temperature=2.0,  # Common temperature for KD
        kd_loss_weight=0.5,  # 50% KD loss, 50% task loss
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=2e-5,
        max_length=max_length,
        output_dir='./outputs/dolly_kd',
        save_checkpoints=True,
        logging_steps=10,
        save_steps=500,
        seed=42
    )
    
    kd = KnowledgeDistillation(teacher_model, student_model_kd, kd_config)
    kd_history = kd.train(train_dataset, eval_dataset)
    
    print("\n✓ KD training complete!")
    
    # ============================================================
    # 4. Reverse Knowledge Distillation (RevKD)
    # ============================================================
    print("\n" + "=" * 80)
    print("[Step 4] Training with Reverse KD (Reverse KL)")
    print("=" * 80)
    
    revkd_config = DistillationConfig(
        teacher_model_name=teacher_name,
        student_model_name=student_name,
        temperature=2.0,
        kd_loss_weight=0.5,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=2e-5,
        max_length=max_length,
        output_dir='./outputs/dolly_revkd',
        save_checkpoints=True,
        logging_steps=10,
        save_steps=500,
        seed=42
    )
    
    revkd = ReverseKnowledgeDistillation(teacher_model, student_model_revkd, revkd_config)
    revkd_history = revkd.train(train_dataset, eval_dataset)
    
    print("\n✓ RevKD training complete!")
    
    # ============================================================
    # 5. Generalized Knowledge Distillation (GKD)
    # ============================================================
    print("\n" + "=" * 80)
    print("[Step 5] Training with GKD (On-Policy JSD)")
    print("=" * 80)
    
    gkd_config = DistillationConfig(
        teacher_model_name=teacher_name,
        student_model_name=student_name,
        temperature=1.0,  # Lower temperature for GKD
        kd_loss_weight=0.5,
        lambda_gkd=0.5,  # 50% on-policy generation
        beta_gkd=0.5,    # Symmetric JSD
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=2e-5,
        max_length=max_length,
        output_dir='./outputs/dolly_gkd',
        save_checkpoints=True,
        logging_steps=10,
        save_steps=500,
        seed=42
    )
    
    gkd = GeneralizedKnowledgeDistillation(teacher_model, student_model_gkd, gkd_config)
    gkd_history = gkd.train(train_dataset, eval_dataset)
    
    print("\n✓ GKD training complete!")
    
    # ============================================================
    # 6. Evaluation: Compare All Methods
    # ============================================================
    print("\n" + "=" * 80)
    print("[Step 6] Evaluating All Methods")
    print("=" * 80)
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # Evaluate perplexity for all models
    print("\nComputing perplexities...")
    
    print("[1/5] Evaluating teacher...")
    teacher_ppl = compute_perplexity(
        teacher_model, eval_dataset, tokenizer, device=device, batch_size=batch_size
    )
    
    print("[2/5] Evaluating baseline student...")
    baseline_ppl = compute_perplexity(
        student_model_baseline, eval_dataset, tokenizer, device=device, batch_size=batch_size
    )
    
    print("[3/5] Evaluating KD student...")
    kd_metrics = kd.evaluate(eval_dataset)
    kd_ppl = kd_metrics['perplexity']
    
    print("[4/5] Evaluating RevKD student...")
    revkd_metrics = revkd.evaluate(eval_dataset)
    revkd_ppl = revkd_metrics['perplexity']
    
    print("[5/5] Evaluating GKD student...")
    gkd_metrics = gkd.evaluate(eval_dataset)
    gkd_ppl = gkd_metrics['perplexity']
    
    # Create results table
    results = {
        'Method': ['Teacher', 'Baseline (No KD)', 'KD (Forward KL)', 'RevKD (Reverse KL)', 'GKD (JSD)'],
        'Model': [teacher_name, student_name, student_name, student_name, student_name],
        'Perplexity': [teacher_ppl, baseline_ppl, kd_ppl, revkd_ppl, gkd_ppl],
        'Temperature': ['-', '-', 2.0, 2.0, 1.0],
        'KD Weight': ['-', 0.0, 0.5, 0.5, 0.5]
    }
    
    df = pd.DataFrame(results)
    
    # Print results
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print("\n" + df.to_string(index=False))
    
    # Save results
    output_dir = Path('./outputs')
    output_dir.mkdir(exist_ok=True)
    df.to_csv(output_dir / 'dolly_distillation_results.csv', index=False)
    print(f"\n✓ Results saved to {output_dir / 'dolly_distillation_results.csv'}")
    
    # ============================================================
    # 7. Text Generation Comparison
    # ============================================================
    print("\n" + "=" * 80)
    print("[Step 7] Text Generation Comparison")
    print("=" * 80)
    
    test_prompts = [
        "What is machine learning?",
        "Explain the concept of knowledge distillation.",
        "What is the capital of France?"
    ]
    
    models = {
        'Teacher': teacher_model,
        'Baseline': student_model_baseline,
        'KD': student_model_kd,
        'RevKD': student_model_revkd,
        'GKD': student_model_gkd
    }
    
    for prompt in test_prompts:
        print(f"\n{'='*80}")
        print(f"Prompt: {prompt}")
        print(f"{'='*80}")
        
        inputs = tokenizer(prompt, return_tensors='pt').to(device)
        
        for name, model in models.items():
            model.eval()
            model.to(device)
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=50,
                    do_sample=True,
                    temperature=0.8,
                    top_p=0.9,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"\n[{name}]")
            print(generated_text)
            print("-" * 80)
    
    # ============================================================
    # 8. Save All Models
    # ============================================================
    print("\n" + "=" * 80)
    print("[Step 8] Saving Models")
    print("=" * 80)
    
    baseline_kd.save_student('./outputs/models/baseline_student')
    kd.save_student('./outputs/models/kd_student')
    revkd.save_student('./outputs/models/revkd_student')
    gkd.save_student('./outputs/models/gkd_student')
    
    print("\n✓ All models saved!")
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎉 EXPERIMENT COMPLETE!")
    print("=" * 80)
    print("\nKey Findings:")
    print(f"  • Teacher perplexity: {teacher_ppl:.2f}")
    print(f"  • Best student perplexity: {min(baseline_ppl, kd_ppl, revkd_ppl, gkd_ppl):.2f}")
    
    # Find best distillation method (excluding Teacher and Baseline)
    student_ppls = {'Baseline (No KD)': baseline_ppl, 'KD (Forward KL)': kd_ppl, 
                    'RevKD (Reverse KL)': revkd_ppl, 'GKD (JSD)': gkd_ppl}
    best_method = min(student_ppls, key=student_ppls.get)
    print(f"  • Best method: {best_method}")
    
    print("\nAll results and models saved to ./outputs/")
    print("=" * 80)


if __name__ == "__main__":
    main()
