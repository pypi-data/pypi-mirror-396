"""
Utility functions for LLM distillation.

Helper functions that assist with tokenizer loading and vocabulary size detection.
These are NOT dataset loaders - dataset loading belongs in examples/.
"""
from transformers import AutoTokenizer
import logging

logger = logging.getLogger(__name__)


def get_vocab_size(tokenizer_name: str) -> int:
    """
    Get vocabulary size from a HuggingFace tokenizer.
    
    This is a convenience function to help users automatically detect
    vocab_size from a tokenizer name.
    
    Args:
        tokenizer_name: HuggingFace tokenizer name
                       (e.g., 'gpt2', 'gpt2-medium', 'bert-base-uncased')
    
    Returns:
        Vocabulary size as integer
    
    Example:
        ```python
        from llm_distil.utils import get_vocab_size
        
        vocab_size = get_vocab_size('gpt2')  # Returns 50257
        print(f"GPT-2 vocabulary size: {vocab_size}")
        ```
    
    Raises:
        Exception: If tokenizer cannot be loaded
    """
    try:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        vocab_size = tokenizer.vocab_size
        logger.info(f"Vocabulary size for '{tokenizer_name}': {vocab_size}")
        return vocab_size
    except Exception as e:
        logger.error(f"Failed to load tokenizer '{tokenizer_name}': {e}")
        raise


def get_tokenizer(tokenizer_name: str, **kwargs) -> AutoTokenizer:
    """
    Load a HuggingFace tokenizer with common defaults.
    
    Args:
        tokenizer_name: HuggingFace tokenizer name
        **kwargs: Additional arguments passed to AutoTokenizer.from_pretrained
    
    Returns:
        Loaded tokenizer instance
    
    Example:
        ```python
        from llm_distil.utils import get_tokenizer
        
        tokenizer = get_tokenizer('gpt2')
        
        # For models without pad token (like GPT-2)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        ```
    
    Raises:
        Exception: If tokenizer cannot be loaded
    """
    try:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, **kwargs)
        logger.info(f"Loaded tokenizer: {tokenizer_name}")
        return tokenizer
    except Exception as e:
        logger.error(f"Failed to load tokenizer '{tokenizer_name}': {e}")
        raise
