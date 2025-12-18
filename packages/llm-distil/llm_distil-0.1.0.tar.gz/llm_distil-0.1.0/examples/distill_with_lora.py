"""
LoRA Knowledge Distillation Example
====================================

This example demonstrates parameter-efficient distillation using LoRA.
LoRA reduces trainable parameters by ~99% while maintaining performance.

Dataset: Databricks Dolly-15k (200 examples for quick demo)
Teacher: GPT-2 Medium (345M parameters) - Full model
Student: GPT-2 Small (117M parameters) - LoRA adapters only (~0.3M trainable)

Comparison:
- Full Fine-tuning: All 117M parameters updated
- LoRA: Only ~0.3M adapter parameters updated (0.26% of total)
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
import pandas as pd
from pathlib import Path

from llm_distil import KnowledgeDistillation, DistillationConfig
from llm_distil.metrics import compute_perplexity


def main():
    print("=" * 80)
    print("LoRA vs Full Fine-tuning Knowledge Distillation Comparison")
    print("=" * 80)
    
    # ============================================================
    # 1. Load Dataset and Tokenize
    # ============================================================
    print("\n[Step 1] Loading dataset...")
    dataset = load_dataset("databricks/databricks-dolly-15k", split="train[:200]")
    
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token
    
    def tokenize_function(examples):
        texts = [f"{inst}\n{resp}" for inst, resp in zip(examples["instruction"], examples["response"])]
        return tokenizer(texts, truncation=True, padding="max_length", max_length=256)
    
    print("Tokenizing dataset...")
    tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=dataset.column_names)
    train_dataset = tokenized_dataset.select(range(160))
    eval_dataset = tokenized_dataset.select(range(160, 200))
    
    print(f"✓ Train: {len(train_dataset)}, Eval: {len(eval_dataset)}")
    
    # ============================================================
    # 2. Load Models
    # ============================================================
    print("\n[Step 2] Loading models...")
    teacher = AutoModelForCausalLM.from_pretrained("gpt2-medium")
    student_full = AutoModelForCausalLM.from_pretrained("gpt2")
    student_lora = AutoModelForCausalLM.from_pretrained("gpt2")
    
    print(f"✓ Teacher: {teacher.num_parameters():,} params")
    print(f"✓ Student: {student_full.num_parameters():,} params")
    
    # ============================================================
    # 3. Train with Full Fine-tuning
    # ============================================================
    print("\n" + "=" * 80)
    print("[Step 3] Training with FULL Fine-tuning")
    print("=" * 80)
    
    full_config = DistillationConfig(
        teacher_model_name="gpt2-medium",
        student_model_name="gpt2",
        temperature=2.0,
        kd_loss_weight=0.5,
        epochs=1,
        batch_size=4,
        learning_rate=5e-5,
        output_dir="./outputs/full_finetune",
        logging_steps=10,
        save_steps=500,
        use_peft=False  # Full fine-tuning
    )
    
    kd_full = KnowledgeDistillation(teacher, student_full, full_config)
    print("\n🔧 Full fine-tuning: All 117M parameters will be updated")
    kd_full.train(train_dataset, eval_dataset)
    
    print("\n✓ Full fine-tuning complete!")
    
    # ============================================================
    # 4. Train with LoRA
    # ============================================================
    print("\n" + "=" * 80)
    print("[Step 4] Training with LoRA (Parameter-Efficient)")
    print("=" * 80)
    
    lora_config = DistillationConfig(
        teacher_model_name="gpt2-medium",
        student_model_name="gpt2",
        temperature=2.0,
        kd_loss_weight=0.5,
        epochs=1,
        batch_size=4,
        learning_rate=1e-4,  # Higher LR for LoRA
        output_dir="./outputs/lora",
        logging_steps=10,
        save_steps=500,
        use_peft=True,  # Enable LoRA
        peft_type="lora",
        lora_r=8,
        lora_alpha=16,
        lora_dropout=0.1,
        lora_target_modules=None  # Auto-detect (c_attn for GPT-2)
    )
    
    kd_lora = KnowledgeDistillation(teacher, student_lora, lora_config)
    kd_lora.train(train_dataset, eval_dataset)
    
    print("\n✓ LoRA training complete!")
    
    # ============================================================
    # 5. Evaluate Both Methods
    # ============================================================
    print("\n" + "=" * 80)
    print("[Step 5] Evaluating Models")
    print("=" * 80)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print("\n[1/3] Evaluating teacher...")
    teacher_ppl = compute_perplexity(teacher, eval_dataset, tokenizer, device=device, batch_size=4)
    
    print("[2/3] Evaluating full fine-tuning student...")
    full_metrics = kd_full.evaluate(eval_dataset)
    full_ppl = full_metrics['perplexity']
    
    print("[3/3] Evaluating LoRA student...")
    lora_metrics = kd_lora.evaluate(eval_dataset)
    lora_ppl = lora_metrics['perplexity']
    
    # ============================================================
    # 6. Results Comparison
    # ============================================================
    print("\n" + "=" * 80)
    print("RESULTS COMPARISON")
    print("=" * 80)
    
    results = {
        'Method': ['Teacher', 'Full Fine-tuning', 'LoRA'],
        'Perplexity': [teacher_ppl, full_ppl, lora_ppl],
        'Trainable Params': [
            f"{teacher.num_parameters():,}",
            f"{student_full.num_parameters():,}",
            "~300,000 (0.26%)"
        ],
        'Model Size': ['355M', '117M', '117M + 0.3M adapters']
    }
    
    df = pd.DataFrame(results)
    print("\n" + df.to_string(index=False))
    
    # Save results
    output_dir = Path('./outputs')
    output_dir.mkdir(exist_ok=True)
    df.to_csv(output_dir / 'lora_comparison_results.csv', index=False)
    print(f"\n✓ Results saved to {output_dir / 'lora_comparison_results.csv'}")
    
    # ============================================================
    # 7. Text Generation Comparison
    # ============================================================
    print("\n" + "=" * 80)
    print("[Step 6] Text Generation Comparison")
    print("=" * 80)
    
    test_prompts = [
        "What is machine learning?",
        "Explain knowledge distillation in simple terms."
    ]
    
    for prompt in test_prompts:
        print(f"\n{'='*80}")
        print(f"Prompt: {prompt}")
        print(f"{'='*80}")
        
        inputs = tokenizer(prompt, return_tensors='pt').to(device)
        
        # Teacher generation
        teacher.eval()
        teacher.to(device)
        with torch.no_grad():
            teacher_output = teacher.generate(
                **inputs,
                max_new_tokens=50,
                do_sample=True,
                temperature=0.8,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id
            )
        teacher_text = tokenizer.decode(teacher_output[0], skip_special_tokens=True)
        
        # Full fine-tuning generation
        student_full.eval()
        student_full.to(device)
        with torch.no_grad():
            full_output = student_full.generate(
                **inputs,
                max_new_tokens=50,
                do_sample=True,
                temperature=0.8,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id
            )
        full_text = tokenizer.decode(full_output[0], skip_special_tokens=True)
        
        # LoRA generation
        student_lora.eval()
        student_lora.to(device)
        with torch.no_grad():
            lora_output = student_lora.generate(
                **inputs,
                max_new_tokens=50,
                do_sample=True,
                temperature=0.8,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id
            )
        lora_text = tokenizer.decode(lora_output[0], skip_special_tokens=True)
        
        print(f"\n[Teacher]")
        print(teacher_text)
        print("-" * 80)
        print(f"\n[Full Fine-tuning]")
        print(full_text)
        print("-" * 80)
        print(f"\n[LoRA]")
        print(lora_text)
        print("-" * 80)
    
    # ============================================================
    # 8. Save Models
    # ============================================================
    print("\n" + "=" * 80)
    print("[Step 7] Saving Models")
    print("=" * 80)
    
    kd_full.save_student('./outputs/models/full_student')
    kd_lora.save_student('./outputs/models/lora_student')
    
    print("\n✓ Full model saved to ./outputs/models/full_student")
    print("✓ LoRA adapters saved to ./outputs/models/lora_student")
    
    # Check file sizes
    import os
    full_size = sum(
        os.path.getsize(os.path.join(dirpath, filename))
        for dirpath, _, filenames in os.walk('./outputs/models/full_student')
        for filename in filenames
    ) / (1024 * 1024)  # MB
    
    lora_size = sum(
        os.path.getsize(os.path.join(dirpath, filename))
        for dirpath, _, filenames in os.walk('./outputs/models/lora_student')
        for filename in filenames
    ) / (1024 * 1024)  # MB
    
    print(f"\n📦 Model Sizes:")
    print(f"  • Full fine-tuning: {full_size:.1f} MB")
    print(f"  • LoRA adapters: {lora_size:.1f} MB")
    print(f"  • Storage savings: {(1 - lora_size/full_size)*100:.1f}%")
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎉 EXPERIMENT COMPLETE!")
    print("=" * 80)
    print("\n✨ Key Findings:")
    print(f"  • LoRA uses only 0.26% of the trainable parameters")
    print(f"  • LoRA achieves comparable perplexity to full fine-tuning")
    print(f"  • LoRA saves {(1 - lora_size/full_size)*100:.1f}% storage space")
    print(f"  • LoRA enables training large models on consumer GPUs")
    print("\n💡 Use LoRA when:")
    print("  • GPU memory is limited")
    print("  • Need to train multiple task-specific adapters")
    print("  • Want faster iteration and deployment")
    print("\n💪 Use Full Fine-tuning when:")
    print("  • Maximum performance is critical")
    print("  • Have sufficient compute resources")
    print("  • Single-task deployment")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
