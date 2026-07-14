import { NutritionStats, IngredientRow } from "../types";

// Highly precise database for high fidelity display
export const NUTRITION_DATABASE: Record<string, NutritionStats> = {
  pho: {
    calories: 750,
    caloriesTarget: 2000,
    protein: 42,
    proteinTarget: 60,
    carbs: "82g",
    fat: "18g",
    allergen: "Gluten (Bánh phở)"
  },
  banhmi: {
    calories: 380,
    caloriesTarget: 2000,
    protein: 16,
    proteinTarget: 60,
    carbs: "52g",
    fat: "14g",
    allergen: "Gluten (Bột mì)"
  },
  buncha: {
    calories: 520,
    caloriesTarget: 2000,
    protein: 28,
    proteinTarget: 60,
    carbs: "74g",
    fat: "22g",
    allergen: "Không dị ứng"
  },
  caphetrung: {
    calories: 220,
    caloriesTarget: 2000,
    protein: 8,
    proteinTarget: 60,
    carbs: "24g",
    fat: "12g",
    allergen: "Lòng đỏ trứng, Sữa đặc"
  },
  custom: {
    calories: 480,
    caloriesTarget: 2000,
    protein: 32,
    proteinTarget: 60,
    carbs: "62g",
    fat: "16g",
    allergen: "Mức mẫn cảm nhẹ"
  }
};

export const INGREDIENTS_TABLE_DATABASE: Record<string, IngredientRow[]> = {
  pho: [
    { name: "Star Anise & Cinnamon", purpose: "Signature aromatic base" },
    { name: "Rice Stick Noodles", purpose: "Texture and carbohydrate" },
    { name: "Thin Sliced Brisket", purpose: "Primary protein source" }
  ],
  banhmi: [
    { name: "Pâté gan béo ngậy", purpose: "Tạo vị bùi béo ngọt tự nhiên" },
    { name: "Bơ trứng đánh tay", purpose: "Độ ngậy mượt thơm lừng xốt bánh mì" },
    { name: "Dưa cải chua ngọt", purpose: "Cân bằng vị béo, kích thích vị giác" }
  ],
  buncha: [
    { name: "Chả miếng & chả viên", purpose: "Nướng chín bằng than hoa đậm đà vị khói" },
    { name: "Nước mắm tỉ lệ vàng", purpose: "Vị chua ngọt mặn cay thanh dịu chuẩn Hà Nội" },
    { name: "Đu đủ xanh giòn", purpose: "Chống ngấy hoàn hảo tăng chất xơ" }
  ],
  caphetrung: [
    { name: "Lòng đỏ trứng tươi", purpose: "Đánh bông sánh mịn như kem mousse" },
    { name: "Cà phê Robusta phin", purpose: "Hương vị đắng nồng nàn cân bằng vị ngậy" },
    { name: "Mật ong & sữa đặc", purpose: "Tạo vị ngọt bùi và khử tanh triệt để" }
  ],
  custom: [
    { name: "Gia vị thảo mộc tự nhiên", purpose: "Hương vị nguyên bản ẩm thực" },
    { name: "Thành phần đạm nướng", purpose: "Hương vị đậm đà dinh dưỡng" },
    { name: "Rau thơm ăn kèm tươi", purpose: "Thanh mát cơ thể tăng vị thanh tao" }
  ]
};

// Friendly ingredient focus coordinates for Grad-CAM simulation
export const FOCUS_COORDINATES: Record<string, { x: string; y: string; size: string; label: string }[]> = {
  pho: [
    { x: "46%", y: "48%", size: "150px", label: "Thịt Bò Tươi Sấn" },
    { x: "62%", y: "42%", size: "110px", label: "Hành Lá & Rau Thơm" }
  ],
  banhmi: [
    { x: "50%", y: "40%", size: "160px", label: "Pâté Gan Gia Truyền" },
    { x: "32%", y: "55%", size: "110px", label: "Vỏ Bánh Giòn Rúm" }
  ],
  buncha: [
    { x: "42%", y: "45%", size: "160px", label: "Chả Quạt Than Hoa" },
    { x: "68%", y: "58%", size: "110px", label: "Đu Đủ Chu Chua Ngọt" }
  ],
  caphetrung: [
    { x: "50%", y: "34%", size: "180px", label: "Kem Trứng Đánh Bông" }
  ],
  custom: [
    { x: "50%", y: "50%", size: "160px", label: "Thành Phần Món Ăn" }
  ]
};
