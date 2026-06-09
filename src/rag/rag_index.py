import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import json
import sys
from pathlib import Path

import chromadb
from chromadb.config import Settings
import yaml
from sentence_transformers import SentenceTransformer

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def make_document(record: dict) -> str:
    return "\n".join([
        f"Tên món: {record.get('ten_mon', '')}",
        f"Nguyên liệu: {record.get('nguyen_lieu', '')}",
        f"Cách làm: {record.get('cach_lam', '')}",
        f"Dị ứng: {record.get('di_ung_enriched') or 'Chưa có thông tin'}",
        f"Calo: {record.get('calo_enriched') or 'Chưa có thông tin'}",
        f"Tên tiếng Anh: {record.get('english_translation') or 'Chưa có thông tin'}",
    ])


def build_index(config_path="configs/config.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    rag_cfg = config["rag"]
    kb_path = Path(rag_cfg["knowledge_base_path"])
    chroma_dir = rag_cfg["chroma_dir"]

    with open(kb_path, "r", encoding="utf-8") as f:
        kb = json.load(f)

    ids = []
    documents = []
    metadatas = []

    for key, record in kb.items():
        ids.append(key)
        documents.append(make_document(record))
        metadatas.append({
            "ten_mon": record.get("ten_mon", ""),
            "url": record.get("url_tham_khao", ""),
        })

    model = SentenceTransformer(rag_cfg["embedding_model"])
    embeddings = model.encode(documents, normalize_embeddings=True).tolist()

    client = chromadb.PersistentClient(
        path=chroma_dir,
        settings=Settings(anonymized_telemetry=False),
    )

    try:
        client.delete_collection(rag_cfg["collection_name"])
    except Exception:
        pass

    collection = client.create_collection(name=rag_cfg["collection_name"])
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(f"Built ChromaDB index with {len(documents)} documents")
    print(f"Saved to: {chroma_dir}")


if __name__ == "__main__":
    build_index()
