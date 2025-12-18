"""
llm_distil: Knowledge Distillation for Large Language Models

A clean, minimal library for distilling large language models using three
proven methods: Standard KD, Reverse KD, and Generalized KD (GKD).

Quick Start:
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
    
    # Train with standard KD
    kd = KnowledgeDistillation(teacher, student, config)
    history = kd.train(train_dataset, eval_dataset)
    
    # Save student
    kd.save_student('./student_model')
    ```

Three Distillation Methods:
    - KnowledgeDistillation: Standard forward KL divergence (mode-covering)
    - ReverseKnowledgeDistillation: Reverse KL divergence (mode-seeking)
    - GeneralizedKnowledgeDistillation: JSD with on-policy generation

See examples/ directory for complete usage examples.
"""

# Core distillation classes
from .kd_trainer import (
    KnowledgeDistillation,
    ReverseKnowledgeDistillation,
    GeneralizedKnowledgeDistillation
)

# Configuration
from .config import DistillationConfig

# Utilities
from .utils import get_vocab_size, get_tokenizer

# Metrics
from .metrics import compute_rouge, compute_perplexity, compute_bleu, MetricTracker

# Version
from .__version__ import __version__

__all__ = [
    # Main classes
    'KnowledgeDistillation',
    'ReverseKnowledgeDistillation',
    'GeneralizedKnowledgeDistillation',
    
    # Configuration
    'DistillationConfig',
    
    # Utilities
    'get_vocab_size',
    'get_tokenizer',
    
    # Metrics
    'compute_rouge',
    'compute_perplexity',
    'compute_bleu',
    'MetricTracker',
    
    # Version
    '__version__'
]

# Set up logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"llm_distil v{__version__} initialized")
