"""
Model utility functions for layer extraction and weight manipulation.

This module provides utilities for working with different transformer architectures
(OPT, Llama, Phi, Falcon) in a unified way.
"""

import random
import torch
from typing import List, Union
from transformers import PreTrainedModel

from ..models.sparsity_predictor import SparsityPredictor


def set_seed(seed: int):
    """
    Set random seed for reproducibility across PyTorch and Python's random module.
    
    This ensures deterministic behavior during multinomial sampling in the
    training and compression loops.
    
    Args:
        seed: Seed value to use
        
    Example:
        >>> set_seed(42)
        >>> # All subsequent random operations will be deterministic
    """
    torch.manual_seed(seed)
    random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_all_layers(model_name: str, model: PreTrainedModel) -> List:
    """
    Retrieve the list of transformer layers for supported model architectures.
    
    Supports: OPT, Phi, Llama, Falcon
    
    Args:
        model_name: Name of the model (e.g., "facebook/opt-125m")
        model: The loaded model instance
    
    Returns:
        List of transformer layers
        
    Raises:
        ValueError: If the model type is not supported
        
    Example:
        >>> from transformers import AutoModel
        >>> model = AutoModel.from_pretrained("facebook/opt-125m")
        >>> layers = get_all_layers("facebook/opt-125m", model)
        >>> len(layers)
        12
    """
    model_name_lower = model_name.lower()
    
    # Handle ForCausalLM models that wrap the base model
    base_model = model.model if hasattr(model, 'model') else model
    
    if "opt" in model_name_lower:
        return base_model.decoder.layers
    elif "phi" in model_name_lower:
        return base_model.layers
    elif "llama" in model_name_lower:
        return base_model.layers
    elif "falcon" in model_name_lower:
        return base_model.transformer.h
    else:
        raise ValueError(
            f"Model type not supported: {model_name}. "
            "Only OPT, Phi, Llama, and Falcon models are supported."
        )


def get_layer_weight(model_name: str, layer: torch.nn.Module) -> torch.Tensor:
    """
    Extract the first MLP weight matrix from a transformer layer.
    
    Different architectures store MLP weights in different locations:
    - OPT: fc1.weight
    - Phi: mlp.fc1.weight
    - Llama: mlp.gate_proj.weight
    - Falcon: mlp.dense_h_to_4h.weight
    
    Args:
        model_name: Name of the model architecture
        layer: The transformer layer object
    
    Returns:
        Weight matrix of the first MLP projection (intermediate_size, hidden_size)
        
    Raises:
        ValueError: If the model type is not supported
        
    Example:
        >>> weight = get_layer_weight("facebook/opt-125m", layers[0])
        >>> weight.shape
        torch.Size([3072, 768])
    """
    model_name_lower = model_name.lower()
    
    if "opt" in model_name_lower:
        return layer.fc1.weight.data
    elif "phi" in model_name_lower:
        return layer.mlp.fc1.weight.data
    elif "llama" in model_name_lower:
        return layer.mlp.gate_proj.weight.data
    elif "falcon" in model_name_lower:
        return layer.mlp.dense_h_to_4h.weight.data
    else:
        raise ValueError(
            f"Model type not supported: {model_name}. "
            "Only OPT, Phi, Llama, and Falcon models are supported."
        )


def create_sparsity_predictor(
    model_name: str, 
    model_config
) -> SparsityPredictor:
    """
    Create a SparsityPredictor tailored to the model's architecture.
    
    Automatically determines the correct hidden_size and intermediate_size
    from the model configuration.
    
    Args:
        model_name: Name of the model architecture
        model_config: Model configuration object from transformers
    
    Returns:
        SparsityPredictor instance with appropriate dimensions
        
    Raises:
        ValueError: If the model type is not supported
        
    Example:
        >>> from transformers import AutoConfig
        >>> config = AutoConfig.from_pretrained("facebook/opt-125m")
        >>> predictor = create_sparsity_predictor("facebook/opt-125m", config)
        >>> predictor.intermediate_size
        3072
    """
    model_name_lower = model_name.lower()
    
    if "opt" in model_name_lower:
        return SparsityPredictor(
            model_config.hidden_size, 
            model_config.ffn_dim
        )
    elif "llama" in model_name_lower or "phi" in model_name_lower:
        return SparsityPredictor(
            model_config.hidden_size,
            model_config.intermediate_size,
        )
    elif "falcon" in model_name_lower:
        return SparsityPredictor(
            model_config.hidden_size,
            model_config.ffn_hidden_size,
        )
    else:
        raise ValueError(
            f"Model type not supported: {model_name}. "
            "Only OPT, Phi, Llama, and Falcon models are supported."
        )


