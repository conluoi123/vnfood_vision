import os
import yaml
from pathlib import Path
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

class VietnameseFoodDataset(Dataset):
    """
    Custom Dataset for Vietnamese Food Recognition.
    Reads images from the ImageNet-style directory structure:
    processed_dir / vung_mien / loai_mon / ten_mon / image.jpg
    """
    def __init__(self, root_dir, transform=None):
        self.root_dir = Path(root_dir)
        self.transform = transform
        
        self.samples = []
        self.classes = []
        
        # Traverse the directory structure
        # Expected: root_dir / vung_mien / loai_mon / ten_mon
        if not self.root_dir.exists():
            print(f"Warning: Root directory {root_dir} does not exist.")
            return

        for vung_mien in self.root_dir.iterdir():
            if not vung_mien.is_dir(): continue
            for loai_mon in vung_mien.iterdir():
                if not loai_mon.is_dir(): continue
                for ten_mon in loai_mon.iterdir():
                    if not ten_mon.is_dir(): continue
                    
                    class_name = ten_mon.name
                    if class_name not in self.classes:
                        self.classes.append(class_name)
                    
                    class_idx = self.classes.index(class_name)
                    
                    # Collect all images in this class folder
                    for img_path in ten_mon.glob("*.*"):
                        if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                            self.samples.append((str(img_path), class_idx))
        
        self.classes.sort()
        # Re-index samples based on sorted classes
        class_to_idx = {cls_name: i for i, cls_name in enumerate(self.classes)}
        self.samples = [(path, class_to_idx[Path(path).parent.name]) for path, _ in self.samples]

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        try:
            image = Image.open(img_path).convert('RGB')
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            # Return a blank image in case of error (or handle it differently)
            image = Image.new('RGB', (384, 384))
            
        if self.transform:
            image = self.transform(image)
            
        return image, label

def get_transforms(config, mode='train'):
    """Returns the transformation pipeline based on the configuration and mode."""
    img_size = config['data']['image_size']
    
    if mode == 'train':
        aug_cfg = config['data']['augmentation']
        return transforms.Compose([
            transforms.RandomResizedCrop(img_size),
            transforms.RandAugment(num_ops=aug_cfg['randaugment_n'], magnitude=aug_cfg['randaugment_m']),
            transforms.ColorJitter(
                brightness=aug_cfg['color_jitter_brightness'],
                contrast=aug_cfg['color_jitter_contrast'],
                saturation=aug_cfg['color_jitter_saturation']
            ),
            transforms.GaussianBlur(kernel_size=aug_cfg['gaussian_blur_kernel']),
            transforms.ToTensor(),
            # Standard ImageNet normalization
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    else:
        # Validation/Test transforms
        return transforms.Compose([
            transforms.Resize(img_size + 32),
            transforms.CenterCrop(img_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

def create_dataloader(config_path='configs/config.yaml', mode='train'):
    """Utility function to create a dataloader from config"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    transform = get_transforms(config, mode)
    dataset = VietnameseFoodDataset(root_dir=config['data']['processed_dir'], transform=transform)
    
    # If dataset is empty (e.g., directory not found or empty), handle gracefully
    if len(dataset) == 0:
        print("Warning: Dataset is empty. Creating a dummy dataset for testing.")
        # Create a dummy dataset for pipeline testing if real data is missing
        class DummyDataset(Dataset):
            def __len__(self): return 10
            def __getitem__(self, idx): return torch.randn(3, config['data']['image_size'], config['data']['image_size']), 0
        dataset = DummyDataset()

    dataloader = DataLoader(
        dataset,
        batch_size=config['data']['batch_size'],
        shuffle=(mode == 'train'),
        num_workers=config['data']['num_workers'],
        pin_memory=True
    )
    
    return dataloader, dataset
