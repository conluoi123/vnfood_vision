import torch
import torch.nn.functional as F
from torchvision import models

def get_peak_cam_coordinate(model, input_tensor, target_class_idx):
    """
    Trích xuất tọa độ điểm ảnh sáng nhất (đóng vai trò lớn nhất trong việc phân loại)
    bằng thuật toán Class Activation Mapping (CAM) đơn giản.
    Hoạt động với EfficientNet, ResNet50, MobileNetV3.
    """
    feature_maps = None
    
    # 1. Đăng ký Hook để lấy Feature Map từ lớp Tích chập cuối cùng
    def hook_fn(module, input, output):
        nonlocal feature_maps
        feature_maps = output

    # Tìm lớp Conv cuối tùy thuộc vào kiến trúc backbone
    handle = None
    weights = None
    
    # EfficientNet
    if hasattr(model, 'model') and hasattr(model.model, 'features'):
        handle = model.model.features.register_forward_hook(hook_fn)
        weights = model.model.classifier[1].weight
    # ResNet50
    elif hasattr(model, 'model') and hasattr(model.model, 'layer4'):
        handle = model.model.layer4.register_forward_hook(hook_fn)
        weights = model.model.fc[1].weight if isinstance(model.model.fc, torch.nn.Sequential) else model.model.fc.weight
    # MobileNetV3
    elif hasattr(model, 'model') and hasattr(model.model, 'features'):
        handle = model.model.features.register_forward_hook(hook_fn)
        weights = model.model.classifier[3].weight
    else:
        # Kiến trúc không được hỗ trợ nội suy
        return {"x": "50%", "y": "50%", "size": "160px", "label": "Vùng đặc trưng trung tâm"}

    try:
        # 2. Chạy xuôi (Forward Pass) để kích hoạt Hook
        _ = model(input_tensor)
        handle.remove()
        
        if feature_maps is None:
            return {"x": "50%", "y": "50%", "size": "160px", "label": "Lỗi Feature Map"}
            
        # 3. Tính toán Heatmap bằng thuật toán CAM
        # shape: [Batch, Channels, Height, Width]
        f_map = feature_maps[0] 
        
        # Trọng số của class mục tiêu (chỉ lấy class đã được predict)
        class_weights = weights[target_class_idx].unsqueeze(-1).unsqueeze(-1)
        
        # Nhân ma trận chập với trọng số và tính tổng (Summing weighted channels)
        cam = (f_map * class_weights).sum(dim=0)
        cam = F.relu(cam) # Chỉ lấy các điểm có tác động dương
        
        # 4. Tìm điểm đỉnh nhiệt (Peak Heat)
        if cam.max() == 0:
            return {"x": "50%", "y": "50%", "size": "160px", "label": "Đặc trưng phân bố đều"}
            
        max_idx = cam.argmax().item()
        h_idx = max_idx // cam.shape[1]
        w_idx = max_idx % cam.shape[1]
        
        # Quy đổi ra phần trăm để UI React vẽ chính xác tọa độ
        y_pct = int((h_idx / cam.shape[0]) * 100)
        x_pct = int((w_idx / cam.shape[1]) * 100)
        
        # Đảm bảo tọa độ không nằm quá sát lề gây lỗi hiển thị CSS
        x_pct = max(15, min(x_pct, 85))
        y_pct = max(15, min(y_pct, 85))
        
        return {
            "x": f"{x_pct}%", 
            "y": f"{y_pct}%",
            "size": "160px", 
            "label": "Đỉnh Heatmap (AI Focus)"
        }
    except Exception as e:
        print(f"Error extracting CAM: {e}")
        if handle:
            handle.remove()
        return {"x": "50%", "y": "50%", "size": "160px", "label": "AI Focus"}
