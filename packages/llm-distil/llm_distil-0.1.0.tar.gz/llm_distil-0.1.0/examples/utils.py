"""
Example utilities for loading datasets.

These are EXAMPLE utilities - NOT part of the core library.
Copy and modify for your own use cases.

Provides dataset wrappers for:
- Databricks Dolly-15k (instruction following)
- Generic instruction datasets
"""
import torch
from torch.utils.data import Dataset, DataLoader
from datasets import load_dataset
from transformers import AutoTokenizer
from typing import Optional, Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class DollyDataset(Dataset):
    """
    Dataset wrapper for Databricks Dolly-15k instruction dataset.
    
    Dolly-15k is a dataset of 15,000 instruction-response pairs
    for training instruction-following language models.
    
    This class formats the data with instruction prompts and creates
    proper input_ids and labels for language modeling.
    """
    
    def __init__(
        self,
        hf_dataset,
        tokenizer,
        max_length: int = 512,
        prompt_template: Optional[str] = None
    ):
        """
        Initialize Dolly dataset.
        
        Args:
            hf_dataset: HuggingFace dataset split (train/validation/test)
            tokenizer: HuggingFace tokenizer
            max_length: Maximum sequence length
            prompt_template: Optional custom prompt template
                           Default: "Below is an instruction..."
        """
        self.data = hf_dataset
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        if prompt_template is None:
            self.prompt_template = (
                "Below is an instruction that describes a task, paired with an input that provides further context. "
                "Write a response that appropriately completes the request.\n\n"
                "### Instruction:\n{instruction}\n\n"
                "### Input:\n{context}\n\n"
                "### Response:\n{response}"
            )
        else:
            self.prompt_template = prompt_template
        
        logger.info(f"Loaded Dolly dataset with {len(self.data)} examples")
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx) -> Dict[str, torch.Tensor]:
        item = self.data[idx]
        
        # Format instruction
        instruction = item.get('instruction', '')
        context = item.get('context', '')
        response = item.get('response', '')
        
        # Create full text
        full_text = self.prompt_template.format(
            instruction=instruction,
            context=context if context else "[No additional context]",
            response=response
        )
        
        # Tokenize
        encoding = self.tokenizer(
            full_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].squeeze(0)
        attention_mask = encoding['attention_mask'].squeeze(0)
        
        # For language modeling, labels = input_ids (shifted internally by model)
        labels = input_ids.clone()
        
        # Optional: Create prompt_attention_mask for GKD
        # This marks which tokens are part of the prompt (instruction + context)
        # vs the response (what we want to generate)
        prompt_text = self.prompt_template.format(
            instruction=instruction,
            context=context if context else "[No additional context]",
            response=""  # Empty response
        )
        prompt_encoding = self.tokenizer(
            prompt_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        prompt_attention_mask = prompt_encoding['attention_mask'].squeeze(0)
        
        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels,
            'prompt_attention_mask': prompt_attention_mask  # For GKD
        }


class InstructionDataset(Dataset):
    """
    Generic instruction dataset wrapper.
    
    Works with any dataset that has 'instruction', 'input', and 'output' fields.
    Similar to Alpaca format.
    """
    
    def __init__(
        self,
        hf_dataset,
        tokenizer,
        max_length: int = 512,
        instruction_field: str = 'instruction',
        input_field: str = 'input',
        output_field: str = 'output'
    ):
        """
        Initialize instruction dataset.
        
        Args:
            hf_dataset: HuggingFace dataset
            tokenizer: HuggingFace tokenizer
            max_length: Maximum sequence length
            instruction_field: Name of instruction field in dataset
            input_field: Name of input/context field
            output_field: Name of output/response field
        """
        self.data = hf_dataset
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.instruction_field = instruction_field
        self.input_field = input_field
        self.output_field = output_field
        
        logger.info(f"Loaded instruction dataset with {len(self.data)} examples")
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx) -> Dict[str, torch.Tensor]:
        item = self.data[idx]
        
        instruction = item.get(self.instruction_field, '')
        input_text = item.get(self.input_field, '')
        output = item.get(self.output_field, '')
        
        # Format text
        if input_text:
            full_text = f"Instruction: {instruction}\nInput: {input_text}\nResponse: {output}"
        else:
            full_text = f"Instruction: {instruction}\nResponse: {output}"
        
        # Tokenize
        encoding = self.tokenizer(
            full_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'labels': encoding['input_ids'].squeeze(0)
        }


def load_dolly_dataset(
    tokenizer_name: str = 'gpt2',
    max_length: int = 512,
    split_ratio: float = 0.9,
    batch_size: int = 8,
    num_workers: int = 0,
    shuffle: bool = True
) -> Tuple[DataLoader, DataLoader]:
    """
    Load Databricks Dolly-15k dataset with train/val split.
    
    Args:
        tokenizer_name: HuggingFace tokenizer name
        max_length: Maximum sequence length
        split_ratio: Train/validation split ratio (default: 0.9)
        batch_size: Batch size for DataLoaders
        num_workers: Number of workers for DataLoader
        shuffle: Whether to shuffle training data
    
    Returns:
        Tuple of (train_loader, val_loader)
    
    Example:
        ```python
        from examples.utils import load_dolly_dataset
        
        train_loader, val_loader = load_dolly_dataset(
            tokenizer_name='gpt2',
            max_length=512,
            batch_size=8
        )
        ```
    """
    logger.info("Loading Databricks Dolly-15k dataset...")
    
    # Load dataset
    dataset = load_dataset('databricks/databricks-dolly-15k')
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Split dataset
    full_data = dataset['train']
    train_size = int(len(full_data) * split_ratio)
    
    train_data = full_data.select(range(train_size))
    val_data = full_data.select(range(train_size, len(full_data)))
    
    logger.info(f"Train samples: {len(train_data)}")
    logger.info(f"Validation samples: {len(val_data)}")
    
    # Create datasets
    train_dataset = DollyDataset(train_data, tokenizer, max_length)
    val_dataset = DollyDataset(val_data, tokenizer, max_length)
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    return train_loader, val_loader


def collate_fn_with_padding(batch, tokenizer):
    """
    Custom collate function for dynamic padding.
    
    More memory efficient than padding to max_length.
    """
    input_ids = [item['input_ids'] for item in batch]
    attention_mask = [item['attention_mask'] for item in batch]
    labels = [item['labels'] for item in batch]
    
    # Pad to longest in batch
    input_ids = torch.nn.utils.rnn.pad_sequence(
        input_ids, batch_first=True, padding_value=tokenizer.pad_token_id
    )
    attention_mask = torch.nn.utils.rnn.pad_sequence(
        attention_mask, batch_first=True, padding_value=0
    )
    labels = torch.nn.utils.rnn.pad_sequence(
        labels, batch_first=True, padding_value=-100
    )
    
    result = {
        'input_ids': input_ids,
        'attention_mask': attention_mask,
        'labels': labels
    }
    
    # Add prompt_attention_mask if available
    if 'prompt_attention_mask' in batch[0]:
        prompt_masks = [item['prompt_attention_mask'] for item in batch]
        prompt_attention_mask = torch.nn.utils.rnn.pad_sequence(
            prompt_masks, batch_first=True, padding_value=0
        )
        result['prompt_attention_mask'] = prompt_attention_mask
    
    return result
