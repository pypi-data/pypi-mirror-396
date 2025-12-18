"""
Loss functions for knowledge distillation.

Implements three distillation objectives:
- Standard KL Divergence (forward KL)
- Reverse KL Divergence
- Generalized Jensen-Shannon Divergence (for GKD)
"""
import torch
import torch.nn.functional as F
from typing import Optional


def sequence_kl_divergence(
    student_logits: torch.Tensor,
    teacher_logits: torch.Tensor,
    temperature: float = 1.0,
    epsilon: float = 1e-9,
    pad_mask: Optional[torch.Tensor] = None
) -> torch.Tensor:
    """
    Compute forward KL divergence (D_KL(teacher || student)) for sequence models.
    
    This is the standard knowledge distillation loss from Hinton et al. (2015).
    The student is trained to match the teacher's softened probability distribution.
    
    Formula: KL(P||Q) = sum(P(x) * log(P(x)/Q(x)))
    - P = teacher distribution (target)
    - Q = student distribution (model output)
    
    Args:
        student_logits: Student model logits [batch_size, seq_len, vocab_size]
        teacher_logits: Teacher model logits [batch_size, seq_len, vocab_size]
        temperature: Temperature for softening distributions (higher = softer)
        epsilon: Small constant for numerical stability
        pad_mask: Boolean mask for valid tokens [batch_size, seq_len]
                 1 for real tokens, 0 for padding
    
    Returns:
        Scalar loss value scaled by T² (preserves gradient magnitude)
    
    Example:
        >>> student_logits = torch.randn(8, 128, 50257)  # GPT-2 vocab
        >>> teacher_logits = torch.randn(8, 128, 50257)
        >>> mask = torch.ones(8, 128)
        >>> loss = sequence_kl_divergence(student_logits, teacher_logits, 
        ...                                temperature=2.0, pad_mask=mask)
    """
    # Apply temperature scaling BEFORE softmax
    student_logits = student_logits / temperature
    teacher_logits = teacher_logits / temperature

    # Stabilize logits by subtracting max value (prevents overflow)
    student_logits = student_logits - student_logits.max(dim=-1, keepdim=True).values
    teacher_logits = teacher_logits - teacher_logits.max(dim=-1, keepdim=True).values

    # Compute log probabilities for student
    student_log_probs = F.log_softmax(student_logits, dim=-1)

    # Compute probabilities for teacher with epsilon for stability
    teacher_probs = F.softmax(teacher_logits, dim=-1) + epsilon

    # KL divergence: sum over vocabulary dimension
    # F.kl_div expects log_probs as input and probs as target
    kl_loss = F.kl_div(
        student_log_probs, teacher_probs, reduction='none'
    ).sum(dim=-1)  # [batch_size, seq_len]

    # Apply padding mask if provided
    if pad_mask is not None:
        kl_loss = kl_loss * pad_mask  # Zero out padded positions
        valid_tokens = pad_mask.sum(dim=-1)  # Count valid tokens per sequence
    else:
        valid_tokens = student_logits.size(1)  # All tokens are valid

    # Average over valid tokens per sequence, then over batch
    sequence_loss = kl_loss.sum(dim=-1) / valid_tokens
    mean_loss = sequence_loss.mean()

    # Scale by T² (Hinton et al. convention - preserves gradient magnitude)
    scaled_loss = mean_loss * (temperature ** 2)
    
    return scaled_loss


def sequence_reverse_kl_divergence(
    student_logits: torch.Tensor,
    teacher_logits: torch.Tensor,
    temperature: float = 1.0,
    epsilon: float = 1e-9,
    pad_mask: Optional[torch.Tensor] = None
) -> torch.Tensor:
    """
    Compute reverse KL divergence (D_KL(student || teacher)) for sequence models.
    
    Unlike forward KL, reverse KL is "mode-seeking" rather than "mode-covering".
    It penalizes the student more heavily for putting probability mass where
    the teacher doesn't, making it focus on high-confidence teacher predictions.
    
    Formula: KL(Q||P) = sum(Q(x) * (log Q(x) - log P(x)))
    - Q = student distribution
    - P = teacher distribution
    
    Args:
        student_logits: Student model logits [batch_size, seq_len, vocab_size]
        teacher_logits: Teacher model logits [batch_size, seq_len, vocab_size]
        temperature: Temperature for softening distributions
        epsilon: Small constant for numerical stability
        pad_mask: Boolean mask for valid tokens [batch_size, seq_len]
    
    Returns:
        Scalar loss value scaled by T²
    
    Example:
        >>> loss = sequence_reverse_kl_divergence(
        ...     student_logits, teacher_logits, temperature=2.0
        ... )
    
    Note:
        Reverse KL tends to produce sharper, more confident distributions
        and may generalize better on out-of-distribution data.
    """
    # Apply temperature scaling
    student_logits = student_logits / temperature
    teacher_logits = teacher_logits / temperature

    # Stabilize logits
    student_logits = student_logits - student_logits.max(dim=-1, keepdim=True).values
    teacher_logits = teacher_logits - teacher_logits.max(dim=-1, keepdim=True).values

    # Compute log probabilities for both distributions
    student_log_probs = F.log_softmax(student_logits, dim=-1)
    teacher_log_probs = F.log_softmax(teacher_logits, dim=-1)

    # Compute student probabilities with epsilon
    student_probs = F.softmax(student_logits, dim=-1) + epsilon

    # Reverse KL: Q * (log Q - log P)
    # Computed manually since PyTorch's kl_div has opposite argument order
    kl_div = torch.sum(
        student_probs * (student_log_probs - teacher_log_probs), 
        dim=-1
    )  # [batch_size, seq_len]

    # Apply padding mask
    if pad_mask is not None:
        kl_div = kl_div * pad_mask
        valid_tokens = pad_mask.sum(dim=-1)
    else:
        valid_tokens = student_logits.size(1)

    # Average and scale
    sequence_loss = kl_div.sum(dim=-1) / valid_tokens
    mean_loss = sequence_loss.mean()
    scaled_loss = mean_loss * (temperature ** 2)
    
    return scaled_loss


