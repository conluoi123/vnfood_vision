/**
 * API Service
 * Centralizes all backend communication.
 */

// 1. Analyze Nutrition
export const analyzeNutritionAPI = async (dishName: string) => {
  const response = await fetch("/api/v1/rag/analyze-nutrition", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dishName })
  });
  return response.json();
};

// 2. Analyze Food (Identify via Key or Image)
export const analyzeFoodAPI = async (payload: { dishKey?: string; image?: string; language: string }) => {
  const response = await fetch("/api/v1/rag/analyze-food", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return response.json();
};

// 3. RAG Chat
export const chatRagAPI = async (payload: {
  message: string;
  dishKey: string;
  dishName?: string;
  history: any[];
  language: string;
}) => {
  const response = await fetch("/api/v1/rag/chat-rag", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return response.json();
};

// 4. Text to Speech
export const ttsAPI = async (text: string) => {
  const response = await fetch("/api/v1/rag/tts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  });
  
  if (!response.ok) throw new Error("TTS failed");
  return response.blob();
};

// 5. Places Search
export const searchPlacesAPI = async (foodName: string, lat?: number, lng?: number) => {
  const response = await fetch("/api/v1/places/search-url", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ food_name: foodName, latitude: lat, longitude: lng, radius_km: 3 })
  });
  return response.json();
};
