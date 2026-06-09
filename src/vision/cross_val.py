"""
cross_val.py — K-Fold Cross Validation cho VNFood Vision
Chạy: python src/vision/cross_val.py --folds 5 --epochs 10
"""
import argparse
import json
import sys
from pathlib import Path

import torch
import yaml
from sklearn.model_selection import StratifiedKFold
from torch.utils.data import DataLoader, Subset

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.vision.dataset import VietnameseFoodDataset, get_transforms
from src.vision.model import FocalLoss, VNFoodModel, compute_class_weights
from src.vision.train import train_one_epoch, validate


def run_cross_val(config_path: str, n_folds: int = 5, epochs: int = 10):
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    torch.manual_seed(config['data']['seed'])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print(f"\n{'='*60}")
    print(f"  K-Fold Cross Validation (k={n_folds})")
    print(f"  Backbone : {config['model']['backbone']}")
    print(f"  Device   : {device}")
    print(f"{'='*60}\n")

    # Load full dataset
    full_dataset = VietnameseFoodDataset(
        root_dir=config['data']['processed_dir'],
        transform=get_transforms(config, mode='train')
    )

    if len(full_dataset) == 0:
        print("⚠️  Dataset trống. Cross-val bỏ qua.")
        return

    labels = [label for _, label in full_dataset.samples]
    num_classes = len(full_dataset.classes)

    skf = StratifiedKFold(n_splits=n_folds, shuffle=True,
                          random_state=config['data']['seed'])

    fold_results = []

    for fold, (train_idx, val_idx) in enumerate(skf.split(range(len(full_dataset)), labels), 1):
        print(f"\n── FOLD {fold}/{n_folds} ─────────────────────────")
        print(f"   Train: {len(train_idx):,} | Val: {len(val_idx):,}")

        train_ds = Subset(full_dataset, train_idx)
        val_ds   = Subset(full_dataset, val_idx)

        train_loader = DataLoader(train_ds, batch_size=config['data']['batch_size'],
                                  shuffle=True, num_workers=config['data']['num_workers'],
                                  pin_memory=True)
        val_loader = DataLoader(val_ds, batch_size=config['data']['batch_size'],
                                shuffle=False, num_workers=config['data']['num_workers'],
                                pin_memory=True)

        # Fresh model cho mỗi fold
        model = VNFoodModel(
            backbone_name=config['model']['backbone'],
            num_classes=num_classes,
            pretrained=config['model']['pretrained'],
            dropout=config['model']['dropout']
        ).to(device)

        criterion = FocalLoss(
            alpha=config['loss']['focal_alpha'],
            gamma=config['loss']['focal_gamma'],
            label_smoothing=config['loss']['label_smoothing'],
            num_classes=num_classes
        )
        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=config['training']['learning_rate'],
            weight_decay=config['training']['weight_decay']
        )

        best_fold_acc = 0.0
        for epoch in range(1, epochs + 1):
            train_one_epoch(model, train_loader, criterion, optimizer, device, config, epoch)
            _, val_acc1, val_acc5 = validate(model, val_loader, criterion, device)
            best_fold_acc = max(best_fold_acc, val_acc1)
            print(f"   Epoch {epoch:02d}/{epochs} | Val Top-1: {val_acc1:.2f}% Top-5: {val_acc5:.2f}%")

        fold_results.append({"fold": fold, "best_val_acc": best_fold_acc})
        print(f"   ✅ Fold {fold} Best: {best_fold_acc:.2f}%")

    # Tổng kết
    avg_acc = sum(r['best_val_acc'] for r in fold_results) / n_folds
    std_acc = (sum((r['best_val_acc'] - avg_acc) ** 2 for r in fold_results) / n_folds) ** 0.5

    print(f"\n{'='*60}")
    print(f"  K-Fold kết quả:")
    for r in fold_results:
        print(f"    Fold {r['fold']}: {r['best_val_acc']:.2f}%")
    print(f"  Mean Accuracy: {avg_acc:.2f}% ± {std_acc:.2f}%")
    print(f"{'='*60}")

    # Lưu kết quả
    result_path = Path("checkpoints/cross_val_results.json")
    result_path.parent.mkdir(parents=True, exist_ok=True)
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump({"folds": fold_results, "mean_acc": avg_acc, "std_acc": std_acc}, f, indent=2)
    print(f"  📄 Kết quả đã lưu → {result_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--folds",  type=int, default=5)
    parser.add_argument("--epochs", type=int, default=10)
    args = parser.parse_args()
    run_cross_val(args.config, args.folds, args.epochs)
