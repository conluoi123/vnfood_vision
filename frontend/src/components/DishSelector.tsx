import React from "react";
import { Upload } from "lucide-react";

interface DishSelectorProps {
  activeDishKey: string;
  setActiveDishKey: (key: string) => void;
  isScanning: boolean;
  customImage: string | null;
  triggerUploadClick: () => void;
}

export default function DishSelector({
  activeDishKey,
  setActiveDishKey,
  isScanning,
  customImage,
  triggerUploadClick,
}: DishSelectorProps) {
  return (
    <div className="w-full bg-[#0b0a0a] border-b border-[#18181a] py-3">
      <div className="max-w-7xl mx-auto px-4 md:px-6 flex items-center gap-3 overflow-x-auto">
        <button
          onClick={() => setActiveDishKey("pho")}
          disabled={isScanning}
          className={`flex-none px-4 py-2 rounded-full text-xs font-bold transition-all ${
            activeDishKey === "pho" && !customImage
              ? "bg-[#ff4f1d] text-white shadow-lg shadow-[#ff4f1d]/20"
              : "bg-[#18181a] text-zinc-400 hover:text-white hover:bg-[#202023] border border-[#242427]"
          } active:scale-95 disabled:opacity-50`}
        >
          🍜 Phở Bò
        </button>
        <button
          onClick={() => setActiveDishKey("banhmi")}
          disabled={isScanning}
          className={`flex-none px-4 py-2 rounded-full text-xs font-bold transition-all ${
            activeDishKey === "banhmi" && !customImage
              ? "bg-[#ff4f1d] text-white shadow-lg shadow-[#ff4f1d]/20"
              : "bg-[#18181a] text-zinc-400 hover:text-white hover:bg-[#202023] border border-[#242427]"
          } active:scale-95 disabled:opacity-50`}
        >
          🥖 Bánh Mì
        </button>
        <button
          onClick={() => setActiveDishKey("buncha")}
          disabled={isScanning}
          className={`flex-none px-4 py-2 rounded-full text-xs font-bold transition-all ${
            activeDishKey === "buncha" && !customImage
              ? "bg-[#ff4f1d] text-white shadow-lg shadow-[#ff4f1d]/20"
              : "bg-[#18181a] text-zinc-400 hover:text-white hover:bg-[#202023] border border-[#242427]"
          } active:scale-95 disabled:opacity-50`}
        >
          🥓 Bún Chả
        </button>
        <button
          onClick={() => setActiveDishKey("caphetrung")}
          disabled={isScanning}
          className={`flex-none px-4 py-2 rounded-full text-xs font-bold transition-all ${
            activeDishKey === "caphetrung" && !customImage
              ? "bg-[#ff4f1d] text-white shadow-lg shadow-[#ff4f1d]/20"
              : "bg-[#18181a] text-zinc-400 hover:text-white hover:bg-[#202023] border border-[#242427]"
          } active:scale-95 disabled:opacity-50`}
        >
          ☕ Cà Phê Trứng
        </button>
        
        <div className="h-5 w-[1px] bg-zinc-800 self-center mx-1" />

        {/* Quick trigger for custom upload */}
        <button
          onClick={triggerUploadClick}
          disabled={isScanning}
          className={`flex-none px-4 py-2 rounded-full text-xs font-bold transition-all flex items-center gap-1.5 ${
            customImage 
              ? "bg-[#ff4f1d] text-white shadow-lg shadow-[#ff4f1d]/20"
              : "bg-[#18181a] text-zinc-400 hover:text-white hover:bg-[#202023] border border-[#242427]"
          }`}
        >
          <Upload className="w-3.5 h-3.5" />
          <span>{customImage ? "Đã Tải Ảnh" : "Tải Lên Ảnh Riêng"}</span>
        </button>
      </div>
    </div>
  );
}
