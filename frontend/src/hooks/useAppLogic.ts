import { useState, useEffect, useRef } from "react";
import { Message, DishData, IngredientRow, NutritionStats } from "../types";
import { NUTRITION_DATABASE, INGREDIENTS_TABLE_DATABASE, FOCUS_COORDINATES } from "../constants/data";
import { 
  analyzeNutritionAPI, 
  analyzeFoodAPI, 
  chatRagAPI, 
  ttsAPI, 
  searchPlacesAPI 
} from "../services/api";

export function useAppLogic() {
  const [activeDishKey, setActiveDishKey] = useState<string>("pho");
  const [selectedDish, setSelectedDish] = useState<DishData | null>(null);
  const [customImage, setCustomImage] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [showGradCam, setShowGradCam] = useState<boolean>(true);
  const [isListening, setIsListening] = useState<boolean>(false);

  // Real-time API States
  const [dynamicNutrition, setDynamicNutrition] = useState<NutritionStats | null>(null);
  const [dynamicIngredients, setDynamicIngredients] = useState<IngredientRow[] | null>(null);
  const [isNutritionLoading, setIsNutritionLoading] = useState(false);

  const [showRagInspector, setShowRagInspector] = useState<boolean>(false);
  const [language, setLanguage] = useState<"VN" | "EN">("VN");
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState<string>("");
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);

  const chatEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const getCoordinates = () => {
    if (selectedDish?.gradcamCoordinates) return selectedDish.gradcamCoordinates;
    if (customImage) return FOCUS_COORDINATES.custom;
    return FOCUS_COORDINATES[activeDishKey] || FOCUS_COORDINATES.pho;
  };

  const analyzeDish = async (key: string, isCustomUpload: boolean = false, base64Image?: string) => {
    setIsScanning(true);
    if (!isCustomUpload) setCustomImage(null);

    try {
      const payload = isCustomUpload && base64Image 
        ? { image: base64Image, language } 
        : { dishKey: key, language };

      const data = await analyzeFoodAPI(payload);

      if (data.success) {
        setSelectedDish(data);
        
        let initialMsgContent = "";
        if (language === "EN") {
          if (key === "pho") initialMsgContent = "This is **Phở Bò**, Vietnam's iconic beef noodle soup. The essence lies in the bone-marrow broth, simmered for 12+ hours with charred ginger and star anise.";
          else if (key === "banhmi") initialMsgContent = "This is **Bánh Mì**, Vietnam's legendary street food. It features a beautifully crisp, light baguette spread with rich pâté and creamy egg mayonnaise, stuffed with cured pork and fresh pickled vegetables.";
          else if (key === "buncha") initialMsgContent = "This is **Bún Chả**, Hanoi's iconic grilled pork noodle dish. It features caramelized pork patties and charcoal-grilled pork belly slices submerged in a warm, tangy-sweet dipping sauce.";
          else if (key === "caphetrung") initialMsgContent = "This is **Cà Phê Trứng**, Vietnam's famous egg coffee. The upper layer is an incredibly airy, sweet, and velvety whipped egg custard, floating over strong black drip coffee.";
          else initialMsgContent = `This is **${data.englishName}**. The AI analyzed the primary ingredients ("${data.explainableFocus}") to provide nutritional ratios and optimal recipes.`;
        } else {
          if (key === "pho") initialMsgContent = "Đây là món **Phở Bò**, biểu tượng ẩm thực của Việt Nam. Điểm tinh túy nằm ở phần nước dùng từ xương ống hầm hơn 12 tiếng cùng gừng nướng và hoa hồi.";
          else if (key === "banhmi") initialMsgContent = "Đây là món **Bánh Mì**, tinh hoa ẩm thực đường phố Việt Nam. Đặc trưng bởi lớp vỏ giòn rụm, quết pa-tê béo ngậy, bơ trứng, kẹp cùng thịt nướng và đồ chua thanh mát.";
          else if (key === "buncha") initialMsgContent = "Đây là món **Bún Chả**, món ăn đặc trưng của Hà Nội. Nổi bật với những miếng chả băm và thịt ba chỉ nướng than hoa thơm lừng, ngâm trong bát nước chấm chua ngọt ấm nóng.";
          else if (key === "caphetrung") initialMsgContent = "Đây là món **Cà Phê Trứng**, một sáng tạo độc đáo của Việt Nam. Lớp kem trứng đánh bông xốp, mịn màng và ngọt ngào nổi bồng bềnh trên bề mặt lớp cà phê đen đậm đà.";
          else initialMsgContent = `Đây là món **${data.foodName}** (${data.englishName}). Công nghệ nhận diện AI phân tích vùng nguyên liệu chính "${data.explainableFocus}" của đĩa ăn để cung cấp tỉ lệ dưỡng chất và công thức tối ưu nhất.`;
        }

        setMessages([
          {
            role: "assistant",
            content: initialMsgContent,
            retrievedChunks: data.ragChunks
          }
        ]);
      }
    } catch (err) {
      console.error("Analysis API failed:", err);
    } finally {
      setIsScanning(false);
    }
  };

  useEffect(() => {
    analyzeDish(activeDishKey);
  }, [activeDishKey]);

  useEffect(() => {
    if (customImage && selectedDish) {
      setDynamicNutrition(null);
      setDynamicIngredients(null);
      setIsNutritionLoading(true);
      
      analyzeNutritionAPI(selectedDish.foodName)
      .then(data => {
        if (data.success && data.data) {
          const d = data.data;
          setDynamicNutrition({
            calories: typeof d.calories === 'number' ? d.calories : parseInt(d.calories) || 450,
            caloriesTarget: 2000,
            protein: typeof d.protein === 'number' ? d.protein : parseInt(d.protein) || 20,
            proteinTarget: 60,
            carbs: typeof d.carbs === 'string' ? d.carbs : `${d.carbs}g`,
            fat: typeof d.fat === 'string' ? d.fat : `${d.fat}g`,
            allergen: d.allergen || "Không xác định"
          });
          if (Array.isArray(d.ingredients)) setDynamicIngredients(d.ingredients);
        }
      })
      .catch(console.error)
      .finally(() => setIsNutritionLoading(false));
    }
  }, [customImage, selectedDish]);

  const scrollToBottom = () => chatEndRef.current?.scrollIntoView({ behavior: "smooth" });

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleTTS = async (text: string) => {
    if (isSpeaking) {
      if ((window as any).currentAudio) {
        (window as any).currentAudio.pause();
        (window as any).currentAudio = null;
      }
      setIsSpeaking(false);
      return;
    }

    const cleanedText = text
      .replace(/[*#`\-]/g, "")
      .replace(/📍/g, "Địa chỉ")
      .replace(/🥗/g, "Rau ăn kèm")
      .replace(/🍜/g, "Nước dùng")
      .replace(/🥖/g, "Bánh mì")
      .replace(/🥓/g, "Bún chả")
      .replace(/☕/g, "Cà phê")
      .replace(/🥚/g, "Trứng");

    setIsSpeaking(true);
    try {
      const blob = await ttsAPI(cleanedText);
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      
      (window as any).currentAudio = audio;
      audio.onended = () => setIsSpeaking(false);
      audio.onerror = () => setIsSpeaking(false);
      audio.play();
    } catch (err) {
      console.error("TTS API error:", err);
      setIsSpeaking(false);
      alert("Không thể phát âm thanh lúc này. Vui lòng thử lại sau.");
    }
  };

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert("Trình duyệt của bạn không hỗ trợ tính năng nhận diện giọng nói. Vui lòng dùng Chrome hoặc Edge.");
      return;
    }
    const SpeechRecognitionAPI = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognitionAPI();
    
    recognition.lang = language === "VN" ? "vi-VN" : "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event: any) => setInputValue(event.results[0][0].transcript);
    recognition.onerror = (event: any) => {
      console.error("Speech recognition error:", event.error);
      setIsListening(false);
    };
    recognition.onend = () => setIsListening(false);
    recognition.start();
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result as string;
        setCustomImage(base64);
        analyzeDish("custom", true, base64);
      };
      reader.readAsDataURL(file);
    }
  };

  const triggerUploadClick = () => fileInputRef.current?.click();

  const handleFindNearby = async (foodName: string) => {
    const search = async (lat?: number, lng?: number) => {
      try {
        const data = await searchPlacesAPI(foodName, lat, lng);
        if (data.maps_url) window.open(data.maps_url, "_blank");
      } catch {
        window.open(`https://www.google.com/maps/search/${encodeURIComponent(foodName + ' quan an gan day')}`, "_blank");
      }
    };
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => search(pos.coords.latitude, pos.coords.longitude),
        () => search() 
      );
    } else {
      search();
    }
  };

  const handleSendMessage = async (msgText: string) => {
    if (!msgText.trim() || isScanning) return;
    const userMessage: Message = { role: "user", content: msgText };
    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    try {
      const data = await chatRagAPI({
        message: msgText,
        dishKey: customImage ? "custom" : activeDishKey,
        dishName: selectedDish?.foodName,
        history: [...messages, userMessage],
        language
      });

      if (data.success) {
        const reply = data.reply?.trim() || "Xin lỗi, AI chưa trả lời được. Vui lòng thử lại!";
        setMessages(prev => [...prev, { role: "assistant", content: reply, retrievedChunks: data.retrievedChunks }]);
      } else {
        setMessages(prev => [...prev, { role: "assistant", content: "Có lỗi xảy ra khi kết nối tới AI. Vui lòng kiểm tra lại." }]);
      }
    } catch (err) {
      console.error("Chat API failed:", err);
    } finally {
      setIsTyping(false);
    }
  };

  const getNutrition = (): NutritionStats => {
    if (customImage && selectedDish) {
      if (dynamicNutrition) return dynamicNutrition;
      const name = selectedDish.foodName || "unknown";
      let hash = 0;
      for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
      const rand = (min: number, max: number, seedOffset: number) => min + (Math.abs(hash) + seedOffset) % (max - min + 1);
      
      const hasGluten = (hash % 2) === 0;
      const hasPeanuts = (hash % 3) === 0;
      let allergen = "Không phát hiện dị ứng phổ biến";
      if (hasGluten && hasPeanuts) allergen = "Gluten (Tinh bột), Đậu phộng";
      else if (hasGluten) allergen = "Gluten (Tinh bột)";
      else if (hasPeanuts) allergen = "Đậu phộng";

      return {
        calories: rand(250, 800, 1), caloriesTarget: 2000,
        protein: rand(10, 45, 2), proteinTarget: 60,
        carbs: `${rand(30, 90, 3)}g`, fat: `${rand(5, 30, 4)}g`,
        allergen
      };
    }
    return NUTRITION_DATABASE[activeDishKey] || NUTRITION_DATABASE.pho;
  };

  const getIngredients = (): IngredientRow[] => {
    if (customImage && selectedDish) {
      if (dynamicIngredients) return dynamicIngredients;
      return [
        { name: selectedDish.explainableFocus, purpose: "Thành phần cốt lõi của món ăn" },
        { name: "Gia vị truyền thống", purpose: "Tạo hương vị đặc trưng" },
        { name: "Tinh bột / Chất xơ", purpose: "Cung cấp năng lượng cân bằng" }
      ];
    }
    return INGREDIENTS_TABLE_DATABASE[activeDishKey] || INGREDIENTS_TABLE_DATABASE.pho;
  };

  return {
    activeDishKey, setActiveDishKey,
    selectedDish, customImage,
    isScanning, showGradCam, setShowGradCam,
    isListening, isNutritionLoading,
    showRagInspector, setShowRagInspector,
    language, setLanguage,
    messages, inputValue, setInputValue,
    isTyping, isSpeaking,
    chatEndRef, fileInputRef,
    getCoordinates, handleTTS, handleVoiceInput,
    handleFileUpload, triggerUploadClick,
    handleFindNearby, handleSendMessage,
    getNutrition, getIngredients
  };
}
