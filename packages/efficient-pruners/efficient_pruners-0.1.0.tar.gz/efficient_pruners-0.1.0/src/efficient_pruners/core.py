"""
PruneNet: Main class for RL-based model compression.

This module implements the main PruneNet interface with fit() and compress() methods.
"""

import copy
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import json

import torch
from torch.autograd import Variable
from transformers import AutoModel, AutoModelForCausalLM, PreTrainedModel
from tqdm import tqdm

from .config import PruningConfig
from .models.sparsity_predictor import SparsityPredictor
from .utils.model_utils import (
    set_seed,
    get_all_layers,
    get_layer_weight,
    create_sparsity_predictor,
    slice_layer_weights,
)
from .utils.reward_utils import calculate_reward, discount_rewards

logger = logging.getLogger(__name__)


class PruneNet:
    """
    PruneNet: Calibration-free model compression with policy learning.
    
    PruneNet learns a reinforcement learning policy to compress transformer models
    without requiring calibration data. The policy network (SparsityPredictor) learns
    to identify important neurons by preserving the spectral properties of weight matrices.
    
    Main workflow:
        1. Initialize with a PruningConfig (hyperparameters only)
        2. Call fit(model_name) to learn the compression policy via RL
        3. Call compress(compression_ratio) to generate a compressed model
    
    Attributes:
        config: PruningConfig instance with hyperparameters
        model: The transformer model to compress
        policy_model: SparsityPredictor instance (learned policy)
        reference_svds: Dict mapping layer index to reference singular values
        device: PyTorch device for computation
        
    Example:
        >>> from efficient_pruners import PruneNet, PruningConfig
        >>> 
        >>> config = PruningConfig(
        ...     num_episodes=20,
        ...     learning_rate=0.001
        ... )
        >>> 
        >>> pruner = PruneNet(config)
        >>> pruner.fit(model_name="facebook/opt-125m")
        >>> compressed_model = pruner.compress(compression_ratio=0.3)
        >>> compressed_model.save_pretrained("./compressed_model")
    """
    
    def __init__(self, config: PruningConfig):
        """
        Initialize PruneNet with configuration.
        
        Args:
            config: PruningConfig instance with all hyperparameters
        """
        self.config = config
        self.device = torch.device(config.device)
        
        # Model and policy will be loaded during fit/compress
        self.model: Optional[PreTrainedModel] = None
        self.policy_model: Optional[SparsityPredictor] = None
        self.reference_svds: Optional[Dict[int, torch.Tensor]] = None
        
        # Set random seed
        set_seed(config.seed)
        
        logger.info(f"Initialized PruneNet with config:\n{config}")
    
    def _load_model(self) -> PreTrainedModel:
        """Load the pretrained model from HuggingFace."""
        logger.info(f"Loading model: {self.config.model_name}")
        model = AutoModelForCausalLM.from_pretrained(self.config.model_name)
        model.to(self.device)
        model.eval()
        
        # Set sequence length if available
        if hasattr(model.config, 'max_position_embeddings'):
            model.seqlen = model.config.max_position_embeddings
        
        logger.info(f"Model loaded successfully on {self.device}")
        return model
    
    def _compute_reference_svds(self) -> Dict[int, torch.Tensor]:
        """
        Compute SVD for all layers in the uncompressed model.
        
        These serve as reference for reward calculation during training.
        
        Returns:
            Dictionary mapping layer index to singular values
        """
        logger.info("Computing reference SVDs for all layers...")
        svds = {}
        
        layers = get_all_layers(self.config.model_name, self.model)
        for i, layer in enumerate(tqdm(layers, desc="Computing SVDs")):
            weight = get_layer_weight(self.config.model_name, layer)
            
            # Convert to float32 if necessary for SVD
            if weight.dtype == torch.float16:
                weight = weight.to(torch.float32)
            
            _, singular_values, _ = torch.svd(weight)
            svds[i] = singular_values
        
        logger.info(f"Computed SVDs for {len(svds)} layers")
        return svds
    
    def _get_checkpoint_path(self, save_dir: str) -> Path:
        """Generate checkpoint path for policy model."""
        model_short_name = self.config.model_name.split('/')[-1]
        filename = f"policy_{model_short_name}_cr{self.config.compression_ratio}.pt"
        return Path(save_dir) / filename
    
    def fit(self, model_name: str, compression_ratio: float = 0.3, save_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Train the sparsity prediction policy using reinforcement learning.
        
        The policy is trained over multiple episodes, where each episode involves:
        1. Creating a fresh copy of the model
        2. For each layer:
           - Get importance scores from policy
           - Sample rows to keep
           - Compute reward (spectral similarity)
        3. Update policy using policy gradient with accumulated rewards
        
        Args:
            model_name: HuggingFace model checkpoint (e.g., "facebook/opt-125m")
            compression_ratio: Target compression ratio for training (default: 0.3)
            save_dir: Directory to save trained policy. If None, uses config.save_dir
        
        Returns:
            Training history with episode losses and rewards
            
        Example:
            >>> pruner = PruneNet(config)
            >>> history = pruner.fit(model_name="facebook/opt-125m", compression_ratio=0.3)
            >>> print(f"Best reward: {max(history['episode_rewards'])}")
        """
        # Validate compression_ratio
        if not 0 <= compression_ratio < 1:
            raise ValueError(
                f"compression_ratio must be in [0, 1), got {compression_ratio}"
            )
        
        # Store model_name and compression_ratio in config for internal use
        self.config.model_name = model_name
        self.config.compression_ratio = compression_ratio
        
        if save_dir is None:
            save_dir = self.config.save_dir
        
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        checkpoint_path = self._get_checkpoint_path(save_dir)
        
        # Load model if not already loaded
        if self.model is None:
            self.model = self._load_model()
        
        # Check if policy already exists
        if checkpoint_path.exists():
            logger.info(f"Policy checkpoint found at {checkpoint_path}")
            logger.info("Loading existing policy. Use compress() to apply it.")
            self.load_policy(str(checkpoint_path))
            return {"status": "loaded_existing"}
        
        # Initialize policy model
        self.policy_model = create_sparsity_predictor(
            self.config.model_name,
            self.model.config
        )
        self.policy_model.to(self.device)
        self.policy_model.train()
        
        # Compute reference SVDs
        self.reference_svds = self._compute_reference_svds()
        
        # Setup optimizer
        optimizer = torch.optim.AdamW(
            self.policy_model.parameters(),
            lr=self.config.learning_rate
        )
        scaler = torch.amp.GradScaler("cuda" if torch.cuda.is_available() else "cpu")
        
        # Training history
        history = {
            'episode_losses': [],
            'episode_rewards': [],
        }
        
        best_reward = float('-inf')
        
        logger.info(f"Starting policy training for {self.config.num_episodes} episodes")
        
        # Training loop
        for episode in tqdm(range(self.config.num_episodes), desc="Training Episodes"):
            # Create fresh model copy for this episode
            episode_model = copy.deepcopy(self.model)
            episode_model.to(self.device)
            
            # Storage for episode trajectory
            states = []
            actions = []
            rewards = []
            
            # Process each layer
            layers = get_all_layers(self.config.model_name, episode_model)
            for layer_idx, layer in enumerate(layers):
                weight = get_layer_weight(self.config.model_name, layer)
                state = Variable(copy.deepcopy(weight))
                
                # Get importance scores and sample rows
                with torch.autocast(
                    device_type=self.device.type,
                    dtype=torch.float16
                ):
                    keep_probs = self.policy_model(state)
                    feat_len = state.shape[0]
                    num_keep = int((1 - self.config.compression_ratio) * feat_len)
                    
                    row_indices = torch.multinomial(
                        keep_probs,
                        num_keep,
                        replacement=False
                    ).sort().values
                
                # Apply slicing
                slice_layer_weights(self.config.model_name, layer, row_indices)
                
                # Calculate reward
                new_weight = get_layer_weight(self.config.model_name, layer)
                reward = calculate_reward(
                    self.reference_svds[layer_idx],
                    new_weight
                )
                
                # Store trajectory
                states.append(state)
                actions.append(row_indices)
                rewards.append(reward)
            
            # Compute discounted rewards
            discounted_rewards = discount_rewards(rewards, self.config.gamma)
            
            # Policy gradient update
            total_loss = 0.0
            for i in range(len(states)):
                with torch.autocast(
                    device_type=self.device.type,
                    dtype=torch.float16
                ):
                    state = states[i]
                    action = Variable(actions[i])
                    reward = discounted_rewards[i]
                    
                    # Recompute probabilities
                    keep_probs = self.policy_model(state)
                    
                    # Policy gradient loss: -log P(a|s) * R
                    log_probs = torch.log(keep_probs)
                    action_log_probs = torch.gather(log_probs, 0, action)
                    loss = -action_log_probs.sum() * reward
                    
                    # Add KL divergence regularization if enabled
                    if self.config.use_kld:
                        kld_loss = self.policy_model.calculate_total_loss()
                        loss = loss + kld_loss
                    
                    total_loss += loss.item()
                
                # Backward pass
                scaler.scale(loss).backward()
            
            # Optimizer step
            torch.nn.utils.clip_grad_norm_(self.policy_model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad()
            
            # Track metrics
            avg_loss = total_loss / len(states)
            avg_reward = sum(rewards) / len(rewards)
            total_reward = sum(rewards)
            
            history['episode_losses'].append(avg_loss)
            history['episode_rewards'].append(total_reward)
            
            logger.info(
                f"Episode {episode + 1}/{self.config.num_episodes} | "
                f"Loss: {avg_loss:.4f} | "
                f"Avg Reward: {avg_reward:.4f} | "
                f"Total Reward: {total_reward:.4f}"
            )
            
            # Save best model
            if total_reward > best_reward:
                best_reward = total_reward
                logger.info(f"New best reward! Saving policy to {checkpoint_path}")
                self.save_policy(str(checkpoint_path))
        
        logger.info(f"Training complete. Best reward: {best_reward:.4f}")
        
        # Load best policy
        self.load_policy(str(checkpoint_path))
        
        return history
    
    def compress(
        self,
        compression_ratio: float
    ) -> PreTrainedModel:
        """
        Apply the learned policy to compress the model.
        
        This method uses the trained policy to select important rows in each
        layer and produces a compressed model that can be used for inference.
        
        Args:
            compression_ratio: Fraction of neurons to remove, in range [0, 1)
        
        Returns:
            Compressed transformer model (PreTrainedModel)
            
        Raises:
            RuntimeError: If policy has not been trained or loaded
            ValueError: If compression_ratio is not in valid range
            
        Example:
            >>> pruner = PruneNet(config)
            >>> pruner.fit(model_name="facebook/opt-125m")
            >>> compressed_model = pruner.compress(compression_ratio=0.3)
        """
        if self.policy_model is None:
            raise RuntimeError(
                "Policy model not found. Call fit() first or load a pretrained policy."
            )
        
        if not 0 <= compression_ratio < 1:
            raise ValueError(
                f"compression_ratio must be in [0, 1), got {compression_ratio}"
            )
        
        # Store compression_ratio in config for internal use
        self.config.compression_ratio = compression_ratio
        
        # Load model if needed
        if self.model is None:
            self.model = self._load_model()
        
        # Create a copy to compress
        logger.info(f"Compressing model with ratio {compression_ratio}")
        compressed_model = copy.deepcopy(self.model)
        compressed_model.to(self.device)
        
        self.policy_model.eval()
        
        # Compress each layer
        layers = get_all_layers(self.config.model_name, compressed_model)
        with torch.no_grad():
            for layer_idx, layer in enumerate(tqdm(layers, desc="Compressing layers")):
                weight = get_layer_weight(self.config.model_name, layer)
                state = Variable(copy.deepcopy(weight))
                
                with torch.autocast(
                    device_type=self.device.type,
                    dtype=torch.float16
                ):
                    keep_probs = self.policy_model(state)
                    feat_len = state.shape[0]
                    num_keep = int((1 - compression_ratio) * feat_len)
                    
                    row_indices = torch.multinomial(
                        keep_probs,
                        num_keep,
                        replacement=False
                    ).sort().values
                
                slice_layer_weights(self.config.model_name, layer, row_indices)
        
        logger.info("Compression complete")
        return compressed_model
    
    def save_policy(self, path: str):
        """
        Save the trained policy model.
        
        Args:
            path: Path to save policy checkpoint
        """
        if self.policy_model is None:
            raise RuntimeError("No policy model to save")
        
        torch.save({
            'policy_state_dict': self.policy_model.state_dict(),
            'config': self.config.to_dict(),
        }, path)
        logger.info(f"Policy saved to {path}")
    
    def load_policy(self, path: str):
        """
        Load a trained policy model.
        
        Args:
            path: Path to policy checkpoint
        """
        logger.info(f"Loading policy from {path}")
        checkpoint = torch.load(path, map_location=self.device, weights_only=False)
        
        # Initialize policy if not exists
        if self.policy_model is None:
            if self.model is None:
                self.model = self._load_model()
            self.policy_model = create_sparsity_predictor(
                self.config.model_name,
                self.model.config
            )
            self.policy_model.to(self.device)
        
        self.policy_model.load_state_dict(checkpoint['policy_state_dict'])
        self.policy_model.eval()
        logger.info("Policy loaded successfully")
    
    @classmethod
    def from_pretrained(
        cls,
        model_name: str,
        policy_path: str,
        compression_ratio: float = 0.3,
        device: str = "auto"
    ) -> 'PruneNet':
        """
        Create PruneNet instance with a pretrained policy.
        
        Convenient method to load a policy and apply it to a model without
        training.
        
        Args:
            model_name: HuggingFace model name
            policy_path: Path to saved policy checkpoint
            compression_ratio: Compression ratio to use
            device: Device to use for computation
        
        Returns:
            PruneNet instance with loaded policy
            
        Example:
            >>> pruner = PruneNet.from_pretrained(
            ...     model_name="facebook/opt-125m",
            ...     policy_path="./checkpoints/policy_opt-125m_cr0.3.pt",
            ...     compression_ratio=0.3
            ... )
            >>> compressed = pruner.compress()
        """
        config = PruningConfig(
            model_name=model_name,
            compression_ratio=compression_ratio,
            device=device
        )
        
        pruner = cls(config)
        pruner.load_policy(policy_path)
        
        return pruner
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """
        Get statistics about model compression.
        
        Returns:
            Dictionary with parameter counts and compression ratio
        """
        if self.model is None:
            self.model = self._load_model()
        
        original_params = sum(p.numel() for p in self.model.parameters())
        
        # Estimate compressed params
        layers = get_all_layers(self.config.model_name, self.model)
        mlp_params = 0
        for layer in layers:
            weight = get_layer_weight(self.config.model_name, layer)
            mlp_params += weight.numel()
        
        # After compression
        compressed_mlp_params = mlp_params * (1 - self.config.compression_ratio)
        compressed_total = original_params - mlp_params + compressed_mlp_params
        
        return {
            'original_params': original_params,
            'compressed_params': int(compressed_total),
            'reduction_ratio': (original_params - compressed_total) / original_params,
            'params_saved': original_params - int(compressed_total),
        }
