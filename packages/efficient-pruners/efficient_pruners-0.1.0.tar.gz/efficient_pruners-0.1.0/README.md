# PruneNet: Calibration-Free Model Compression with Policy Learning

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-1.12+-red.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains **PruneNet**, a novel model compression framework that uses reinforcement learning to compress large language models without requiring calibration data.

Based on the paper: [You Only Prune Once: Designing Calibration-Free Model Compression With Policy Learning](https://arxiv.org/abs/2501.15296)

## ✨ Key Features

- 🎯 **No Calibration Data Required** - Learns compression policy directly from model weights
- 🤖 **Reinforcement Learning-Based** - Learns optimal neuron selection strategy
- 📊 **Preserves Spectral Properties** - Maintains weight matrix characteristics
- 🚀 **Easy to Use** - Simple `fit()` and `compress()` API following scikit-learn patterns
- 🔧 **Flexible Configuration** - Extensive hyperparameter control
- 📦 **Multiple Architectures** - Supports OPT, Llama, Phi, Falcon

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/parmanu-lcs2/efficient_pruners
cd efficient_pruners
pip install -e .
```

### Basic Usage (New API)

```python
from efficient_pruners import PruneNet, PruningConfig

# Configure hyperparameters
config = PruningConfig(
    num_episodes=20,
    learning_rate=0.001
)

# Initialize pruner
pruner = PruneNet(config)

# Train policy on specific model with target compression ratio
pruner.fit(model_name="facebook/opt-125m", compression_ratio=0.3)

# Compress with the same or different ratio
compressed_model = pruner.compress(compression_ratio=0.3)

# Save compressed model
compressed_model.save_pretrained("./compressed_model")

# Test text generation with compressed LLM
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("facebook/opt-125m")
inputs = tokenizer("The future of AI is", return_tensors="pt")

# Generate text with compressed model
outputs = compressed_model.generate(**inputs, max_length=50)
text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(text)
```

### Legacy CLI Usage

The original command-line interface is still available in the `prunenet/` directory:

```bash
python3 -m prunenet \
    --model_name facebook/opt-125m \
    --compression_ratio 0.3 \
    --save_dir ./models/ \
    --device cuda:0
```

## 📖 Documentation

- **[API Guide](docs/API_GUIDE.md)** - Complete API reference
- **[Test Notebook](notebooks/test_fit_compress.ipynb)** - Interactive fit/compress test with visualizations
- **[Test Script](examples/test_fit_compress.py)** - Automated fit/compress test

## 📂 Project Structure

```
PruneNet/
├── src/efficient_pruners/     # Main package
│   ├── core.py                # PruneNet class (fit/compress API)
│   ├── config.py              # PruningConfig dataclass
│   ├── models/                # SparsityPredictor policy network
│   │   └── sparsity_predictor.py
│   └── utils/                 # Model and reward utilities
│       ├── model_utils.py
│       └── reward_utils.py
├── examples/                  # Test & usage examples
│   └── test_fit_compress.py   # Complete fit/compress test script
├── notebooks/                 # Interactive tutorials
│   └── test_fit_compress.ipynb  # Complete fit/compress test notebook
├── docs/                      # Documentation
│   └── API_GUIDE.md
├── prunenet/                  # Original CLI implementation
├── setup.py                   # Package setup
├── pyproject.toml             # Modern build system
└── requirements.txt           # Dependencies
```

## 🎯 Supported Models

- **OPT**: facebook/opt-125m, facebook/opt-1.3b, etc.
- **Llama**: meta-llama/Llama-2-7b-hf, etc.
- **Phi**: microsoft/phi-1, microsoft/phi-2, etc.
- **Falcon**: tiiuae/falcon-7b, etc.

## 🧪 Running Examples

### Test Script

Run the comprehensive test to verify both `fit()` and `compress()` methods:

```bash
python examples/test_fit_compress.py
```

This script will:
- ✅ Train an RL policy using `fit()`
- ✅ Compress the model using `compress()`
- ✅ **Test `.generate()` on the compressed LLM**
- ✅ Compare outputs between original and compressed models
- ✅ Display compression statistics

### Interactive Notebook

```bash
jupyter notebook notebooks/test_fit_compress.ipynb
```

The notebook includes:
- Step-by-step walkthrough of `fit()` and `compress()`
- Visualizations of training progress
- **Interactive text generation testing with compressed model**
- Side-by-side comparison of model outputs

## ⚙️ Advanced Configuration

```python
config = PruningConfig(
    num_episodes=20,
    learning_rate=0.001,
    use_kld=True,          # Enable KL divergence regularization
    gamma=0.99,            # Reward discount factor
    device="auto",         # Auto-detect GPU/CPU
    save_dir="./outputs"   # Checkpoint directory
)

pruner = PruneNet(config)
pruner.fit(model_name="facebook/opt-125m")
compressed_model = pruner.compress(compression_ratio=0.3)
```

See [API_GUIDE.md](docs/API_GUIDE.md) for all configuration options.

## 📊 Performance

Typical compression results on OPT-125M:

| Compression | Size Reduction | Perplexity Impact |
|-------------|----------------|-------------------|
| 20%         | ~15%           | +2-3%             |
| 30%         | ~22%           | +3-5%             |
| 40%         | ~30%           | +5-8%             |
| 50%         | ~37%           | +8-12%            |

## 🔬 Research & Original Implementation

The original research scripts are preserved in `prunenet/` and `experiments/` directories. See the original README sections below for research-specific details.

---

## Original Evaluation Scripts

<!-- We re-use the LM evaluation scripts from -->
<!-- [SliceGPT](https://github.com/microsoft/TransformerCompression) to evaluate our -->
<!-- compressed models. See `experiments/run_lm_eval.py` for details. See the -->
<!-- `experiments/run_llm_eval*` scripts for details on how we evaluate the models. -->
<!-- For our running example of `microsoft/phi-2`, the script -->
<!-- `experiments/run_llm_eval_phi.sh` is helpful. -->

## Slicing the attention modules

<!-- In addition to slicing the FFN weight matrices, the scripts -->
<!-- `experiments/trainable_activation_sparsity_allmodules.py` and -->
<!-- `experiments/run_lm_eval_allmodules.py` slice the attention modules using the -->
<!-- same pruning technique. However, we observed that doing this harms the -->
<!-- compressed model's performance significantly, and this step is therefore not -->
<!-- advised. -->

## Citation

If you find our work useful in your projects/research, kindly cite our paper:

    @inproceedings{
        sengupta2025you,
        title={You Only Prune Once: Designing Calibration-Free Model Compression With Policy Learning},
        author={Ayan Sengupta and Siddhant Chaudhary and Tanmoy Chakraborty},
        booktitle={The Thirteenth International Conference on Learning Representations},
        year={2025},
        url={https://openreview.net/forum?id=5RZoYIT3u6}
    }
