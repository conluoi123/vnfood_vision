export interface Message {
  role: "user" | "assistant";
  content: string;
  retrievedChunks?: {
    simScore: number;
    source: string;
    content: string;
  }[];
}

export interface DishData {
  foodName: string;
  englishName: string;
  confidence: number;
  calories: number;
  allergyInfo: string;
  explainableFocus: string;
  unsplashUrl: string | null;
  gradcamCoordinates?: { x: string; y: string; size: string; label: string }[];
  ragChunks: {
    simScore: number;
    source: string;
    content: string;
  }[];
  prompts: string[];
}

export interface IngredientRow {
  name: string;
  purpose: string;
}

export interface NutritionStats {
  calories: number;
  caloriesTarget: number;
  protein: number;
  proteinTarget: number;
  carbs: string;
  fat: string;
  allergen: string;
}
