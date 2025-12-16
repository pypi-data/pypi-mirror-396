from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version
version = {}
with open("src/efficient_pruners/__version__.py", "r") as f:
    exec(f.read(), version)

setup(
    name="efficient_pruners",
    version=version['__version__'],
    author="Parmanu, LCS2, IIT Delhi",
    author_email="",
    description="Calibration-Free Model Compression with Reinforcement Learning-Based Policy Learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/parmanu-lcs2/efficient_pruners",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.12.0",
        "transformers>=4.30.0",
        "numpy>=1.23.0",
        "scipy>=1.9.0",
        "tqdm>=4.65.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "jupyter>=1.0.0",
        ],
        "eval": [
            "lm-eval>=0.4.0",
            "datasets>=2.10.0",
            "evaluate>=0.4.0",
        ],
        "finetune": [
            "peft>=0.5.0",
            "pytorch-lightning>=2.0.0",
        ],
        "logging": [
            "wandb>=0.15.0",
            "tensorboard>=2.11.0",
        ],
        "all": [
            "lm-eval>=0.4.0",
            "datasets>=2.10.0",
            "evaluate>=0.4.0",
            "peft>=0.5.0",
            "pytorch-lightning>=2.0.0",
            "wandb>=0.15.0",
            "tensorboard>=2.11.0",
        ]
    },
    keywords=["model-compression", "pruning", "reinforcement-learning", "transformers", "llm", "deep-learning", "pytorch"],
)
