"""Configuration classes for PruneNet."""

from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any
import json
import torch


@dataclass
class PruningConfig:
    """
    Configuration for PruneNet compression.
    
    This dataclass encapsulates hyperparameters for training the sparsity
    prediction policy. Model name is specified in fit() and compression ratio
    is specified in compress().
    
    Attributes:
        num_episodes (int): Number of RL training episodes
        learning_rate (float): Learning rate for policy optimizer
        use_kld (bool): Whether to use KL divergence regularization
        gamma (float): Reward discount factor for temporal credit assignment
        seed (int): Random seed for reproducibility
        device (str): PyTorch device ("auto", "cpu", "cuda", "cuda:0", etc.)
        save_dir (str): Directory to save checkpoints and compressed models
        
    Example:
        >>> config = PruningConfig(
        ...     num_episodes=20,
        ...     learning_rate=0.001
        ... )
        >>> pruner = PruneNet(config)
        >>> pruner.fit(model_name="facebook/opt-125m")
        >>> compressed = pruner.compress(compression_ratio=0.3)
    """
    
    # Policy training hyperparameters
    num_episodes: int = 20
    learning_rate: float = 0.001
    use_kld: bool = False
    gamma: float = 0.99
    
    # System configuration
    seed: int = 42
    device: str = "auto"
    
    # I/O configuration
    save_dir: str = "./prunenet_outputs"
    
    # Internal state (set during fit/compress - not for user initialization)
    model_name: Optional[str] = field(default=None, init=False, repr=False)
    compression_ratio: Optional[float] = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.num_episodes < 1:
            raise ValueError(
                f"num_episodes must be positive, got {self.num_episodes}"
            )
        
        if self.learning_rate <= 0:
            raise ValueError(
                f"learning_rate must be positive, got {self.learning_rate}"
            )
        
        # Handle device auto-detection
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        return asdict(self)
    
    def save(self, path: str):
        """
        Save configuration to JSON file.
        
        Args:
            path: Path to save configuration file
        """
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'PruningConfig':
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Dictionary with configuration parameters
            
        Returns:
            PruningConfig instance
        """
        return cls(**config_dict)
    
    @classmethod
    def from_json(cls, path: str) -> 'PruningConfig':
        """
        Load configuration from JSON file.
        
        Args:
            path: Path to configuration file
            
        Returns:
            PruningConfig instance
        """
        with open(path, 'r') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"PruningConfig(\n"
            f"  num_episodes={self.num_episodes},\n"
            f"  learning_rate={self.learning_rate},\n"
            f"  use_kld={self.use_kld},\n"
            f"  gamma={self.gamma},\n"
            f"  seed={self.seed},\n"
            f"  device='{self.device}',\n"
            f"  save_dir='{self.save_dir}'\n"
            f")"
        )
