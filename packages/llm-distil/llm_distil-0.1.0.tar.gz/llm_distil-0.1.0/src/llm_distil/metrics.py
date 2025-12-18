"""
Evaluation metrics for language model distillation.

Provides ROUGE, perplexity, and BLEU metrics using HuggingFace evaluate library.
"""
import torch
import evaluate
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)


def compute_rouge(
    predictions: List[str],
    references: List[str],
    rouge_types: Optional[List[str]] = None
) -> Dict[str, float]:
    """
    Compute ROUGE scores for text generation.
    
    ROUGE (Recall-Oriented Understudy for Gisting Evaluation) measures
    the overlap between generated and reference texts.
    
    Args:
        predictions: List of generated texts
        references: List of reference texts
        rouge_types: ROUGE variants to compute
                    Default: ['rouge1', 'rouge2', 'rougeL', 'rougeLsum']
    
    Returns:
        Dictionary with ROUGE scores
    
    Example:
        ```python
        from llm_distil.metrics import compute_rouge
        
        predictions = ["The cat sat on the mat", "Hello world"]
        references = ["A cat was sitting on a mat", "Hello there"]
        
        scores = compute_rouge(predictions, references)
        print(f"ROUGE-L: {scores['rougeL']:.4f}")
        ```
    """
    if rouge_types is None:
        rouge_types = ['rouge1', 'rouge2', 'rougeL', 'rougeLsum']
    
    try:
        rouge = evaluate.load('rouge')
        results = rouge.compute(
            predictions=predictions,
            references=references,
            rouge_types=rouge_types
        )
        
        logger.info(f"Computed ROUGE scores: {results}")
        return results
    
    except Exception as e:
        logger.error(f"Failed to compute ROUGE: {e}")
        raise


def compute_perplexity(
    model,
    dataset,
    tokenizer,
    device: str = 'cuda',
    batch_size: int = 8,
    max_length: int = 512
) -> float:
    """
    Compute perplexity of a language model on a dataset.
    
    Perplexity measures how well the model predicts the data.
    Lower perplexity indicates better performance.
    
    Formula: perplexity = exp(average_loss)
    
    Args:
        model: PyTorch language model
        dataset: Dataset or DataLoader
        tokenizer: HuggingFace tokenizer
        device: Device to run on ('cuda' or 'cpu')
        batch_size: Batch size for evaluation
        max_length: Maximum sequence length
    
    Returns:
        Perplexity value (float)
    
    Example:
        ```python
        from llm_distil.metrics import compute_perplexity
        
        perplexity = compute_perplexity(
            model=student_model,
            dataset=eval_dataset,
            tokenizer=tokenizer,
            device='cuda'
        )
        print(f"Model perplexity: {perplexity:.2f}")
        ```
    """
    model.eval()
    model.to(device)
    
    total_loss = 0.0
    total_tokens = 0
    
    # Handle both Dataset and DataLoader
    if hasattr(dataset, '__iter__') and hasattr(dataset, 'batch_size'):
        # It's already a DataLoader
        dataloader = dataset
    else:
        # It's a Dataset, create DataLoader
        from torch.utils.data import DataLoader
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Computing perplexity"):
            # Get inputs
            if isinstance(batch, dict):
                # Handle input_ids - could be tensor, list of tensors, or list of lists
                if torch.is_tensor(batch['input_ids']):
                    input_ids = batch['input_ids'].to(device)
                elif isinstance(batch['input_ids'], list):
                    # List of sequences - convert to tensor
                    if len(batch['input_ids']) > 0 and torch.is_tensor(batch['input_ids'][0]):
                        input_ids = torch.stack(batch['input_ids']).to(device)
                    else:
                        input_ids = torch.tensor(batch['input_ids'], dtype=torch.long).to(device)
                else:
                    input_ids = batch['input_ids'].to(device)
                
                # Handle labels
                if 'labels' in batch:
                    if torch.is_tensor(batch['labels']):
                        labels = batch['labels'].to(device)
                    elif isinstance(batch['labels'], list):
                        if len(batch['labels']) > 0 and torch.is_tensor(batch['labels'][0]):
                            labels = torch.stack(batch['labels']).to(device)
                        else:
                            labels = torch.tensor(batch['labels'], dtype=torch.long).to(device)
                    else:
                        labels = batch['labels'].to(device)
                else:
                    labels = input_ids.clone()
            else:
                input_ids = batch.to(device)
                labels = input_ids
            
            # Forward pass
            outputs = model(input_ids=input_ids, labels=labels)
            loss = outputs.loss
            
            # Accumulate loss
            # Count non-padding tokens if labels have -100
            if (labels == -100).any():
                valid_tokens = (labels != -100).sum().item()
            else:
                valid_tokens = labels.numel()
            
            total_loss += loss.item() * valid_tokens
            total_tokens += valid_tokens
    
    # Compute average loss and perplexity
    avg_loss = total_loss / total_tokens
    perplexity = np.exp(avg_loss)
    
    logger.info(f"Perplexity: {perplexity:.4f} (avg loss: {avg_loss:.4f})")
    return perplexity


