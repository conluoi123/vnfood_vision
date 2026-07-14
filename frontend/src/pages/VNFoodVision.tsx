import React, { useState, useRef } from "react";
import { motion } from "framer-motion";
import {
  UploadCloud,
  Search,
  MapPin,
  Languages,
  Send,
  ChefHat,
  AlertTriangle,
  Flame,
  Beef,
  Wheat,
  CheckCircle2,
  Loader2
} from "lucide-react";
import { analyzeFoodImage } from "../services/api";

// Dùng tạm ảnh Unsplash do ảnh AI sinh chưa nằm trong thư mục Frontend
const MOCK_PHO_IMAGE = "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?q=80&w=1000&auto=format&fit=crop";

interface Message {
  id: number;
  type: "user" | "ai";
  content: string;
}

export default function VNFoodVision() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      type: "user",
      content: "Tell me more about this specific dish and how it's usually prepared.",
    },
    {
      id: 2,
      type: "ai",
      content: "This is **Phở Bò**, Vietnam's iconic beef noodle soup. The essence lies in the bone-marrow broth, simmered for 12+ hours with charred ginger and star anise.",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [uploadedImage, setUploadedImage] = useState<string>(MOCK_PHO_IMAGE);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [prediction, setPrediction] = useState<{name: string, conf: number} | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;
    const newUserMessage: Message = { id: messages.length + 1, type: "user", content: inputValue };
    setMessages((prev) => [...prev, newUserMessage]);
    setInputValue("");
    
    // Giả lập AI trả lời
    setTimeout(() => {
      setMessages((prev) => [...prev, { id: prev.length + 1, type: "ai", content: "I am analyzing the image to give you more insights. Please wait..." }]);
    }, 800);
  };

  const processFile = async (file: File) => {
    const reader = new FileReader();
    reader.onload = (event) => setUploadedImage(event.target?.result as string);
    reader.readAsDataURL(file);

    setIsAnalyzing(true);
    setPrediction(null);
    try {
      const res = await analyzeFoodImage(file);
      if (res.success) {
        setPrediction({ name: res.data.class_name, conf: res.data.confidence });
      }
    } catch (err) {
      console.error("Lỗi khi phân tích ảnh", err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith("image/")) {
      processFile(file);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) {
      processFile(file);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-gray-100 font-sans selection:bg-[#FF571A]/30 flex flex-col">
      {/* Header - Glassmorphism */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-[#0A0A0A]/80 border-b border-white/5 shadow-2xl shadow-[#FF571A]/5">
        <div className="max-w-[1600px] mx-auto px-6 h-20 flex items-center justify-between">
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-[#FF571A] to-[#FF8A00] p-2.5 rounded-xl shadow-lg shadow-[#FF571A]/20">
              <ChefHat className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              VNFood Vision
            </h1>
          </motion.div>
          <div className="flex items-center gap-4">
            <div className="px-4 py-2 rounded-full bg-white/5 border border-white/10 flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-xs font-semibold tracking-wider text-gray-300 uppercase">Academic Mode</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <main className="max-w-[1600px] mx-auto p-6 grid grid-cols-1 xl:grid-cols-12 gap-8 w-full flex-1">
        
        {/* === LEFT COLUMN: Vision Zone === */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="xl:col-span-7 flex flex-col gap-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-medium text-[#FF571A] flex items-center gap-2">
              <Search className="w-5 h-5" /> Vision & Discovery Zone
            </h2>
          </div>

          {/* Upload Area */}
          <div 
            className={`relative h-[400px] w-full rounded-3xl overflow-hidden group transition-all duration-300 border-2 cursor-pointer ${isDragging ? 'border-[#FF571A] bg-[#FF571A]/5' : 'border-white/10 bg-white/5 hover:border-[#FF571A]/50 hover:shadow-[0_0_30px_rgba(255,87,26,0.15)]'}`}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
          >
            <input type="file" ref={fileInputRef} className="hidden" accept="image/*" onChange={handleFileSelect} />
            <img src={uploadedImage} alt="Food Preview" className="absolute inset-0 w-full h-full object-cover opacity-80 group-hover:opacity-40 transition-opacity duration-500" />
            <div className="absolute inset-0 bg-gradient-to-t from-[#0A0A0A] via-transparent to-transparent opacity-80" />
            
            {/* Drag Overlay */}
            <div className="absolute inset-0 flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
              <div className="p-5 rounded-full bg-[#FF571A]/20 backdrop-blur-md mb-4 border border-[#FF571A]/30">
                <UploadCloud className="w-12 h-12 text-[#FF571A]" />
              </div>
              <p className="text-white font-medium text-xl drop-shadow-md">Click or Drop Image Here</p>
            </div>
          </div>

          {/* Result Banner */}
          {isAnalyzing && (
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="bg-[#FF571A]/10 border border-[#FF571A]/30 p-6 rounded-3xl flex items-center justify-center gap-4 shadow-lg backdrop-blur-sm">
              <Loader2 className="w-8 h-8 text-[#FF571A] animate-spin" />
              <span className="text-xl font-medium text-[#FF571A]">AI Chef is analyzing your food...</span>
            </motion.div>
          )}
          {prediction && !isAnalyzing && (
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className={`p-6 rounded-3xl flex items-center justify-between shadow-lg backdrop-blur-sm border ${prediction.conf < 0.4 ? 'bg-gradient-to-r from-red-500/20 to-orange-500/10 border-red-500/30 shadow-[0_0_30px_rgba(239,68,68,0.15)]' : 'bg-gradient-to-r from-green-500/20 to-emerald-500/10 border-green-500/30 shadow-[0_0_30px_rgba(34,197,94,0.15)]'}`}>
              <div className="flex items-center gap-5">
                 <div className={`p-4 rounded-2xl border shadow-inner ${prediction.conf < 0.4 ? 'bg-red-500/20 border-red-500/30' : 'bg-green-500/20 border-green-500/30'}`}>
                   {prediction.conf < 0.4 ? <AlertTriangle className="w-8 h-8 text-red-400" /> : <CheckCircle2 className="w-8 h-8 text-green-400" />}
                 </div>
                 <div>
                   <p className={`text-sm font-bold uppercase tracking-widest mb-1 ${prediction.conf < 0.4 ? 'text-red-400' : 'text-green-400'}`}>
                     {prediction.conf < 0.4 ? 'Low Confidence' : 'Match Found'}
                   </p>
                   <h3 className="text-3xl font-extrabold text-white drop-shadow-lg">{prediction.name}</h3>
                 </div>
              </div>
              <div className="text-right pr-4">
                 <p className={`text-sm font-bold uppercase tracking-widest mb-1 ${prediction.conf < 0.4 ? 'text-red-400/80' : 'text-green-400/80'}`}>Confidence</p>
                 <p className={`text-4xl font-extrabold drop-shadow-lg ${prediction.conf < 0.4 ? 'text-red-400' : 'text-green-400'}`}>{(prediction.conf * 100).toFixed(1)}%</p>
              </div>
            </motion.div>
          )}

          {/* Nutrition Card */}
          <div className="rounded-3xl bg-white/5 border border-white/10 p-8 backdrop-blur-sm relative overflow-hidden">
            {/* Thanh màu bên trái */}
            <div className="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-[#FF571A] to-[#FF8A00]" />
            
            <div className="flex justify-between items-start mb-8 pl-4">
              <div>
                <h3 className="text-2xl font-semibold text-white mb-1">Nutrition Analysis</h3>
                <p className="text-sm text-gray-400">Per standard serving (450g)</p>
              </div>
              <div className="px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-red-400" />
                <span className="text-xs font-medium text-red-400 uppercase tracking-wide">Allergen: Gluten</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-10 pl-4">
              {/* Progress Bars */}
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-300 flex items-center gap-1.5"><Flame className="w-4 h-4 text-[#FF571A]" /> Calories</span>
                    <span className="text-white font-medium">750 / 2000 kcal</span>
                  </div>
                  <div className="h-2.5 rounded-full bg-white/10 overflow-hidden">
                    <motion.div initial={{ width: 0 }} animate={{ width: "37.5%" }} transition={{ duration: 1, ease: "easeOut" }} className="h-full bg-gradient-to-r from-[#FF571A] to-[#FF8A00] rounded-full shadow-[0_0_10px_#FF571A]" />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-300 flex items-center gap-1.5"><Beef className="w-4 h-4 text-blue-400" /> Protein</span>
                    <span className="text-white font-medium">42g / 60g</span>
                  </div>
                  <div className="h-2.5 rounded-full bg-white/10 overflow-hidden">
                    <motion.div initial={{ width: 0 }} animate={{ width: "70%" }} transition={{ delay: 0.2, duration: 1 }} className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full shadow-[0_0_10px_#3B82F6]" />
                  </div>
                </div>
              </div>
              
              {/* Mini Data Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="rounded-2xl bg-white/5 border border-white/5 p-5 flex flex-col justify-center hover:bg-white/10 transition-colors">
                  <span className="text-gray-400 text-sm mb-1 flex items-center gap-1.5"><Wheat className="w-4 h-4 text-yellow-500" /> Carbs</span>
                  <span className="text-3xl font-semibold text-white">82<span className="text-lg text-gray-500">g</span></span>
                </div>
                <div className="rounded-2xl bg-white/5 border border-white/5 p-5 flex flex-col justify-center hover:bg-white/10 transition-colors">
                  <span className="text-gray-400 text-sm mb-1">Fat</span>
                  <span className="text-3xl font-semibold text-white">18<span className="text-lg text-gray-500">g</span></span>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button className="flex-[2] py-4 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors flex items-center justify-center gap-2 text-white font-medium">
              <Search className="w-5 h-5 text-[#FF571A]" /> Read Name
            </button>
            <button className="flex-[3] py-4 rounded-2xl bg-gradient-to-r from-[#FF571A] to-[#FF8A00] hover:opacity-90 transition-opacity flex items-center justify-center gap-2 text-white font-medium shadow-lg shadow-[#FF571A]/20">
              <MapPin className="w-5 h-5" /> Find Nearby
            </button>
            <button className="w-20 py-4 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors flex items-center justify-center text-gray-400">
              <Languages className="w-5 h-5" />
            </button>
          </div>
        </motion.div>

        {/* === RIGHT COLUMN: Chat Interface === */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="xl:col-span-5 flex flex-col gap-6 h-[850px]">
          <h2 className="text-xl font-medium text-[#FF571A] flex items-center gap-2">
            <ChefHat className="w-5 h-5" /> Chef AI Assistant
          </h2>
          
          <div className="flex-1 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-sm flex flex-col overflow-hidden relative">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 [&::-webkit-scrollbar]:hidden">
              {messages.map((msg, i) => (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }} key={msg.id} className={`flex gap-4 ${msg.type === "user" ? "flex-row-reverse" : ""}`}>
                  {msg.type === "ai" && (
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#FF571A] to-[#FF8A00] flex items-center justify-center shrink-0 shadow-lg shadow-[#FF571A]/20">
                      <ChefHat className="w-5 h-5 text-white" />
                    </div>
                  )}
                  <div className={`max-w-[85%] p-4 rounded-2xl ${msg.type === "user" ? "bg-white/10 text-white rounded-tr-sm" : "bg-[#FF571A]/10 text-gray-100 border border-[#FF571A]/20 rounded-tl-sm"}`}>
                    <p className="leading-relaxed whitespace-pre-wrap text-[15px]">{msg.content}</p>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Input Area */}
            <div className="p-5 bg-black/40 border-t border-white/5 backdrop-blur-md">
              <div className="flex gap-2 mb-4 overflow-x-auto pb-2 [&::-webkit-scrollbar]:hidden">
                {["How to cook this?", "Show me a healthy version", "Historical origin"].map((suggestion) => (
                  <button key={suggestion} onClick={() => setInputValue(suggestion)} className="px-4 py-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-xs text-gray-300 whitespace-nowrap transition-colors">
                    {suggestion}
                  </button>
                ))}
              </div>
              <div className="relative flex items-center bg-[#0A0A0A] border border-white/10 rounded-2xl p-1.5 focus-within:border-[#FF571A]/50 focus-within:ring-1 focus-within:ring-[#FF571A]/50 transition-all shadow-inner">
                <input 
                  type="text" 
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask Chef AI anything..." 
                  className="w-full bg-transparent border-none outline-none px-4 py-2.5 text-[15px] text-white placeholder:text-gray-600" 
                />
                <button onClick={handleSendMessage} className="p-3 bg-[#FF571A] hover:bg-[#FF8A00] transition-colors rounded-xl flex items-center justify-center text-white shadow-lg shadow-[#FF571A]/20">
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </motion.div>

      </main>
    </div>
  );
}
