# API Guide

Complete API reference for the `llm_distil` library.

## Table of Contents

1. [Distillation Classes](#distillation-classes)
   - [KnowledgeDistillation](#knowledgedistillation)
   - [ReverseKnowledgeDistillation](#reverseknowledgedistillation)
   - [GeneralizedKnowledgeDistillation](#generalizedknowledgedistillation)
2. [Configuration](#configuration)
3. [Loss Functions](#loss-functions)
4. [Metrics](#metrics)
5. [Utilities](#utilities)
6. [Complete Examples](#complete-examples)
7. [Common Pitfalls](#common-pitfalls)

---

## Distillation Classes

All distillation classes share a common interface:

```python
class BaseDistillation:
    def __init__(self, teacher_model, student_model, config)
    def train(self, train_dataset, eval_dataset=None)
    def evaluate(self, eval_dataset)
    def save_student(self, output_dir)
    def load_student(self, model_path)
```

**Key Implementation Details:**
- Teacher model automatically moves to student's device (no manual device management needed)
- Uses `DataCollatorForLanguageModeling` internally for causal LM tasks
- `eval_strategy` parameter (not `evaluation_strategy`) for HuggingFace Trainer compatibility
- `compute_perplexity` requires tokenizer parameter for proper evaluation

### KnowledgeDistillation

Standard knowledge distillation using forward KL divergence.

**Loss Function:**
```
L_KD = (1 - α) * L_CE + α * T² * KL(Teacher || Student)
```

Where:
- `L_CE`: Cross-entropy loss on true labels
- `T`: Temperature (softens distributions)
- `α`: `kd_loss_weight` (balance between losses)
- T² scaling preserves gradient magnitudes

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `teacher_model` | `PreTrainedModel` | Required | Teacher model (larger, already trained) |
| `student_model` | `PreTrainedModel` | Required | Student model (smaller, to be distilled) |
| `config` | `DistillationConfig` | Required | Configuration object |

**Configuration Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `temperature` | float | 2.0 | Softening temperature (higher = softer) |
| `kd_loss_weight` | float | 0.5 | Weight for KD loss (0=CE only, 1=KD only) |
| `epochs` | int | 3 | Number of training epochs |
| `batch_size` | int | 8 | Batch size per GPU |
| `learning_rate` | float | 5e-5 | Learning rate |
| `max_length` | int | 512 | Maximum sequence length |

**Example:**

```python
from llm_distil import KnowledgeDistillation, DistillationConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load models
teacher = AutoModelForCausalLM.from_pretrained("gpt2-medium")
student = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token

# Configure
config = DistillationConfig(
    teacher_model_name="gpt2-medium",
    student_model_name="gpt2",
    temperature=2.0,
    kd_loss_weight=0.5,
    epochs=3,
)

# Train
kd = KnowledgeDistillation(teacher, student, config)
kd.train(train_dataset, eval_dataset)

# Evaluate
metrics = kd.evaluate(test_dataset)
print(f"Perplexity: {metrics['perplexity']:.2f}")

# Save
kd.save_student("./distilled_model")
```

**When to Use:**
- General-purpose distillation
- Want student to cover all teacher behaviors (mean-seeking)
- Teacher has multi-modal distributions

---

### ReverseKnowledgeDistillation

Reverse KL divergence (mode-seeking behavior).

**Loss Function:**
```
L_RevKD = (1 - α) * L_CE + α * T² * KL(Student || Teacher)
```

**Key Difference from KD:**
- Forward KL (`Teacher || Student`): Student covers all teacher modes (mean-seeking)
- Reverse KL (`Student || Teacher`): Student focuses on teacher's peak modes (mode-seeking)

**Example:**

```python
from llm_distil import ReverseKnowledgeDistillation

# Same setup as KD
revkd = ReverseKnowledgeDistillation(teacher, student, config)
revkd.train(train_dataset, eval_dataset)
```

**When to Use:**
- Want student to focus on high-confidence predictions
- Teacher has sparse, peaked distributions
- Generation tasks where diversity is less important

---

### GeneralizedKnowledgeDistillation

Generalized JSD with on-policy generation.

**Loss Function:**
```
L_GKD = λ * JSD(Teacher, Student) + (1 - λ) * JSD(Teacher, Student_generated)
```

Where:
- `λ`: `lambda_gkd` (mixture weight)
- `β`: `beta_gkd` (on-policy weight, alternative parameterization)
- `Student_generated`: Student generates sequences during training

**JSD (Jensen-Shannon Divergence):**
```
JSD(P, Q) = 0.5 * KL(P || M) + 0.5 * KL(Q || M)
M = 0.5 * (P + Q)
```

**Configuration Fields (in addition to standard fields):**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `lambda_gkd` | float | 0.5 | Off-policy weight (0=all on-policy, 1=all off-policy) |
| `beta_gkd` | float | 0.5 | Alternative to lambda (on-policy weight) |
| `max_new_tokens` | int | 128 | Tokens to generate for on-policy samples |

**Example:**

```python
from llm_distil import GeneralizedKnowledgeDistillation, DistillationConfig

# GKD-specific config
config = DistillationConfig(
    teacher_model_name="gpt2-medium",
    student_model_name="gpt2",
    lambda_gkd=0.5,  # 50% off-policy, 50% on-policy
    beta_gkd=0.5,
    epochs=3,
)

gkd = GeneralizedKnowledgeDistillation(teacher, student, config)
gkd.train(train_dataset, eval_dataset)
```

**When to Use:**
- Generative tasks (text generation, summarization)
- Want more robust distillation with student's own generations
- Avoid exposure bias (student seeing only teacher's distribution)

---

## Parameter-Efficient Fine-Tuning (PEFT)

All distillation classes support PEFT methods for memory-efficient training.

### Benefits of PEFT

- **Memory Efficient**: Train large models on consumer GPUs (e.g., RTX 3090)
- **Fast Training**: Fewer parameters to update means faster iterations
- **Easy Deployment**: Save only adapters (~few MB vs ~500MB+ for full models)
- **Multi-Task**: Train multiple adapters for one base model

### Supported PEFT Methods

| Method | Description | Trainable Params | Best For |
|--------|-------------|------------------|----------|
| **LoRA** | Low-Rank Adaptation | 0.1-1% | General-purpose, best performance/efficiency trade-off |
| **QLoRA** | Quantized LoRA (4-bit/8-bit) | 0.1-1% | Extreme memory constraints, largest models |
| **Prefix Tuning** | Learn prefix vectors | <1% | Tasks where prompt-like control helps |
| **Prompt Tuning** | Learn soft prompts | <0.1% | Simplest method, good for task adaptation |
| **IA3** | Infused Adapter | <0.1% | Ultra-efficient, good for small tasks |

### LoRA Configuration

```python
from llm_distil import KnowledgeDistillation, DistillationConfig

config = DistillationConfig(
    teacher_model_name="gpt2-medium",
    student_model_name="gpt2",
    use_peft=True,  # Enable PEFT
    peft_type="lora",  # Choose method
    lora_r=8,  # LoRA rank (4-64, higher=more capacity)
    lora_alpha=16,  # LoRA scaling (usually 2*r)
    lora_dropout=0.1,  # Dropout for regularization
    lora_target_modules=None,  # None = auto-detect
    lora_bias="none",  # "none", "all", "lora_only"
    learning_rate=1e-4  # Higher LR often works better for LoRA
)

kd = KnowledgeDistillation(teacher, student, config)
kd.train(train_dataset, eval_dataset)
```

### QLoRA Configuration

For extremely large models with 4-bit quantization:

```python
from transformers import BitsAndBytesConfig
import torch

# Load student with 4-bit quantization
quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

student = AutoModelForCausalLM.from_pretrained(
    "gpt2",
    quantization_config=quant_config,
    device_map="auto"
)

config = DistillationConfig(
    teacher_model_name="gpt2-medium",
    student_model_name="gpt2",
    use_peft=True,
    peft_type="qlora",
    lora_r=8,
    lora_alpha=16
)
```

### LoRA Hyperparameter Guide

**`lora_r` (rank)**:
- 4-8: Good for small tasks, very efficient
- 8-16: Balanced trade-off (recommended)
- 16-64: More capacity, closer to full fine-tuning

**`lora_alpha` (scaling)**:
- Rule of thumb: `alpha = 2 * r`
- Higher alpha = stronger LoRA influence

**`lora_target_modules`**:
- `None`: Auto-detect (recommended)
- GPT-2: `["c_attn"]` or `["c_attn", "c_proj"]`
- LLaMA: `["q_proj", "v_proj"]` or `["q_proj", "k_proj", "v_proj", "o_proj"]`

### Installation for PEFT

```bash
pip install peft>=0.7.0
pip install bitsandbytes>=0.41.0  # For QLoRA
pip install accelerate>=0.24.0  # Recommended
```

### Example: Full vs LoRA Comparison

See [`examples/distill_with_lora.py`](../examples/distill_with_lora.py) for a complete comparison.

**Typical Results (GPT-2 124M → LoRA)**:
- Trainable params: 294,912 / 124,439,808 (0.24%)
- Memory usage: ~2GB vs ~8GB (full fine-tuning)
- Training speed: ~1.5x faster
- Model storage: ~2MB (adapters) vs ~500MB (full model)
- Performance: Within 1-2% of full fine-tuning

---

## Configuration

### DistillationConfig

Dataclass for all distillation parameters.

**Full Parameter List:**

```python
@dataclass
class DistillationConfig:
    # Model identifiers
    teacher_model_name: str
    student_model_name: str
    
    # KD/RevKD parameters
    temperature: float = 2.0
    kd_loss_weight: float = 0.5
    
    # GKD parameters
    lambda_gkd: float = 0.5
    beta_gkd: float = 0.5
    
    # Training parameters
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 8
    per_device_eval_batch_size: int = 8
    learning_rate: float = 5e-5
    weight_decay: float = 0.01
    warmup_steps: int = 500
    logging_steps: int = 100
    eval_steps: int = 500
    save_steps: int = 500
    max_length: int = 512
    max_new_tokens: int = 128
    output_dir: str = "./output"
    
    # Advanced
    gradient_accumulation_steps: int = 1
    max_grad_norm: float = 1.0
    fp16: bool = False
    seed: int = 42
```

**Methods:**

- `to_dict()`: Convert to dictionary
- `from_dict(config_dict)`: Create from dictionary
- `save(filepath)`: Save to JSON file
- `load(filepath)`: Load from JSON file

**Example:**

```python
# Create config
config = DistillationConfig(
    teacher_model_name="gpt2-large",
    student_model_name="distilgpt2",
    temperature=3.0,
    epochs=5,
    learning_rate=1e-4,
)

# Save config
config.save("config.json")

# Load config
loaded_config = DistillationConfig.load("config.json")
```

**Validation:**

Config validates parameters in `__post_init__`:
- `temperature > 0`
- `0 <= kd_loss_weight <= 1`
- `0 <= lambda_gkd <= 1`
- `epochs > 0`
- `learning_rate > 0`

---

## Loss Functions

Low-level loss functions (usually not called directly).

### sequence_kl_divergence

Forward KL divergence for sequences.

```python
from llm_distil.losses import sequence_kl_divergence

loss = sequence_kl_divergence(
    teacher_logits,  # [batch, seq_len, vocab_size]
    student_logits,  # [batch, seq_len, vocab_size]
    temperature=2.0,
    attention_mask=mask  # [batch, seq_len]
)
```

### sequence_reverse_kl_divergence

Reverse KL divergence for sequences.

```python
from llm_distil.losses import sequence_reverse_kl_divergence

loss = sequence_reverse_kl_divergence(
    teacher_logits,
    student_logits,
    temperature=2.0,
    attention_mask=mask
)
```

### generalized_jsd_loss

Generalized Jensen-Shannon divergence.

```python
from llm_distil.losses import generalized_jsd_loss

loss = generalized_jsd_loss(
    teacher_logits,
    student_logits,
    lambda_weight=0.5,
    attention_mask=mask
)
```

---

## Metrics

### compute_rouge

Compute ROUGE scores between predictions and references.

```python
from llm_distil.metrics import compute_rouge

rouge_scores = compute_rouge(
    predictions=["The cat sat on the mat"],
    references=["A cat was sitting on a mat"]
)
# Returns: {'rouge1': ..., 'rouge2': ..., 'rougeL': ...}
```

### compute_perplexity

Compute perplexity on a dataset.

```python
from llm_distil.metrics import compute_perplexity

perplexity = compute_perplexity(
    model, 
    eval_dataset,  # HuggingFace Dataset or DataLoader
    tokenizer,  # Required for proper evaluation
    device="cuda",
    batch_size=8
)
```

**Note:** Handles both HuggingFace `Dataset` objects and PyTorch `DataLoader` objects.

### compute_bleu

Compute BLEU scores.

```python
from llm_distil.metrics import compute_bleu

bleu_scores = compute_bleu(
    predictions=["The cat sat on the mat"],
    references=[["A cat was sitting on a mat"]]
)
# Returns: {'bleu': ..., 'precisions': [...], 'brevity_penalty': ..., 'length_ratio': ...}
```

### MetricTracker

Track metrics during training.

```python
from llm_distil.metrics import MetricTracker

tracker = MetricTracker()
tracker.update("train_loss", 2.5)
tracker.update("train_loss", 2.3)

avg_loss = tracker.get_average("train_loss")  # 2.4
metrics = tracker.get_all_metrics()  # {'train_loss': 2.4}
```

---

## Utilities

### get_tokenizer

Load tokenizer with standard defaults.

```python
from llm_distil.utils import get_tokenizer

tokenizer = get_tokenizer("gpt2")
# Automatically sets pad_token = eos_token if needed
```

### get_vocab_size

Get vocabulary size for a model.

```python
from llm_distil.utils import get_vocab_size

vocab_size = get_vocab_size("gpt2")  # 50257
```

---

## Complete Examples

### Example 1: Distill GPT2-medium to GPT2

```python
from llm_distil import KnowledgeDistillation, DistillationConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

# Load models
teacher = AutoModelForCausalLM.from_pretrained("gpt2-medium")
student = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token

# Load dataset
dataset = load_dataset("databricks/databricks-dolly-15k", split="train[:1000]")

# Tokenize
def tokenize_function(examples):
    return tokenizer(
        examples["instruction"],
        truncation=True,
        padding="max_length",
        max_length=512
    )

tokenized_dataset = dataset.map(tokenize_function, batched=True)
train_dataset = tokenized_dataset.select(range(800))
eval_dataset = tokenized_dataset.select(range(800, 1000))

# Configure
config = DistillationConfig(
    teacher_model_name="gpt2-medium",
    student_model_name="gpt2",
    temperature=2.0,
    kd_loss_weight=0.5,
    epochs=3,
    batch_size=8,
    learning_rate=5e-5,
)

# Train
kd = KnowledgeDistillation(teacher, student, config)
kd.train(train_dataset, eval_dataset)

# Evaluate
metrics = kd.evaluate(eval_dataset)
print(f"Perplexity: {metrics['perplexity']:.2f}")

# Save
kd.save_student("./distilled_gpt2")
```

### Example 2: Compare All Three Methods

```python
import pandas as pd
from llm_distil import (
    KnowledgeDistillation,
    ReverseKnowledgeDistillation,
    GeneralizedKnowledgeDistillation,
    DistillationConfig
)

# Shared config
base_config = DistillationConfig(
    teacher_model_name="gpt2-medium",
    student_model_name="gpt2",
    epochs=3,
)

# Train with KD
kd = KnowledgeDistillation(teacher, student, base_config)
kd.train(train_dataset, eval_dataset)
kd_metrics = kd.evaluate(eval_dataset)

# Train with RevKD
student_revkd = AutoModelForCausalLM.from_pretrained("gpt2")
revkd = ReverseKnowledgeDistillation(teacher, student_revkd, base_config)
revkd.train(train_dataset, eval_dataset)
revkd_metrics = revkd.evaluate(eval_dataset)

# Train with GKD
student_gkd = AutoModelForCausalLM.from_pretrained("gpt2")
gkd_config = base_config
gkd_config.lambda_gkd = 0.5
gkd = GeneralizedKnowledgeDistillation(teacher, student_gkd, gkd_config)
gkd.train(train_dataset, eval_dataset)
gkd_metrics = gkd.evaluate(eval_dataset)

# Compare
results = pd.DataFrame({
    "Method": ["KD", "RevKD", "GKD"],
    "Perplexity": [
        kd_metrics['perplexity'],
        revkd_metrics['perplexity'],
        gkd_metrics['perplexity']
    ]
})
print(results)
```

---

## Common Pitfalls

### 1. Vocabulary Size Mismatch

**Problem:** Teacher and student have different vocabulary sizes.

**Solution:** Library handles this automatically by using `min(teacher_vocab, student_vocab)` in loss computation.

```python
# Handled internally - no action needed
# If you need to check:
from llm_distil.utils import get_vocab_size
teacher_vocab = get_vocab_size("gpt2-medium")  # 50257
student_vocab = get_vocab_size("gpt2")  # 50257
```

### 2. Padding Token Not Set

**Problem:** Tokenizer doesn't have a pad token (common with GPT2).

**Solution:**

```python
tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token
```

Or use `get_tokenizer`:

```python
from llm_distil.utils import get_tokenizer
tokenizer = get_tokenizer("gpt2")  # Automatically sets pad_token
```

### 3. Dataset Format

**Problem:** Dataset doesn't have `input_ids` and `attention_mask`.

**Solution:** Tokenize first:

```python
def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=512
    )

tokenized_dataset = dataset.map(tokenize_function, batched=True)
```

### 4. Memory Issues

**Problem:** OOM errors during training.

**Solution:** Reduce batch size or use gradient accumulation:

```python
config = DistillationConfig(
    batch_size=4,  # Reduce from 8
    gradient_accumulation_steps=2,  # Effective batch size = 4 * 2 = 8
)
```

### 5. Temperature Too High/Low

**Problem:** Loss explodes or student doesn't learn.

**Solution:** Use temperature in range [1.0, 5.0], typically 2.0-3.0:

```python
config = DistillationConfig(
    temperature=2.0,  # Good starting point
)
```

### 6. GKD Requires Prompts

**Problem:** GKD needs `prompt_input_ids` and `prompt_attention_mask` in dataset.

**Solution:** Add prompts to dataset:

```python
def add_prompts(examples):
    # Extract first few tokens as prompt
    prompt_length = 32
    examples['prompt_input_ids'] = [ids[:prompt_length] for ids in examples['input_ids']]
    examples['prompt_attention_mask'] = [mask[:prompt_length] for mask in examples['attention_mask']]
    return examples

dataset = dataset.map(add_prompts)
```

### 7. Model Not on Correct Device

**Problem:** Models on CPU when GPU available.

**Solution:** Models are automatically moved to the correct device by `Trainer`. No action needed.

---

## Advanced Topics

### Custom Training Arguments

Pass custom `TrainingArguments` to the trainer:

```python
from transformers import TrainingArguments

custom_args = TrainingArguments(
    output_dir="./custom_output",
    evaluation_strategy="steps",
    eval_steps=100,
    save_strategy="steps",
    save_steps=500,
    logging_steps=50,
    report_to="wandb",  # Log to Weights & Biases
)

kd = KnowledgeDistillation(config, teacher, student, tokenizer)
# Pass custom args in train()
kd.train(train_dataset, eval_dataset, training_args=custom_args)
```

### Mixed Precision Training

Enable FP16 for faster training:

```python
config = DistillationConfig(
    fp16=True,
    # ... other params
)
```

### Custom Evaluation

Implement custom evaluation logic:

```python
# Evaluate with custom metrics
metrics = kd.evaluate(eval_dataset)

# Generate text samples
from llm_distil.metrics import compute_rouge

prompt = "Once upon a time"
inputs = tokenizer(prompt, return_tensors="pt").to(student.device)

with torch.no_grad():
    student_output = student.generate(**inputs, max_new_tokens=100)
    teacher_output = teacher.generate(**inputs, max_new_tokens=100)

student_text = tokenizer.decode(student_output[0], skip_special_tokens=True)
teacher_text = tokenizer.decode(teacher_output[0], skip_special_tokens=True)

rouge = compute_rouge([student_text], [teacher_text])
print(f"ROUGE-L: {rouge['rougeL']:.4f}")
```

---

## Examples and Tutorials

### Python Scripts

**1. All Methods Comparison** - [`examples/distill_dolly15k.py`](../examples/distill_dolly15k.py)
- Complete 8-step pipeline
- Compares KD, RevKD, and GKD
- Includes text generation and model saving
- Quick demo (200 examples, 1 epoch)

**2. LoRA vs Full Fine-tuning** - [`examples/distill_with_lora.py`](../examples/distill_with_lora.py)
- Parameter-efficient distillation with LoRA
- Side-by-side comparison with full fine-tuning
- Shows trainable parameters and storage savings
- Demonstrates 99% parameter reduction

### Interactive Notebooks

**1. Standard Distillation Demo** - [`notebooks/dolly15k_distillation_demo.ipynb`](../notebooks/dolly15k_distillation_demo.ipynb)
- Interactive tutorial for all 3 distillation methods
- Step-by-step explanations
- Visualizations and comparisons
- Best for learning the basics

**2. LoRA Distillation Demo** - [`notebooks/lora_distillation_demo.ipynb`](../notebooks/lora_distillation_demo.ipynb)
- Full fine-tuning vs LoRA comparison
- 10 sections covering complete workflow
- Matplotlib visualizations (perplexity, parameters)
- Text generation examples
- Model size comparison and recommendations
- Additional experiments section (QLoRA, Prefix Tuning, etc.)

### Quick Start Guide

**For Standard Distillation:**
```bash
# Run the complete comparison
python examples/distill_dolly15k.py

# Or use the notebook
jupyter notebook notebooks/dolly15k_distillation_demo.ipynb
```

**For Parameter-Efficient Distillation:**
```bash
# First install PEFT
pip install peft bitsandbytes accelerate

# Run LoRA comparison
python examples/distill_with_lora.py

# Or use the notebook
jupyter notebook notebooks/lora_distillation_demo.ipynb
```
