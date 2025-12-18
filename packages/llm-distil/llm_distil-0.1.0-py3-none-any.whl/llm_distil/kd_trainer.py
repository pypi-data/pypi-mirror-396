"""
Knowledge Distillation trainer classes.

Implements three distillation methods:
- KnowledgeDistillation: Standard forward KL divergence
- ReverseKnowledgeDistillation: Reverse KL divergence
- GeneralizedKnowledgeDistillation: JSD with on-policy generation
"""
import torch
import torch.nn as nn
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    GenerationConfig,
    DataCollatorForLanguageModeling,
    set_seed
)
from typing import Optional, Dict, Any, List
import logging
import random
from pathlib import Path

# PEFT imports (optional dependency)
try:
    from peft import (
        get_peft_model,
        LoraConfig,
        PrefixTuningConfig,
        PromptTuningConfig,
        IA3Config,
        TaskType,
        prepare_model_for_kbit_training,
        PeftModel
    )
    PEFT_AVAILABLE = True
except ImportError:
    PEFT_AVAILABLE = False
    logger.warning("PEFT library not available. Install with: pip install peft")

from .config import DistillationConfig
from .losses import sequence_kl_divergence, sequence_reverse_kl_divergence, generalized_jsd_loss
from .metrics import compute_rouge, compute_perplexity

logger = logging.getLogger(__name__)


