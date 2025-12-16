"""
SparsityPredictor: Neural policy model for importance-based row selection.

This module implements a learnable sparsity prediction network that uses
reinforcement learning to identify important rows in MLP weight matrices
while preserving the spectral properties of the original weights.
"""

from torch import nn
from torch.distributions import Uniform
import torch
from typing import Tuple


class SparsityPredictor(torch.nn.Module):
    """
    A neural module that predicts sparsity patterns over MLP weight matrices
    using a learned distribution over rows. Implements differentiable
    sparsity via a reparameterization trick for RL-based optimization.
    
    The policy network learns to output keep probabilities for each row of
    an MLP weight matrix. During training, these probabilities are optimized
    using policy gradient methods with rewards based on spectral similarity.
    
    Architecture:
        - Linear projection: hidden_size -> intermediate_size
        - Learnable row sparsity parameters: (intermediate_size, 1)
        - Sigmoid activation with reparameterization trick
    
    Args:
        hidden_size: Dimensionality of the input hidden representation (default: 768)
        intermediate_size: Number of rows in the target MLP weight matrix (default: 3072)
    
    Attributes:
        proj_intermediate: Learnable linear projection for row-wise sparsity logits
        row_sparsities: Learnable parameter for initial sparsity scores per row
        alpha: Current sparsity distribution parameters (set during forward pass)
        keep_probs: Final keep probabilities after reparameterization
    
    Example:
        >>> predictor = SparsityPredictor(hidden_size=768, intermediate_size=3072)
        >>> weight_matrix = torch.randn(3072, 768)
        >>> keep_probs = predictor(weight_matrix)
        >>> # Sample rows to keep
        >>> num_keep = int(3072 * 0.7)  # Keep 70% of rows
        >>> row_indices = torch.multinomial(keep_probs, num_keep, replacement=False)
    """

    def __init__(self, hidden_size: int = 768, intermediate_size: int = 3072):
        super(SparsityPredictor, self).__init__()

        self.intermediate_size = intermediate_size
        self.proj_intermediate = nn.Linear(
            hidden_size, intermediate_size, bias=True
        )
        self.row_sparsities = nn.Parameter(
            torch.rand(intermediate_size, 1), requires_grad=True
        )  # (intermediate_size, 1)
        
        self.alpha = None
        self.keep_probs = None

    def calculate_KLD(self) -> torch.Tensor:
        """
        Compute KL divergence between the learned sparsity distribution (alpha)
        and a Bernoulli(0.5) prior to encourage sparsity regularization.
        
        This loss term prevents the policy from becoming too deterministic and
        encourages exploration during training.
        
        Returns:
            Scalar KL divergence loss
            
        Raises:
            RuntimeError: If forward() has not been called yet (alpha is None)
        """
        if self.alpha is None:
            raise RuntimeError("Must call forward() before calculating KLD")
            
        return (
            -1 * torch.log(self.alpha) * (1 - self.alpha)
            - self.alpha * torch.log(1 - self.alpha)
            + torch.log(torch.tensor(0.5)).to(self.alpha.device)
        ).sum()

    def calculate_total_loss(self) -> torch.Tensor:
        """
        Compute the total regularization loss for training.
        
        Currently only includes KL divergence, but can be extended to include
        additional regularization terms.
        
        Returns:
            Total loss (scalar)
        """
        return self.calculate_KLD()

    def forward(self, weight_matrix: torch.Tensor) -> torch.Tensor:
        """
        Forward pass to compute differentiable sparsity probabilities.
        
        Uses a reparameterization trick (Gumbel-Softmax style) to make the
        categorical sampling operation differentiable for policy gradient
        training.
        
        Args:
            weight_matrix: MLP weight matrix of shape (intermediate_size, hidden_size)
        
        Returns:
            Keep probabilities for each row (shape: [intermediate_size])
            
        Raises:
            ValueError: If weight matrix shape doesn't match intermediate_size
            
        Example:
            >>> predictor = SparsityPredictor(hidden_size=768, intermediate_size=3072)
            >>> weight = torch.randn(3072, 768)
            >>> probs = predictor(weight)
            >>> probs.shape
            torch.Size([3072])
        """
        if weight_matrix.shape[0] != self.intermediate_size:
            raise ValueError(
                f"Expected weight matrix with {self.intermediate_size} rows, "
                f"got {weight_matrix.shape[0]}"
            )

        # Compute row-wise importance scores
        proj_ = self.proj_intermediate(weight_matrix)  # (intermediate_size, intermediate_size)
        alpha = nn.Sigmoid()(proj_ @ self.row_sparsities)[:, 0]  # (intermediate_size,)
        
        self.alpha = alpha

        # Sample from Uniform(0, 1) for reparameterization
        m = Uniform(torch.tensor([0.0]), torch.tensor([1.0]))
        eps = m.sample((alpha.shape[0],)).to(weight_matrix.device)[:, 0]  # (intermediate_size,)

        # Reparameterization trick: make sampling differentiable
        keep_probs = nn.Sigmoid()(
            torch.log(eps)
            - torch.log(1 - eps)
            + torch.log(alpha)
            - torch.log(1 - alpha)
        )
        self.keep_probs = keep_probs

        return keep_probs
    
    def get_importance_scores(self, weight_matrix: torch.Tensor) -> torch.Tensor:
        """
        Get deterministic importance scores without reparameterization.
        
        Useful for visualization and analysis after training.
        
        Args:
            weight_matrix: MLP weight matrix
            
        Returns:
            Importance scores (alpha values) for each row
        """
        if weight_matrix.shape[0] != self.intermediate_size:
            raise ValueError(
                f"Expected weight matrix with {self.intermediate_size} rows, "
                f"got {weight_matrix.shape[0]}"
            )
        
        proj_ = self.proj_intermediate(weight_matrix)
        alpha = nn.Sigmoid()(proj_ @ self.row_sparsities)[:, 0]
        return alpha