def generalized_jsd_loss(
    student_logits: torch.Tensor,
    teacher_logits: torch.Tensor,
    labels: Optional[torch.Tensor] = None,
    beta: float = 0.5,
    temperature: float = 1.0,
    reduction: str = "batchmean"
) -> torch.Tensor:
    """
    Compute Generalized Jensen-Shannon Divergence for on-policy distillation (GKD).
    
    JSD is a symmetric divergence measure between two distributions.
    It's computed via a mixture distribution:
    
    Formula: JSD_beta(P||Q) = beta*KL(P||M) + (1-beta)*KL(Q||M)
    where M = beta*P + (1-beta)*Q (mixture of teacher and student)
    
    This loss is used in Generalized Knowledge Distillation (GKD) where
    the student generates sequences on-policy that are then used for training.
    
    Args:
        student_logits: Student model logits [batch_size, seq_len, vocab_size]
        teacher_logits: Teacher model logits [batch_size, seq_len, vocab_size]
        labels: Token IDs with -100 for ignored tokens [batch_size, seq_len]
        beta: Mixture weight (0.5 = symmetric JSD, like classic JSD)
        temperature: Temperature for softening distributions
        reduction: How to reduce the loss ('batchmean', 'sum', 'mean', 'none')
    
    Returns:
        JSD loss value (scalar if reduction != 'none')
    
    Example:
        >>> # For GKD with student-generated sequences
        >>> loss = generalized_jsd_loss(
        ...     student_logits, teacher_logits,
        ...     labels=labels,  # Mask out prompt tokens
        ...     beta=0.5,
        ...     temperature=1.0
        ... )
    
    Note:
        Unlike forward/reverse KL, JSD is symmetric and bounded.
        It provides a balanced distillation objective.
    """
    # Apply temperature scaling
    student_logits = student_logits / temperature
    teacher_logits = teacher_logits / temperature

    # Compute log probabilities
    student_log_probs = F.log_softmax(student_logits, dim=-1)
    teacher_log_probs = F.log_softmax(teacher_logits, dim=-1)

    # Compute mixture distribution log probabilities
    # log(a*exp(log_p) + b*exp(log_q)) = logsumexp([log(a)+log_p, log(b)+log_q])
    beta_tensor = torch.tensor(beta, dtype=student_log_probs.dtype, device=student_log_probs.device)
    mixture_log_probs = torch.logsumexp(
        torch.stack([
            student_log_probs + torch.log(beta_tensor),
            teacher_log_probs + torch.log(1 - beta_tensor)
        ]),
        dim=0,
    )

    # Compute KL divergences from mixture to teacher and student
    # Note: PyTorch's kl_div has reversed argument order vs mathematical definition
    kl_teacher = F.kl_div(
        mixture_log_probs, teacher_log_probs,
        reduction="none", log_target=True
    )
    kl_student = F.kl_div(
        mixture_log_probs, student_log_probs,
        reduction="none", log_target=True
    )

    # Compute weighted JSD
    jsd = beta_tensor * kl_teacher + (1 - beta_tensor) * kl_student

    # Apply label masking (ignore special tokens marked as -100)
    if labels is not None:
        mask = labels != -100
        jsd = jsd[mask]

    # Apply reduction
    if reduction == "batchmean":
        if labels is not None:
            return jsd.sum() / mask.sum()
        else:
            return jsd.sum() / (jsd.size(0) * jsd.size(1))
    elif reduction == "sum":
        return jsd.sum()
    elif reduction == "mean":
        return jsd.mean()
    else:
        return jsd