def slice_layer_weights(
    model_name: str, 
    layer: torch.nn.Module, 
    row_indices: torch.Tensor
):
    """
    Apply row slicing to MLP weights in a transformer layer.
    
    This modifies the layer in-place, updating:
    - Weight matrices of intermediate projections (keeping only selected rows)
    - Bias vectors (if present)
    - Output projection weights (to match new intermediate dimension)
    
    The function handles architecture-specific differences in layer structure.
    
    Args:
        model_name: Name of the model architecture
        layer: The transformer layer to modify
        row_indices: Indices of rows to keep (1D tensor)
        
    Raises:
        ValueError: If the model type is not supported
        
    Example:
        >>> # Keep 70% of neurons (randomly selected by policy)
        >>> keep_probs = predictor(weight_matrix)
        >>> num_keep = int(3072 * 0.7)
        >>> row_indices = torch.multinomial(keep_probs, num_keep, replacement=False)
        >>> slice_layer_weights("facebook/opt-125m", layer, row_indices)
        >>> # Layer now has 70% of original neurons
    """
    model_name_lower = model_name.lower()
    num_keep = len(row_indices)
    
    if "opt" in model_name_lower:
        # Update intermediate projection
        layer.fc1.out_features = num_keep
        layer.fc1.weight.data = layer.fc1.weight[row_indices, :]
        layer.fc1.bias.data = layer.fc1.bias[row_indices]
        
        # Update output projection
        layer.fc2.in_features = num_keep
        layer.fc2.weight.data = layer.fc2.weight[:, row_indices]

    elif "phi" in model_name_lower:
        # Update intermediate projection
        layer.mlp.fc1.out_features = num_keep
        layer.mlp.fc1.weight.data = layer.mlp.fc1.weight[row_indices, :]
        layer.mlp.fc1.bias.data = layer.mlp.fc1.bias[row_indices]
        
        # Update output projection
        layer.mlp.fc2.in_features = num_keep
        layer.mlp.fc2.weight.data = layer.mlp.fc2.weight[:, row_indices]

    elif "llama" in model_name_lower:
        # Llama has gate_proj and up_proj that both need slicing
        layer.mlp.gate_proj.out_features = num_keep
        layer.mlp.gate_proj.weight.data = layer.mlp.gate_proj.weight[row_indices, :]
        
        layer.mlp.up_proj.out_features = num_keep
        layer.mlp.up_proj.weight.data = layer.mlp.up_proj.weight[row_indices, :]
        
        # Update output projection
        layer.mlp.down_proj.in_features = num_keep
        layer.mlp.down_proj.weight.data = layer.mlp.down_proj.weight[:, row_indices]

    elif "falcon" in model_name_lower:
        # Update intermediate projection
        layer.mlp.dense_h_to_4h.out_features = num_keep
        layer.mlp.dense_h_to_4h.weight.data = layer.mlp.dense_h_to_4h.weight[row_indices, :]
        
        # Update output projection
        layer.mlp.dense_4h_to_h.in_features = num_keep
        layer.mlp.dense_4h_to_h.weight.data = layer.mlp.dense_4h_to_h.weight[:, row_indices]
    
    else:
        raise ValueError(
            f"Model type not supported: {model_name}. "
            "Only OPT, Phi, Llama, and Falcon models are supported."
        )
