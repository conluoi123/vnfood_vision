import logging
import os
import json
from datetime import datetime

LOG_DIR = "backend/logs"
os.makedirs(LOG_DIR, exist_ok=True)
SYSTEM_LOG_FILE = os.path.join(LOG_DIR, "system.log")

def log_event(event_type: str, data: dict):
    """
    Ghi log các sự kiện hệ thống (như prediction, RAG chat) vào file.
    Định dạng JSON để Frontend có thể dễ dàng parse và hiển thị trên Dashboard.
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "data": data
    }
    with open(SYSTEM_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

def get_logs(limit: int = 50):
    """Đọc N dòng log gần nhất."""
    if not os.path.exists(SYSTEM_LOG_FILE):
        return []
    logs = []
    with open(SYSTEM_LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in reversed(lines[-limit:]):
            try:
                logs.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    return logs
