"""
Reward calculation utilities for policy training.

This module implements reward functions based on spectral similarity
using the Kolmogorov-Smirnov (KS) test and temporal discounting.
"""

import numpy as np
import torch
from scipy import stats
from typing import List


def calculate_reward(
    reference_sv: torch.Tensor,
    compressed_weight: torch.Tensor
) -> float:
    """
    Compute reward based on spectral similarity using KS statistic.
    
    The reward encourages the policy to preserve the singular value
    distribution of the original weight matrix. Higher rewards indicate
    better preservation of spectral properties.
    
    Algorithm:
        1. Compute SVD of compressed weight matrix
        2. Compare singular values using 2-sample KS test
        3. Return inverse of KS statistic (lower distance = higher reward)
    
    Args:
        reference_sv: Singular values of the original uncompressed weight (1D tensor)
        compressed_weight: Weight matrix after compression (2D tensor)
    
    Returns:
        Reward value (scalar). Higher is better. Returns 99999 if distributions
        are identical (KS statistic = 0).
        
    Example:
        >>> # Get reference SVD
        >>> _, s_ref, _ = torch.svd(original_weight)
        >>> # Compress and calculate reward
        >>> compressed = original_weight[row_indices, :]
        >>> reward = calculate_reward(s_ref, compressed)
        >>> print(f"Reward: {reward:.4f}")
    """
    # Convert to float32 if necessary
    if compressed_weight.dtype == torch.float16:
        compressed_weight = compressed_weight.to(torch.float32)
    
    # Compute SVD of compressed weight
    _, s_compressed, _ = torch.svd(compressed_weight)
    
    # Calculate KS statistic between the two distributions
    ks_statistic = stats.ks_2samp(
        reference_sv.detach().cpu().numpy(),
        s_compressed.detach().cpu().numpy()
    ).statistic
    
    # Return inverse (lower KS distance = higher reward)
    if ks_statistic == 0:
        return 99999.0  # Perfect match
    else:
        return 1.0 / ks_statistic


def discount_rewards(
    rewards: List[float],
    gamma: float = 0.99
) -> np.ndarray:
    """
    Apply temporal discounting to a sequence of rewards.
    
    Implements exponential discounting: r_i' = gamma^i * r_i
    
    This gives higher weight to earlier layers and encourages the policy
    to prioritize preserving early layer representations.
    
    Args:
        rewards: List of reward values from each layer
        gamma: Discount factor in range (0, 1). Higher values give more weight
               to later rewards. Default: 0.99
    
    Returns:
        Array of discounted rewards (same length as input)
        
    Example:
        >>> rewards = [10.0, 8.0, 6.0, 4.0]
        >>> discounted = discount_rewards(rewards, gamma=0.95)
        >>> print(discounted)
        [10.0  7.6  5.415  3.647]
    """
    if not 0 < gamma <= 1:
        raise ValueError(f"gamma must be in (0, 1], got {gamma}")
    
    discounted = np.array([
        gamma**i * rewards[i] 
        for i in range(len(rewards))
    ])
    
    return discounted


def normalize_rewards(rewards: List[float]) -> np.ndarray:
    """
    Normalize rewards to zero mean and unit variance.
    
    This stabilizes policy gradient training by reducing variance
    in the gradient estimates.
    
    Args:
        rewards: List of reward values
    
    Returns:
        Normalized rewards (zero mean, unit std)
        
    Example:
        >>> rewards = [10.0, 20.0, 15.0, 25.0]
        >>> normalized = normalize_rewards(rewards)
        >>> print(f"Mean: {normalized.mean():.2f}, Std: {normalized.std():.2f}")
        Mean: 0.00, Std: 1.00
    """
    rewards_array = np.array(rewards)
    mean = rewards_array.mean()
    std = rewards_array.std()
    
    if std < 1e-8:
        # All rewards are the same
        return np.zeros_like(rewards_array)
    
    return (rewards_array - mean) / std
