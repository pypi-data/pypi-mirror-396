"""
Configuration classes for LLM distillation.
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
import json
from pathlib import Path


@dataclass
class DistillationConfig:
    """
    Configuration for knowledge distillation training.
    
    This config controls all aspects of the distillation process including
    model selection, training hyperparameters, and distillation-specific settings.
    
    Args:
        teacher_model_name: HuggingFace model name for teacher (e.g., 'gpt2-medium')
        student_model_name: HuggingFace model name for student (e.g., 'gpt2')
        
        # Distillation parameters
        temperature: Temperature for softening distributions (1.0-10.0, higher = softer)
        kd_loss_weight: Weight for KD loss vs task loss (0.0-1.0, 1.0 = only KD)
        
        # Training hyperparameters
        epochs: Number of training epochs
        batch_size: Training batch size
        learning_rate: Learning rate for optimizer
        max_length: Maximum sequence length in tokens
        warmup_steps: Number of warmup steps for learning rate scheduler
        weight_decay: Weight decay for AdamW optimizer
        max_grad_norm: Maximum gradient norm for clipping
        
        # GKD-specific parameters
        lambda_gkd: Probability of using student-generated sequences (0.0-1.0)
        beta_gkd: Mixture weight for JSD computation (0.5 = symmetric)
        
        # Optional features
        inject_noise: Whether to add noise to teacher logits (regularization)
        noise_scale: Standard deviation of noise if inject_noise=True
        
        # System settings
        output_dir: Directory for saving checkpoints and logs
        save_checkpoints: Whether to save model checkpoints during training
        logging_steps: Log metrics every N steps
        save_steps: Save checkpoint every N steps
        eval_steps: Evaluate every N steps (if eval_dataset provided)
        seed: Random seed for reproducibility
        fp16: Use mixed precision training (faster on modern GPUs)
        dataloader_num_workers: Number of workers for DataLoader
        
        # Logging
        report_to: Logging backend ('wandb', 'tensorboard', or None)
        wandb_project: W&B project name (if report_to='wandb')
        wandb_run_name: W&B run name (if report_to='wandb')
    
    Example:
        ```python
        from llm_distil import DistillationConfig, KnowledgeDistillation
        
        config = DistillationConfig(
            teacher_model_name='gpt2-medium',
            student_model_name='gpt2',
            temperature=2.0,
            kd_loss_weight=0.5,
            epochs=3,
            batch_size=8,
            learning_rate=2e-5
        )
        
        kd = KnowledgeDistillation(teacher_model, student_model, config)
        ```
    """
    # Required parameters
    teacher_model_name: str
    student_model_name: str
    
    # Distillation parameters
    temperature: float = 2.0
    kd_loss_weight: float = 0.5
    
    # Training hyperparameters
    epochs: int = 3
    batch_size: int = 8
    learning_rate: float = 2e-5
    max_length: int = 512
    warmup_steps: int = 100
    weight_decay: float = 0.01
    max_grad_norm: float = 1.0
    
    # GKD-specific (only used by GeneralizedKnowledgeDistillation)
    lambda_gkd: float = 0.5
    beta_gkd: float = 0.5
    
    # PEFT (Parameter-Efficient Fine-Tuning) settings
    use_peft: bool = False
    peft_type: str = "lora"  # "lora", "qlora", "prefix", "prompt", "ia3"
    lora_r: int = 8  # LoRA rank
    lora_alpha: int = 16  # LoRA alpha (scaling factor)
    lora_dropout: float = 0.1  # LoRA dropout
    lora_target_modules: Optional[list] = None  # None = auto-detect
    lora_bias: str = "none"  # "none", "all", "lora_only"
    
    # Optional features
    inject_noise: bool = False
    noise_scale: float = 0.001
    
    # System settings
    output_dir: str = './distillation_outputs'
    save_checkpoints: bool = True
    logging_steps: int = 50
    save_steps: int = 500
    eval_steps: int = 500
    seed: int = 42
    fp16: bool = False
    dataloader_num_workers: int = 0
    
    # Logging
    report_to: Optional[str] = None  # 'wandb', 'tensorboard', or None
    wandb_project: str = 'llm-distillation'
    wandb_run_name: Optional[str] = None
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if self.temperature <= 0:
            raise ValueError(f"temperature must be positive, got {self.temperature}")
        
        if not 0 <= self.kd_loss_weight <= 1:
            raise ValueError(f"kd_loss_weight must be in [0, 1], got {self.kd_loss_weight}")
        
        if not 0 <= self.lambda_gkd <= 1:
            raise ValueError(f"lambda_gkd must be in [0, 1], got {self.lambda_gkd}")
        
        if not 0 <= self.beta_gkd <= 1:
            raise ValueError(f"beta_gkd must be in [0, 1], got {self.beta_gkd}")
        
        if self.epochs <= 0:
            raise ValueError(f"epochs must be positive, got {self.epochs}")
        
        if self.batch_size <= 0:
            raise ValueError(f"batch_size must be positive, got {self.batch_size}")
        
        # Validate PEFT parameters
        if self.use_peft:
            valid_peft_types = ["lora", "qlora", "prefix", "prompt", "ia3"]
            if self.peft_type.lower() not in valid_peft_types:
                raise ValueError(f"peft_type must be one of {valid_peft_types}, got {self.peft_type}")
            
            if self.lora_r <= 0:
                raise ValueError(f"lora_r must be positive, got {self.lora_r}")
            
            if self.lora_alpha <= 0:
                raise ValueError(f"lora_alpha must be positive, got {self.lora_alpha}")
            
            if not 0 <= self.lora_dropout < 1:
                raise ValueError(f"lora_dropout must be in [0, 1), got {self.lora_dropout}")
        
        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'DistillationConfig':
        """Create config from dictionary."""
        return cls(**config_dict)
    
    def save(self, path: str):
        """
        Save configuration to JSON file.
        
        Args:
            path: Path to save config (e.g., 'config.json')
        """
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'DistillationConfig':
        """
        Load configuration from JSON file.
        
        Args:
            path: Path to config file
        
        Returns:
            DistillationConfig instance
        """
        with open(path, 'r') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)
    
    def update(self, **kwargs) -> 'DistillationConfig':
        """
        Update config parameters.
        
        Args:
            **kwargs: Parameters to update
        
        Returns:
            Updated config instance
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown parameter: {key}")
        return self
