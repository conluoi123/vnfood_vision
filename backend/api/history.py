import os
import sqlite3
import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/history", tags=["History"])

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "history.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Create the table schema. We use IF NOT EXISTS so data persists across restarts.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id TEXT PRIMARY KEY,
            food_name TEXT,
            image TEXT,
            messages TEXT,
            dish_data TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

# Initialize on import
init_db()

class HistoryItemBase(BaseModel):
    id: str
    foodName: str
    image: str
    messages: str
    dishData: str

class HistoryItemResponse(HistoryItemBase):
    date: str

@router.get("/", response_model=List[HistoryItemResponse])
def get_history():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, food_name, image, messages, dish_data, created_at FROM scan_history ORDER BY created_at DESC LIMIT 50")
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "foodName": row[1],
                "image": row[2],
                "messages": row[3],
                "dishData": row[4],
                "date": row[5]
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def add_history(item: HistoryItemBase):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        created_at = datetime.datetime.now().isoformat()
        
        # Upsert: Update if exists, Insert if not
        cursor.execute("SELECT id FROM scan_history WHERE id = ?", (item.id,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute(
                "UPDATE scan_history SET messages = ?, dish_data = ? WHERE id = ?",
                (item.messages, item.dishData, item.id)
            )
        else:
            cursor.execute(
                "INSERT INTO scan_history (id, food_name, image, messages, dish_data, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (item.id, item.foodName, item.image, item.messages, item.dishData, created_at)
            )
            
        conn.commit()
        
        # Keep only the latest 20 items to avoid bloated DB
        cursor.execute(
            """
            DELETE FROM scan_history 
            WHERE id NOT IN (
                SELECT id FROM scan_history ORDER BY created_at DESC LIMIT 20
            )
            """
        )
        conn.commit()
        conn.close()
        return {"success": True, "id": item.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/all")
def clear_history():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scan_history")
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{item_id}")
def delete_history_item(item_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scan_history WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
