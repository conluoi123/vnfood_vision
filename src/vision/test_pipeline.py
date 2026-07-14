import sys
import os
import torch
from pathlib import Path

# Add project root to path so we can import src modules
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.vision.dataset import create_dataloader

def test_pipeline():
    print("Testing Pipeline Initialization...")
    config_path = project_root / 'configs' / 'config.yaml'
    
    try:
        dataloader, dataset = create_dataloader(config_path=str(config_path), mode='train')
        print(f"Dataset successfully created with {len(dataset)} samples.")
        
        # Test loading a single batch
        print("Loading a test batch...")
        images, labels = next(iter(dataloader))
        
        print("\nPipeline Test Successful! ✅")
        print("-" * 40)
        print(f"Batch Image Tensor Shape: {images.shape}")
        print(f"Batch Labels Tensor Shape: {labels.shape}")
        print(f"Expected Shape: [batch_size, 3, 384, 384]")
        print("-" * 40)
        
        if images.shape[1:] == torch.Size([3, 384, 384]):
            print("Shape verification: PASSED")
        else:
            print("Shape verification: FAILED")
            
    except Exception as e:
        print(f"Pipeline Test Failed! ❌\nError: {e}")

if __name__ == "__main__":
    test_pipeline()