def compute_bleu(
    predictions: List[str],
    references: List[List[str]],
    max_order: int = 4
) -> Dict[str, float]:
    """
    Compute BLEU score for text generation.
    
    BLEU (Bilingual Evaluation Understudy) measures n-gram overlap
    between generated and reference texts.
    
    Args:
        predictions: List of generated texts
        references: List of lists of reference texts (multiple references per prediction)
        max_order: Maximum n-gram order (default: 4 for BLEU-4)
    
    Returns:
        Dictionary with BLEU scores
    
    Example:
        ```python
        from llm_distil.metrics import compute_bleu
        
        predictions = ["The cat sat on the mat"]
        references = [["A cat was sitting on a mat", "The cat is on the mat"]]
        
        scores = compute_bleu(predictions, references)
        print(f"BLEU-4: {scores['bleu']:.4f}")
        ```
    """
    try:
        bleu = evaluate.load('bleu')
        results = bleu.compute(
            predictions=predictions,
            references=references,
            max_order=max_order
        )
        
        logger.info(f"Computed BLEU scores: {results}")
        return results
    
    except Exception as e:
        logger.error(f"Failed to compute BLEU: {e}")
        raise


class MetricTracker:
    """
    Track multiple metrics during training/evaluation.
    
    Example:
        ```python
        tracker = MetricTracker(['rouge', 'perplexity'])
        
        # During training
        tracker.update('rouge', epoch=1, value=0.35)
        tracker.update('perplexity', epoch=1, value=25.4)
        
        # Get history
        history = tracker.get_history()
        ```
    """
    
    def __init__(self, metric_names: List[str]):
        """
        Initialize metric tracker.
        
        Args:
            metric_names: List of metric names to track
        """
        self.metric_names = metric_names
        self.history = {name: [] for name in metric_names}
    
    def update(self, metric_name: str, epoch: int, value: float):
        """Add a metric value."""
        if metric_name not in self.metric_names:
            logger.warning(f"Unknown metric: {metric_name}")
            return
        
        self.history[metric_name].append({
            'epoch': epoch,
            'value': value
        })
    
    def get_history(self) -> Dict[str, List[Dict[str, float]]]:
        """Get full metric history."""
        return self.history
    
    def get_latest(self, metric_name: str) -> Optional[float]:
        """Get latest value for a metric."""
        if metric_name in self.history and self.history[metric_name]:
            return self.history[metric_name][-1]['value']
        return None
    
    def get_best(self, metric_name: str, mode: str = 'max') -> Optional[float]:
        """
        Get best value for a metric.
        
        Args:
            metric_name: Name of metric
            mode: 'max' for metrics where higher is better (e.g., ROUGE),
                  'min' for metrics where lower is better (e.g., perplexity)
        """
        if metric_name not in self.history or not self.history[metric_name]:
            return None
        
        values = [item['value'] for item in self.history[metric_name]]
        
        if mode == 'max':
            return max(values)
        else:
            return min(values)
