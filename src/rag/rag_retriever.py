import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import json
import re
import unicodedata

import chromadb
from chromadb.config import Settings
import yaml
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer


def tokenize(text: str):
    text = text.lower()
    return re.findall(r"\w+", text, flags=re.UNICODE)


def normalize_for_match(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace("đ", "d")
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def detect_query_intent(query: str) -> str:
    query_norm = normalize_for_match(query)

    if any(term in query_norm for term in ["nguyen lieu", "gom nhung gi", "co gi", "can gi"]):
        return "ingredients"
    if any(term in query_norm for term in ["cach lam", "cach nau", "nau nhu the nao", "lam nhu the nao", "cong thuc"]):
        return "instructions"
    if any(term in query_norm for term in ["di ung", "gay di ung", "tom khong", "hai san", "dau phong"]):
        return "allergens"
    if any(term in query_norm for term in ["calo", "kcal", "nang luong", "bao nhieu calo"]):
        return "calories"
    if any(term in query_norm for term in ["tieng anh", "english", "dich"]):
        return "translation"
    if any(term in query_norm for term in ["an kem", "rau gi", "rau nao", "an voi"]):
        return "serving"
    return "summary"


class HybridRAGRetriever:
    def __init__(self, config_path="configs/config.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        self.rag_cfg = config["rag"]

        with open(self.rag_cfg["knowledge_base_path"], "r", encoding="utf-8") as f:
            self.kb = json.load(f)

        self.ids = list(self.kb.keys())
        self.id_to_index = {item_id: idx for idx, item_id in enumerate(self.ids)}
        self.documents = [self._make_document(self.kb[item_id]) for item_id in self.ids]

        self.embedding_model = SentenceTransformer(self.rag_cfg["embedding_model"])
        self.reranker = CrossEncoder(self.rag_cfg["reranker_model"])
        self.bm25 = BM25Okapi([tokenize(doc) for doc in self.documents])

        self.client = chromadb.PersistentClient(
            path=self.rag_cfg["chroma_dir"],
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_collection(self.rag_cfg["collection_name"])

    def _make_document(self, record: dict) -> str:
        return "\n".join([
            f"Tên món: {record.get('ten_mon', '')}",
            f"Nguyên liệu: {record.get('nguyen_lieu', '')}",
            f"Cách làm: {record.get('cach_lam', '')}",
            f"Dị ứng: {record.get('di_ung_enriched') or 'Chưa có thông tin'}",
            f"Calo: {record.get('calo_enriched') or 'Chưa có thông tin'}",
            f"Tên tiếng Anh: {record.get('english_translation') or 'Chưa có thông tin'}",
        ])

    def _focused_context(self, record: dict, intent: str) -> str:
        food_name = record.get("ten_mon", "")
        ingredients = record.get("nguyen_lieu", "")
        instructions = record.get("cach_lam", "")
        allergens = record.get("di_ung_enriched") or "Chưa có thông tin"
        calories = record.get("calo_enriched") or "Chưa có thông tin"
        english = record.get("english_translation") or "Chưa có thông tin"

        if intent == "ingredients":
            return f"Tên món: {food_name}\nNguyên liệu: {ingredients}"
        if intent == "instructions":
            return f"Tên món: {food_name}\nCách làm: {instructions}"
        if intent == "allergens":
            return f"Tên món: {food_name}\nDị ứng: {allergens}\nNguyên liệu: {ingredients}"
        if intent == "calories":
            return f"Tên món: {food_name}\nCalo: {calories}"
        if intent == "translation":
            return f"Tên món: {food_name}\nTên tiếng Anh: {english}"
        if intent == "serving":
            return f"Tên món: {food_name}\nThông tin ăn kèm/rau/gia vị liên quan nằm trong nguyên liệu:\n{ingredients}"

        return self._make_document(record)

    def _food_name_boost(self, query: str, record: dict) -> float:
        query_norm = normalize_for_match(query)
        food_norm = normalize_for_match(record.get("ten_mon", ""))
        if not query_norm or not food_norm:
            return 0.0

        query_tokens = set(query_norm.split())
        food_tokens = food_norm.split()
        if not food_tokens:
            return 0.0

        if re.search(rf"\b{re.escape(food_norm)}\b", query_norm):
            return 2.0 + min(len(food_tokens), 4) * 0.2

        overlap = sum(1 for token in food_tokens if token in query_tokens)
        coverage = overlap / len(food_tokens)
        if overlap >= 2 and coverage >= 0.5:
            return 0.7 * coverage

        return 0.0

    def retrieve(self, query: str):
        dense_top_k = self.rag_cfg["dense_top_k"]
        sparse_top_k = self.rag_cfg["sparse_top_k"]
        final_top_k = self.rag_cfg["final_top_k"]
        intent = detect_query_intent(query)

        query_embedding = self.embedding_model.encode(
            query, normalize_embeddings=True
        ).tolist()

        dense = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=dense_top_k,
        )

        candidate_ids = set(dense["ids"][0])

        bm25_scores = self.bm25.get_scores(tokenize(query))
        bm25_ranked = sorted(
            enumerate(bm25_scores),
            key=lambda x: x[1],
            reverse=True,
        )[:sparse_top_k]

        for idx, _ in bm25_ranked:
            candidate_ids.add(self.ids[idx])

        candidates = []
        for item_id in candidate_ids:
            idx = self.id_to_index[item_id]
            record = self.kb[item_id]
            candidates.append({
                "id": item_id,
                "document": self.documents[idx],
                "focused_context": self._focused_context(record, intent),
                "metadata": record,
                "intent": intent,
            })

        pairs = [(query, item["document"]) for item in candidates]
        rerank_scores = self.reranker.predict(pairs)

        for item, score in zip(candidates, rerank_scores):
            rerank_score = float(score)
            food_boost = self._food_name_boost(query, item["metadata"])
            item["rerank_score"] = rerank_score
            item["food_name_boost"] = food_boost
            item["score"] = rerank_score + food_boost

        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:final_top_k]
