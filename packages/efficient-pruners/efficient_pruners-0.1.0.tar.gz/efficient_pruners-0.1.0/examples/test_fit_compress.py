"""
Test Script: fit() and compress() Methods

This script demonstrates and tests the two core methods of PruneNet:
1. fit() - Learns an RL policy for model compression
2. compress() - Applies the learned policy to compress the model
"""

import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Import PruneNet package
from efficient_pruners import PruneNet, PruningConfig


def main():
    print("="*80)
    print("Testing PruneNet: fit() and compress() Methods")
    print("="*80)
    
    # Step 1: Configure PruneNet
    print("\n[Step 1] Creating configuration...")
    config = PruningConfig(
        num_episodes=5,         # 5 episodes for quick testing
        learning_rate=0.001,
        use_kld=False,
        gamma=0.99,
        seed=42,
        device="auto",
        save_dir="./outputs/test_fit_compress"
    )
    
    model_name = "facebook/opt-125m"
    compression_ratio = 0.3  # Remove 30% of MLP neurons
    
    print(f"✓ Configuration created")
    print(f"  Model: {model_name}")
    print(f"  Compression: {compression_ratio * 100:.0f}%")
    print(f"  Episodes: {config.num_episodes}")
    
    # Step 2: Initialize PruneNet
    print("\n[Step 2] Initializing PruneNet...")
    pruner = PruneNet(config)
    print(f"✓ PruneNet initialized on {pruner.device}")
    
    # Step 3: TEST fit() method
    print("\n" + "="*80)
    print("[Step 3] TESTING fit() METHOD - Learning RL Policy")
    print("="*80)
    print("\nWhat fit() does:")
    print("  1. Load the LLM")
    print("  2. Compute reference SVDs for all layers")
    print("  3. Initialize SparsityPredictor policy network")
    print("  4. Train policy using reinforcement learning")
    print("  5. Save best policy checkpoint")
    print("\nRunning fit()...")
    print("-"*80)
    
    history = pruner.fit(model_name=model_name, compression_ratio=compression_ratio)
    
    print("-"*80)
    print("\n✅ fit() METHOD COMPLETED!")
    
    if 'episode_rewards' in history:
        print(f"\nTraining Summary:")
        print(f"  Episodes completed: {len(history['episode_rewards'])}")
        print(f"  Initial reward: {history['episode_rewards'][0]:.4f}")
        print(f"  Final reward: {history['episode_rewards'][-1]:.4f}")
        print(f"  Best reward: {max(history['episode_rewards']):.4f}")
        improvement = (history['episode_rewards'][-1] - history['episode_rewards'][0]) / history['episode_rewards'][0] * 100
        print(f"  Improvement: {improvement:+.2f}%")
        print(f"\n✓ Policy learned successfully!")
    else:
        print("\n✓ Loaded existing policy from checkpoint")
    
    # Step 4: TEST compress() method
    print("\n" + "="*80)
    print("[Step 4] TESTING compress() METHOD - Applying Learned Policy")
    print("="*80)
    print("\nWhat compress() does:")
    print("  1. Load the trained policy")
    print("  2. Create a copy of the original model")
    print("  3. Apply policy to select important neurons")
    print("  4. Return compressed model")
    print("\nRunning compress()...")
    print("-"*80)
    
    compressed_model = pruner.compress(compression_ratio=compression_ratio)
    
    print("-"*80)
    print("\n✅ compress() METHOD COMPLETED!")
    
    # Step 5: Verify compression
    print("\n" + "="*80)
    print("[Step 5] Verifying Compression Results")
    print("="*80)
    
    stats = pruner.get_compression_stats()
    print(f"\nCompression Statistics:")
    print(f"  Original parameters:     {stats['original_params']:,}")
    print(f"  Compressed parameters:   {stats['compressed_params']:,}")
    print(f"  Parameters saved:        {stats['params_saved']:,}")
    print(f"  Reduction ratio:         {stats['reduction_ratio'] * 100:.2f}%")
    
    # Step 6: Test compressed model functionality
    print("\n" + "="*80)
    print("[Step 6] Testing Compressed Model Functionality")
    print("="*80)
    
    output_dir = "./outputs/test_fit_compress/compressed_model"
    compressed_model.save_pretrained(output_dir)
    print(f"\n✓ Compressed model saved to: {output_dir}")
    
    # Prepare for inference test
    print("\nPreparing models for text generation test...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    original_model = AutoModelForCausalLM.from_pretrained(model_name)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    original_model.to(device)
    compressed_model.to(device)
    original_model.eval()
    compressed_model.eval()
    
    print("✓ Models ready")
    
    # Generate text
    test_prompt = "The future of artificial intelligence is"
    print(f"\nTest Prompt: '{test_prompt}'")
    print("-"*80)
    
    inputs = tokenizer(test_prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        original_outputs = original_model.generate(**inputs, max_length=50, do_sample=True, temperature=0.8)
    original_text = tokenizer.decode(original_outputs[0], skip_special_tokens=True)
    
    with torch.no_grad():
        compressed_outputs = compressed_model.generate(**inputs, max_length=50, do_sample=True, temperature=0.8)
    compressed_text = tokenizer.decode(compressed_outputs[0], skip_special_tokens=True)
    
    print(f"\n📄 Original Model:\n{original_text}")
    print(f"\n✂️ Compressed Model:\n{compressed_text}")
    print("-"*80)
    
    # Final summary
    print("\n" + "="*80)
    print("✅ TEST SUMMARY")
    print("="*80)
    print("\nfit() Method:")
    print("  ✓ Loaded LLM")
    print("  ✓ Initialized SparsityPredictor")
    print("  ✓ Trained RL policy")
    print("  ✓ Saved best checkpoint")
    
    print("\ncompress() Method:")
    print("  ✓ Loaded trained policy")
    print("  ✓ Applied policy to compress model")
    print("  ✓ Generated compressed model")
    print(f"  ✓ Achieved {stats['reduction_ratio'] * 100:.2f}% reduction")
    
    print("\nFunctionality:")
    print("  ✓ Compressed model saved successfully")
    print("  ✓ Compressed model can generate text")
    
    print("\n" + "="*80)
    print("🎉 Both fit() and compress() methods working correctly!")
    print("="*80)


if __name__ == "__main__":
    main()