class _DistillationTrainer(Trainer):
    """
    Custom Trainer for knowledge distillation.
    
    Extends HuggingFace Trainer to support KD loss computation.
    This is an internal class - users should use KnowledgeDistillation,
    ReverseKnowledgeDistillation, or GeneralizedKnowledgeDistillation.
    """
    
    def __init__(
        self,
        distillation_method: str,  # 'kld', 'reversekld', 'gkd'
        teacher_model,
        kd_loss_weight: float,
        temperature: float,
        inject_noise: bool,
        noise_scale: float,
        lambda_gkd: float,
        beta_gkd: float,
        tokenizer=None,
        max_length: int = 512,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.distillation_method = distillation_method
        self.teacher_model = teacher_model
        self.kd_loss_weight = kd_loss_weight
        self.temperature = temperature
        self.inject_noise = inject_noise
        self.noise_scale = noise_scale
        self.lambda_gkd = lambda_gkd
        self.beta_gkd = beta_gkd
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Move teacher to same device as student
        if self.teacher_model is not None:
            self.teacher_model.eval()
            for param in self.teacher_model.parameters():
                param.requires_grad = False
        
        # Setup generation config for GKD
        if self.distillation_method == 'gkd' and self.tokenizer:
            self.generation_config = GenerationConfig(
                temperature=1.0,
                do_sample=True,
                top_k=0,
                use_cache=True,
                pad_token_id=self.tokenizer.pad_token_id,
            )
    
    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        """
        Compute combined task loss and KD loss.
        
        Formula: total_loss = (1 - alpha) * task_loss + alpha * kd_loss
        where alpha = kd_loss_weight
        """
        # For GKD: randomly use student-generated sequences
        if self.distillation_method == 'gkd' and random.random() <= self.lambda_gkd:
            inputs = self._generate_on_policy(model, inputs)
        
        # Forward pass through student
        outputs = model(**inputs)
        task_loss = outputs.loss
        
        # Forward pass through teacher (no gradients)
        # Ensure teacher is on the same device as student
        teacher_device = next(self.teacher_model.parameters()).device
        model_device = next(model.parameters()).device
        if teacher_device != model_device:
            self.teacher_model.to(model_device)
        
        with torch.no_grad():
            self.teacher_model.eval()
            teacher_outputs = self.teacher_model(**inputs)
        
        # Extract logits
        teacher_logits = teacher_outputs.logits
        student_logits = outputs.logits
        
        # Optional: inject noise to teacher logits (regularization)
        if self.inject_noise:
            noise = torch.randn_like(teacher_logits) * self.noise_scale
            teacher_logits = teacher_logits + noise
        
        # Handle vocab size mismatch (e.g., Qwen models)
        if teacher_logits.shape[-1] != student_logits.shape[-1]:
            common_vocab = min(teacher_logits.shape[-1], student_logits.shape[-1])
            teacher_logits = teacher_logits[:, :, :common_vocab]
            student_logits = student_logits[:, :, :common_vocab]
        
        # Compute KD loss based on distillation method
        if self.distillation_method == 'kld':
            kd_loss = sequence_kl_divergence(
                student_logits,
                teacher_logits,
                temperature=self.temperature,
                pad_mask=inputs.get('attention_mask')
            )
        
        elif self.distillation_method == 'reversekld':
            kd_loss = sequence_reverse_kl_divergence(
                student_logits,
                teacher_logits,
                temperature=self.temperature,
                pad_mask=inputs.get('attention_mask')
            )
        
        elif self.distillation_method == 'gkd':
            kd_loss = generalized_jsd_loss(
                student_logits,
                teacher_logits,
                labels=inputs.get('labels'),
                beta=self.beta_gkd,
                temperature=self.temperature
            )
        
        else:
            raise ValueError(f"Unknown distillation method: {self.distillation_method}")
        
        # Combine losses
        total_loss = (1 - self.kd_loss_weight) * task_loss + self.kd_loss_weight * kd_loss
        
        return (total_loss, outputs) if return_outputs else total_loss
    
    def _generate_on_policy(self, model, inputs):
        """
        Generate sequences with student model for GKD (on-policy distillation).
        
        Extracts prompt from inputs, generates completion, returns new inputs.
        """
        model.eval()
        
        # Extract prompt using prompt_attention_mask
        prompt_mask = inputs.get('prompt_attention_mask')
        if prompt_mask is None:
            # If no prompt mask, return original inputs
            return inputs
        
        prompt_mask = prompt_mask.bool()
        prompt_input_ids_list = []
        
        for input_ids, mask in zip(inputs['input_ids'], prompt_mask):
            prompt_tokens = torch.masked_select(input_ids, mask).tolist()
            prompt_input_ids_list.append(prompt_tokens)
        
        # Pad prompts to equal length (left padding)
        max_prompt_len = max(len(seq) for seq in prompt_input_ids_list)
        pad_token_id = self.tokenizer.pad_token_id
        
        padded_prompts = []
        padded_masks = []
        
        for seq in prompt_input_ids_list:
            pad_len = max_prompt_len - len(seq)
            padded_seq = [pad_token_id] * pad_len + seq
            mask = [0] * pad_len + [1] * len(seq)
            padded_prompts.append(padded_seq)
            padded_masks.append(mask)
        
        # Convert to tensors
        prompt_input_ids = torch.tensor(padded_prompts, device=model.device)
        prompt_attention_mask = torch.tensor(padded_masks, device=model.device)
        
        # Generate completions
        max_new_tokens = self.max_length - max_prompt_len
        if max_new_tokens <= 0:
            return inputs
        
        generated_ids = model.generate(
            input_ids=prompt_input_ids,
            attention_mask=prompt_attention_mask,
            generation_config=self.generation_config,
            max_new_tokens=max_new_tokens
        )
        
        # Decode and re-tokenize (creates proper inputs with labels)
        generated_texts = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        new_inputs = self.tokenizer(
            generated_texts,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=self.max_length
        ).to(model.device)
        
        # Create labels (mask padding with -100)
        new_labels = new_inputs['input_ids'].clone()
        new_labels[new_labels == pad_token_id] = -100
        new_inputs['labels'] = new_labels
        
        model.train()
        return new_inputs


class KnowledgeDistillation:
    """
    Standard Knowledge Distillation using forward KL divergence.
    
    Trains a smaller student model to mimic a larger teacher model by
    minimizing the KL divergence from teacher to student distributions.
    
    Formula: KL(teacher || student)
    
    This is the most common distillation method from Hinton et al. (2015).
    It's "mode-covering" - the student tries to cover all modes of the teacher.
    
    Example:
        ```python
        from transformers import AutoModelForCausalLM
        from llm_distil import KnowledgeDistillation, DistillationConfig
        
        # Load models
        teacher = AutoModelForCausalLM.from_pretrained('gpt2-medium')
        student = AutoModelForCausalLM.from_pretrained('gpt2')
        
        # Configure distillation
        config = DistillationConfig(
            teacher_model_name='gpt2-medium',
            student_model_name='gpt2',
            temperature=2.0,
            kd_loss_weight=0.5,
            epochs=3,
            batch_size=8
        )
        
        # Create distiller
        kd = KnowledgeDistillation(teacher, student, config)
        
        # Train
        history = kd.train(train_dataset, eval_dataset)
        
        # Save student
        kd.save_student('./student_model')
        ```
    
    Args:
        teacher_model: Pretrained teacher model (will be frozen)
        student_model: Student model to train
        config: DistillationConfig with hyperparameters
    """
    
    def __init__(
        self,
        teacher_model: nn.Module,
        student_model: nn.Module,
        config: DistillationConfig
    ):
        self.teacher_model = teacher_model
        self.student_model = student_model
        self.config = config
        
        # Freeze teacher
        self.teacher_model.eval()
        for param in self.teacher_model.parameters():
            param.requires_grad = False
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(config.student_model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Apply PEFT if enabled
        if config.use_peft:
            logger.info(f"Applying PEFT ({config.peft_type}) to student model...")
            self.student_model = self._apply_peft(self.student_model)
            trainable_stats = self._count_trainable_params()
            logger.info(f"  Trainable parameters: {trainable_stats}")
        
        # Set seed
        set_seed(config.seed)
        
        logger.info(f"Initialized KnowledgeDistillation")
        logger.info(f"  Teacher: {config.teacher_model_name}")
        logger.info(f"  Student: {config.student_model_name}")
        logger.info(f"  Temperature: {config.temperature}")
        logger.info(f"  KD loss weight: {config.kd_loss_weight}")
    
    def _apply_peft(self, model: nn.Module) -> nn.Module:
        """
        Apply PEFT (Parameter-Efficient Fine-Tuning) to the model.
        
        Args:
            model: Model to apply PEFT to
        
        Returns:
            PEFT-wrapped model
        """
        if not PEFT_AVAILABLE:
            raise ImportError(
                "PEFT is required for parameter-efficient fine-tuning. "
                "Install with: pip install peft"
            )
        
        peft_type = self.config.peft_type.lower()
        
        if peft_type == "lora":
            peft_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=self.config.lora_r,
                lora_alpha=self.config.lora_alpha,
                lora_dropout=self.config.lora_dropout,
                target_modules=self.config.lora_target_modules,
                bias=self.config.lora_bias,
                inference_mode=False
            )
        elif peft_type == "qlora":
            # Prepare model for k-bit training (requires bitsandbytes)
            model = prepare_model_for_kbit_training(model)
            peft_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=self.config.lora_r,
                lora_alpha=self.config.lora_alpha,
                lora_dropout=self.config.lora_dropout,
                target_modules=self.config.lora_target_modules,
                bias=self.config.lora_bias,
                inference_mode=False
            )
        elif peft_type == "prefix":
            peft_config = PrefixTuningConfig(
                task_type=TaskType.CAUSAL_LM,
                num_virtual_tokens=20,
                prefix_projection=False
            )
        elif peft_type == "prompt":
            peft_config = PromptTuningConfig(
                task_type=TaskType.CAUSAL_LM,
                num_virtual_tokens=20
            )
        elif peft_type == "ia3":
            peft_config = IA3Config(
                task_type=TaskType.CAUSAL_LM,
                target_modules=self.config.lora_target_modules,
                feedforward_modules=["mlp"]
            )
        else:
            raise ValueError(f"Unsupported PEFT type: {peft_type}")
        
        return get_peft_model(model, peft_config)
    
    def _count_trainable_params(self) -> str:
        """
        Count trainable parameters in the model.
        
        Returns:
            String with trainable/total parameters and percentage
        """
        trainable = sum(p.numel() for p in self.student_model.parameters() if p.requires_grad)
        total = sum(p.numel() for p in self.student_model.parameters())
        percentage = 100 * trainable / total if total > 0 else 0
        return f"{trainable:,} / {total:,} ({percentage:.2f}%)"
    
    def train(
        self,
        train_dataset,
        eval_dataset=None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Train the student model with knowledge distillation.
        
        Args:
            train_dataset: Training dataset (PyTorch Dataset or DataLoader)
            eval_dataset: Optional evaluation dataset
            **kwargs: Additional arguments passed to TrainingArguments
        
        Returns:
            Training history dictionary
        """
        # Create training arguments
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.epochs,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            learning_rate=self.config.learning_rate,
            warmup_steps=self.config.warmup_steps,
            weight_decay=self.config.weight_decay,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_steps=self.config.eval_steps if eval_dataset else None,
            eval_strategy='steps' if eval_dataset else 'no',
            save_strategy='steps' if self.config.save_checkpoints else 'no',
            fp16=self.config.fp16,
            dataloader_num_workers=self.config.dataloader_num_workers,
            seed=self.config.seed,
            report_to=self.config.report_to if self.config.report_to else 'none',
            run_name=self.config.wandb_run_name,
            max_grad_norm=self.config.max_grad_norm,
            **kwargs
        )
        
        # Create data collator that adds labels for language modeling
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False  # Causal LM, not masked LM
        )
        
        # Create custom trainer
        trainer = _DistillationTrainer(
            distillation_method='kld',
            teacher_model=self.teacher_model,
            kd_loss_weight=self.config.kd_loss_weight,
            temperature=self.config.temperature,
            inject_noise=self.config.inject_noise,
            noise_scale=self.config.noise_scale,
            lambda_gkd=0.0,  # Not used for KD
            beta_gkd=0.5,  # Not used for KD
            tokenizer=self.tokenizer,
            max_length=self.config.max_length,
            model=self.student_model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
        )
        
        # Train
        logger.info("Starting training...")
        train_result = trainer.train()
        
        # Save final model
        if self.config.save_checkpoints:
            final_path = Path(self.config.output_dir) / "final_model"
            self.student_model.save_pretrained(final_path)
            self.tokenizer.save_pretrained(final_path)
            logger.info(f"Saved final model to {final_path}")
        
        return {
            'train_loss': train_result.training_loss,
            'metrics': train_result.metrics
        }
    
    def evaluate(
        self,
        eval_dataset,
        metrics: List[str] = ['rouge', 'perplexity']
    ) -> Dict[str, Any]:
        """
        Evaluate the student model.
        
        Args:
            eval_dataset: Evaluation dataset
            metrics: List of metrics to compute ('rouge', 'perplexity', 'bleu')
        
        Returns:
            Dictionary of evaluation metrics
        """
        results = {}
        
        # Compute perplexity
        if 'perplexity' in metrics:
            logger.info("Computing perplexity...")
            ppl = compute_perplexity(
                self.student_model,
                eval_dataset,
                self.tokenizer,
                device='cuda' if torch.cuda.is_available() else 'cpu'
            )
            results['perplexity'] = ppl
        
        # Compute ROUGE (requires text generation)
        if 'rouge' in metrics:
            logger.info("Computing ROUGE scores...")
            # This would require generating text and comparing to references
            # Implementation depends on dataset structure
            logger.warning("ROUGE computation requires custom implementation per dataset")
        
        return results
    
    def save_student(self, path: str):
        """
        Save the trained student model.
        
        For PEFT models, this saves only the adapter weights (much smaller).
        For full fine-tuning, saves the entire model.
        
        Args:
            path: Directory path to save model and tokenizer
        """
        Path(path).mkdir(parents=True, exist_ok=True)
        
        # Save model (PEFT-aware)
        if self.config.use_peft and PEFT_AVAILABLE and isinstance(self.student_model, PeftModel):
            # Save only adapter weights for PEFT
            self.student_model.save_pretrained(path)
            logger.info(f"Saved PEFT adapter to {path}")
            
            # Also save the config
            self.config.save(str(Path(path) / "distillation_config.json"))
        else:
            # Save full model
            self.student_model.save_pretrained(path)
            logger.info(f"Saved student model to {path}")
        
        # Save tokenizer
        self.tokenizer.save_pretrained(path)
        logger.info(f"Saved tokenizer to {path}")
    
    @classmethod
    def load_student(cls, path: str):
        """
        Load a trained student model.
        
        Args:
            path: Directory path containing saved model
        
        Returns:
            Loaded model and tokenizer
        """
        model = AutoModelForCausalLM.from_pretrained(path)
        tokenizer = AutoTokenizer.from_pretrained(path)
        logger.info(f"Loaded student model from {path}")
        return model, tokenizer


class ReverseKnowledgeDistillation(KnowledgeDistillation):
    """
    Reverse Knowledge Distillation using reverse KL divergence.
    
    Uses reverse KL divergence which is "mode-seeking" rather than "mode-covering".
    This often produces sharper, more confident predictions and may generalize
    better on out-of-distribution data.
    
    Formula: KL(student || teacher)
    
    Example:
        ```python
        from llm_distil import ReverseKnowledgeDistillation, DistillationConfig
        
        config = DistillationConfig(
            teacher_model_name='gpt2-medium',
            student_model_name='gpt2',
            temperature=2.0,
            kd_loss_weight=0.5
        )
        
        revkd = ReverseKnowledgeDistillation(teacher, student, config)
        history = revkd.train(train_dataset, eval_dataset)
        ```
    
    Args:
        teacher_model: Pretrained teacher model
        student_model: Student model to train
        config: DistillationConfig
    """
    
    def __init__(
        self,
        teacher_model: nn.Module,
        student_model: nn.Module,
        config: DistillationConfig
    ):
        super().__init__(teacher_model, student_model, config)
        logger.info("Initialized ReverseKnowledgeDistillation (mode-seeking)")
    
    def train(self, train_dataset, eval_dataset=None, **kwargs) -> Dict[str, Any]:
        """Train with reverse KL divergence."""
        # Create training arguments (same as base class)
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.epochs,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            learning_rate=self.config.learning_rate,
            warmup_steps=self.config.warmup_steps,
            weight_decay=self.config.weight_decay,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_steps=self.config.eval_steps if eval_dataset else None,
            eval_strategy='steps' if eval_dataset else 'no',
            save_strategy='steps' if self.config.save_checkpoints else 'no',
            fp16=self.config.fp16,
            dataloader_num_workers=self.config.dataloader_num_workers,
            seed=self.config.seed,
            report_to=self.config.report_to if self.config.report_to else 'none',
            run_name=self.config.wandb_run_name,
            max_grad_norm=self.config.max_grad_norm,
            **kwargs
        )
        
        # Create data collator that adds labels for language modeling
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False  # Causal LM, not masked LM
        )
        
        # Create custom trainer with 'reversekld' method
        trainer = _DistillationTrainer(
            distillation_method='reversekld',  # Key difference
            teacher_model=self.teacher_model,
            kd_loss_weight=self.config.kd_loss_weight,
            temperature=self.config.temperature,
            inject_noise=self.config.inject_noise,
            noise_scale=self.config.noise_scale,
            lambda_gkd=0.0,
            beta_gkd=0.5,
            tokenizer=self.tokenizer,
            max_length=self.config.max_length,
            model=self.student_model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
        )
        
        # Train
        logger.info("Starting training with Reverse KL...")
        train_result = trainer.train()
        
        # Save final model
        if self.config.save_checkpoints:
            final_path = Path(self.config.output_dir) / "final_model"
            self.student_model.save_pretrained(final_path)
            self.tokenizer.save_pretrained(final_path)
            logger.info(f"Saved final model to {final_path}")
        
        return {
            'train_loss': train_result.training_loss,
            'metrics': train_result.metrics
        }


class GeneralizedKnowledgeDistillation(KnowledgeDistillation):
    """
    Generalized Knowledge Distillation with on-policy generation.
    
    Uses Jensen-Shannon Divergence and supports on-policy learning where
    the student generates sequences that are then used for distillation.
    This is more sample-efficient and can lead to better generalization.
    
    Formula: JSD_beta(teacher || student)
    
    Key features:
    - Symmetric divergence (unlike KL)
    - On-policy generation (student generates training data)
    - Controlled by lambda (probability of using generated sequences)
    
    Example:
        ```python
        from llm_distil import GeneralizedKnowledgeDistillation, DistillationConfig
        
        config = DistillationConfig(
            teacher_model_name='gpt2-medium',
            student_model_name='gpt2',
            temperature=1.0,
            kd_loss_weight=0.5,
            lambda_gkd=0.5,  # 50% on-policy
            beta_gkd=0.5     # Symmetric JSD
        )
        
        gkd = GeneralizedKnowledgeDistillation(teacher, student, config)
        history = gkd.train(train_dataset, eval_dataset)
        ```
    
    Args:
        teacher_model: Pretrained teacher model
        student_model: Student model to train
        config: DistillationConfig (with lambda_gkd and beta_gkd)
    """
    
    def __init__(
        self,
        teacher_model: nn.Module,
        student_model: nn.Module,
        config: DistillationConfig
    ):
        super().__init__(teacher_model, student_model, config)
        logger.info("Initialized GeneralizedKnowledgeDistillation (GKD)")
        logger.info(f"  Lambda (on-policy probability): {config.lambda_gkd}")
        logger.info(f"  Beta (JSD mixture weight): {config.beta_gkd}")
    
    def train(self, train_dataset, eval_dataset=None, **kwargs) -> Dict[str, Any]:
        """Train with Generalized JSD and on-policy generation."""
        # Create training arguments
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.epochs,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            learning_rate=self.config.learning_rate,
            warmup_steps=self.config.warmup_steps,
            weight_decay=self.config.weight_decay,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_steps=self.config.eval_steps if eval_dataset else None,
            eval_strategy='steps' if eval_dataset else 'no',
            save_strategy='steps' if self.config.save_checkpoints else 'no',
            fp16=self.config.fp16,
            dataloader_num_workers=self.config.dataloader_num_workers,
            seed=self.config.seed,
            report_to=self.config.report_to if self.config.report_to else 'none',
            run_name=self.config.wandb_run_name,
            max_grad_norm=self.config.max_grad_norm,
            **kwargs
        )
        
        # Create data collator that adds labels for language modeling
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False  # Causal LM, not masked LM
        )
        
        # Create custom trainer with 'gkd' method
        trainer = _DistillationTrainer(
            distillation_method='gkd',  # Key difference
            teacher_model=self.teacher_model,
            kd_loss_weight=self.config.kd_loss_weight,
            temperature=self.config.temperature,
            inject_noise=self.config.inject_noise,
            noise_scale=self.config.noise_scale,
            lambda_gkd=self.config.lambda_gkd,  # On-policy probability
            beta_gkd=self.config.beta_gkd,      # JSD mixture weight
            tokenizer=self.tokenizer,
            max_length=self.config.max_length,
            model=self.student_model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
        )
        
        # Train
        logger.info("Starting training with GKD (on-policy distillation)...")
        train_result = trainer.train()
        
        # Save final model
        if self.config.save_checkpoints:
            final_path = Path(self.config.output_dir) / "final_model"
            self.student_model.save_pretrained(final_path)
            self.tokenizer.save_pretrained(final_path)
            logger.info(f"Saved final model to {final_path}")
        
        return {
            'train_loss': train_result.training_loss,
            'metrics': train_result.metrics
        }
