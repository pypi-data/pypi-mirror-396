"""
Efficient Pruners: Calibration-Free Model Compression with Policy Learning

PruneNet implements reinforcement learning-based compression for large language models
without requiring calibration data. The policy network learns to identify important
neurons by preserving the spectral properties of weight matrices.

Main API:
    from efficient_pruners import PruneNet, PruningConfig
    
    # Configure pruning
    config = PruningConfig(
        model_name="facebook/opt-125m",
        compression_ratio=0.3,
        num_episodes=20
    )
    
    # Train policy and compress
    pruner = PruneNet(config)
    pruner.fit()  # Learn compression policy
    compressed_model = pruner.compress()  # Apply compression
    
    # Save compressed model
    compressed_model.save_pretrained("./compressed_model")

Classes:
    PruneNet: Main interface for policy learning and model compression
    PruningConfig: Configuration dataclass for pruning parameters
    SparsityPredictor: Neural policy model for importance prediction

Example:
    >>> from efficient_pruners import PruneNet, PruningConfig
    >>> config = PruningConfig(model_name="facebook/opt-125m", compression_ratio=0.3)
    >>> pruner = PruneNet(config)
    >>> pruner.fit(save_dir="./checkpoints")
    >>> compressed_model = pruner.compress()
"""

from .core import PruneNet
from .config import PruningConfig
from .models.sparsity_predictor import SparsityPredictor
from .__version__ import __version__

__all__ = [
    'PruneNet',
    'PruningConfig',
    'SparsityPredictor',
    '__version__'
]

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info(f"Efficient Pruners v{__version__} initialized")
