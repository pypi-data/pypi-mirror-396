# PruneNet API Guide

Complete API reference for the Efficient Pruners package.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Classes](#core-classes)
4. [Configuration](#configuration)
5. [Utilities](#utilities)
6. [Examples](#examples)

---

## Installation

### From Source

```bash
git clone https://github.com/parmanu-lcs2/efficient_pruners
cd efficient_pruners
pip install -e .
```

### With Optional Dependencies

```bash
# For evaluation
pip install -e ".[eval]"

# For finetuning
pip install -e ".[finetune]"

# For logging (wandb/tensorboard)
pip install -e ".[logging]"

# Install all extras
pip install -e ".[all]"
```

---

## Quick Start

```python
from efficient_pruners import PruneNet, PruningConfig

# Configure hyperparameters only
config = PruningConfig(
    num_episodes=20,
    learning_rate=0.001
)

# Initialize pruner
pruner = PruneNet(config)

# Train policy on specific model with target compression ratio
pruner.fit(model_name="facebook/opt-125m", compression_ratio=0.3)

# Compress with learned policy
compressed_model = pruner.compress(compression_ratio=0.3)

# Save compressed model
compressed_model.save_pretrained("./compressed_model")
```

---

## Core Classes

### PruneNet

Main class for reinforcement learning-based model compression.

#### Constructor

```python
PruneNet(config: PruningConfig)
```

**Parameters:**
- `config` (PruningConfig): Configuration object with all hyperparameters

**Attributes:**
- `config`: The configuration object
- `model`: The transformer model being compressed
- `policy_model`: The trained SparsityPredictor
- `device`: PyTorch device for computation

#### Methods

##### `fit(model_name: str, compression_ratio: float = 0.3, save_dir: Optional[str] = None) -> Dict[str, Any]`

Train the compression policy using reinforcement learning.

**Parameters:**
- `model_name` (str): HuggingFace model name (e.g., "facebook/opt-125m")
- `compression_ratio` (float, optional): Target compression ratio for training (default: 0.3)
- `save_dir` (str, optional): Directory to save trained policy. Uses `config.save_dir` if None.

**Returns:**
- Dictionary with training history containing:
  - `episode_losses`: List of losses per episode
  - `episode_rewards`: List of total rewards per episode

**Example:**
```python
pruner = PruneNet(config)
history = pruner.fit(
    model_name="facebook/opt-125m",
    compression_ratio=0.3,
    save_dir="./checkpoints"
)

print(f"Best reward: {max(history['episode_rewards'])}")
```

##### `compress(compression_ratio: float) -> PreTrainedModel`

Apply the learned policy to compress the model.

**Parameters:**
- `compression_ratio` (float): Compression ratio to apply (must match or differ from training ratio)

**Returns:**
- Compressed transformer model (PreTrainedModel)

**Raises:**
- `RuntimeError`: If policy hasn't been trained or loaded

**Example:**
```python
# Use same ratio as training
compressed = pruner.compress(compression_ratio=0.3)

# Or try different ratio
compressed = pruner.compress(compression_ratio=0.5)
```

##### `save_policy(path: str)`

Save the trained policy model.

**Parameters:**
- `path` (str): Path to save policy checkpoint

**Example:**
```python
pruner.save_policy("./my_policy.pt")
```

##### `load_policy(path: str)`

Load a trained policy model.

**Parameters:**
- `path` (str): Path to policy checkpoint

**Example:**
```python
pruner.load_policy("./my_policy.pt")
```

##### `get_compression_stats() -> Dict[str, Any]`

Get statistics about model compression.

**Returns:**
- Dictionary with:
  - `original_params`: Original parameter count
  - `compressed_params`: Compressed parameter count
  - `reduction_ratio`: Fraction of parameters removed
  - `params_saved`: Number of parameters saved

**Example:**
```python
stats = pruner.get_compression_stats()
print(f"Reduced by {stats['reduction_ratio']*100:.2f}%")
```

##### `from_pretrained(model_name: str, policy_path: str, compression_ratio: float = 0.3, device: str = "auto") -> PruneNet` (classmethod)

Create PruneNet instance with a pretrained policy.

**Parameters:**
- `model_name` (str): HuggingFace model name
- `policy_path` (str): Path to saved policy checkpoint
- `compression_ratio` (float): Compression ratio to use
- `device` (str): Device for computation

**Returns:**
- PruneNet instance with loaded policy

**Example:**
```python
pruner = PruneNet.from_pretrained(
    model_name="facebook/opt-125m",
    policy_path="./checkpoints/policy.pt",
    compression_ratio=0.3
)
compressed = pruner.compress()
```

---

## Configuration

### PruningConfig

Dataclass for compression configuration.

#### Constructor

```python
PruningConfig(
    num_episodes: int = 20,
    learning_rate: float = 0.001,
    use_kld: bool = False,
    gamma: float = 0.99,
    seed: int = 42,
    device: str = "auto",
    save_dir: str = "./prunenet_outputs"
)
```

**Parameters:**

- `num_episodes` (int): Number of RL training episodes (default: 20)
- `learning_rate` (float): Learning rate for policy optimizer (default: 0.001)
- `use_kld` (bool): Whether to use KL divergence regularization (default: False)
- `gamma` (float): Reward discount factor (default: 0.99)
- `seed` (int): Random seed for reproducibility (default: 42)
- `device` (str): PyTorch device ("auto", "cpu", "cuda", etc.) (default: "auto")
- `save_dir` (str): Directory for checkpoints (default: "./prunenet_outputs")

**Note:** `model_name` and `compression_ratio` are specified in the `fit()` and `compress()` methods, not in the config.

**Validation:**
- Raises `ValueError` if `num_episodes` < 1
- Raises `ValueError` if `learning_rate` <= 0

#### Methods

##### `to_dict() -> Dict[str, Any]`

Convert configuration to dictionary.

##### `save(path: str)`

Save configuration to JSON file.

##### `from_dict(config_dict: Dict[str, Any]) -> PruningConfig` (classmethod)

Create configuration from dictionary.

##### `from_json(path: str) -> PruningConfig` (classmethod)

Load configuration from JSON file.

**Example:**
```python
# Create config
config = PruningConfig(
    model_name="facebook/opt-125m",
    compression_ratio=0.3
)

# Save to file
config.save("config.json")

# Load from file
loaded_config = PruningConfig.from_json("config.json")
```

---

## Utilities

### Model Utilities

Located in `efficient_pruners.utils.model_utils`

#### `set_seed(seed: int)`

Set random seed for reproducibility.

#### `get_all_layers(model_name: str, model: PreTrainedModel) -> List`

Get all transformer layers from a model.

**Supported models:** OPT, Phi, Llama, Falcon

#### `get_layer_weight(model_name: str, layer: nn.Module) -> torch.Tensor`

Extract MLP weight matrix from a layer.

#### `create_sparsity_predictor(model_name: str, model_config) -> SparsityPredictor`

Create a SparsityPredictor for a specific model architecture.

#### `slice_layer_weights(model_name: str, layer: nn.Module, row_indices: torch.Tensor)`

Apply row slicing to layer weights in-place.

### Reward Utilities

Located in `efficient_pruners.utils.reward_utils`

#### `calculate_reward(reference_sv: torch.Tensor, compressed_weight: torch.Tensor) -> float`

Compute reward based on spectral similarity using Kolmogorov-Smirnov test.

#### `discount_rewards(rewards: List[float], gamma: float = 0.99) -> np.ndarray`

Apply temporal discounting to rewards.

#### `normalize_rewards(rewards: List[float]) -> np.ndarray`

Normalize rewards to zero mean and unit variance.

---

## Examples

### Basic Usage

```python
from efficient_pruners import PruneNet, PruningConfig

config = PruningConfig(
    num_episodes=20,
    learning_rate=0.001
)

pruner = PruneNet(config)
pruner.fit(model_name="facebook/opt-125m", compression_ratio=0.3)
compressed = pruner.compress(compression_ratio=0.3)
compressed.save_pretrained("./compressed")
```

### Different Compression Ratios

```python
config = PruningConfig(
    num_episodes=20,
    save_dir="./outputs"
)

for ratio in [0.2, 0.3, 0.5]:
    pruner = PruneNet(config)
    pruner.fit(
        model_name="facebook/opt-125m",
        compression_ratio=ratio,
        save_dir=f"./outputs/ratio_{ratio}"
    )
    compressed = pruner.compress(compression_ratio=ratio)
    compressed.save_pretrained(f"./compressed_ratio_{ratio}")
```

### With KL Divergence Regularization

```python
config = PruningConfig(
    num_episodes=20,
    use_kld=True  # Enable KL divergence
)

pruner = PruneNet(config)
pruner.fit(model_name="facebook/opt-125m", compression_ratio=0.3)
compressed = pruner.compress(compression_ratio=0.3)
```

### Loading Pretrained Policy

```python
# Train once
pruner = PruneNet(config)
pruner.fit()

# Load and reuse
pruner2 = PruneNet.from_pretrained(
    model_name="facebook/opt-125m",
    policy_path="./checkpoints/policy.pt",
    compression_ratio=0.3
)
compressed = pruner2.compress()
```

### Text Generation with Compressed Model

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

# Compress model
model_name = "facebook/opt-125m"
pruner = PruneNet(config)
pruner.fit(model_name=model_name, compression_ratio=0.3)
compressed = pruner.compress(compression_ratio=0.3)
compressed.save_pretrained("./compressed")

# Load for generation
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained("./compressed")

# Generate text
inputs = tokenizer("The future of AI is", return_tensors="pt")
outputs = model.generate(**inputs, max_length=50)
print(tokenizer.decode(outputs[0]))
```

---

## Supported Models

PruneNet supports the following model architectures:

- **OPT** (facebook/opt-*)
- **Llama** (meta-llama/*)
- **Phi** (microsoft/phi-*)
- **Falcon** (tiiuae/falcon-*)

---

## Best Practices

### Compression Ratios

- **Light (20-30%)**: Minimal quality loss, good for production
- **Medium (30-40%)**: Balanced compression
- **Heavy (40-50%)**: Maximum size reduction, may impact quality

### Training Episodes

- **Experimentation**: 5-10 episodes
- **Production**: 20-50 episodes
- Monitor reward curves to determine convergence

### Hyperparameters

- Start with defaults (`lr=0.001`, `gamma=0.99`)
- Enable `use_kld=True` for more stable training
- Adjust `learning_rate` if training is unstable

---

## Troubleshooting

### RuntimeError: Policy model not found

**Solution:** Call `fit()` before `compress()` or load a pretrained policy.

### ValueError: compression_ratio must be in [0, 1)

**Solution:** Ensure compression ratio is between 0 and 1 (exclusive).

### CUDA Out of Memory

**Solution:** 
- Use smaller models
- Reduce batch size (not applicable for PruneNet, but relevant for evaluation)
- Use CPU by setting `device="cpu"`

---

## Citation

If you use PruneNet in your research, please cite:

```bibtex
@inproceedings{
        sengupta2025you,
        title={You Only Prune Once: Designing Calibration-Free Model Compression With Policy Learning},
        author={Ayan Sengupta and Siddhant Chaudhary and Tanmoy Chakraborty},
        booktitle={The Thirteenth International Conference on Learning Representations},
        year={2025},
        url={https://openreview.net/forum?id=5RZoYIT3u6}
    }
```

---

## License

MIT License - See LICENSE file for details.

---

## Support

- **Issues**: https://github.com/parmanu-lcs2/efficient_pruners/issues
- **Documentation**: See `README.md` and examples in `examples/`
- **Notebooks**: See `notebooks/` for interactive tutorials
