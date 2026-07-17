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

type FoodAnalysisResponse = {
  success?: boolean;
  foodName?: string;
  englishName?: string;
  confidence?: number;
};

const readFileAsDataUrl = (file: File): Promise<string> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(reader.error ?? new Error("Unable to read image file"));
    reader.onload = () => resolve(String(reader.result));
    reader.readAsDataURL(file);
  });

export const analyzeFoodImage = async (file: File) => {
  const image = await readFileAsDataUrl(file);
  const response = (await analyzeFoodAPI({ image, language: "VN" })) as FoodAnalysisResponse;

  return {
    success: response.success === true,
    data: {
      class_name: response.englishName ?? response.foodName ?? "Unknown",
      confidence: response.confidence ?? 0,
    },
  };
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

// 6. History APIs
export const getHistoryAPI = async () => {
  const response = await fetch("/api/v1/history/");
  return response.json();
};

export const addHistoryAPI = async (payload: { id: string; foodName: string; image: string; messages: string; dishData: string; }) => {
  const response = await fetch("/api/v1/history/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return response.json();
};

export const clearHistoryAPI = async () => {
  const response = await fetch("/api/v1/history/all", {
    method: "DELETE"
  });
  return response.json();
};

export const deleteHistoryItemAPI = async (id: string) => {
  const response = await fetch(`/api/v1/history/${id}`, {
    method: "DELETE"
  });
  return response.json();
};

export const getAnalyticsAPI = async () => {
  const response = await fetch("/api/v1/analytics/stats");
  return response.json();
};

export const updateSettingsAPI = async (payload: { llmEngine: string; visionModel: string; topK: number }) => {
  const response = await fetch("/api/v1/settings/update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return response.json();
};
