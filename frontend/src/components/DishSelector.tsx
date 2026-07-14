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
    <div className="w-full bg-[#000000] border-b border-zinc-900 py-3 relative z-20">
      <div className="max-w-7xl mx-auto px-4 md:px-6 flex items-center gap-2 overflow-x-auto snap-x snap-mandatory [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
        <button
          onClick={() => setActiveDishKey("pho")}
          disabled={isScanning}
          className={`snap-start flex-none px-5 py-2 rounded-full text-[13px] font-medium transition-all duration-300 ${
            activeDishKey === "pho" && !customImage
              ? "bg-zinc-100 text-zinc-950 shadow-sm"
              : "bg-transparent text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900 border border-transparent"
          } active:scale-95 disabled:opacity-50`}
        >
          Phở Bò
        </button>
        <button
          onClick={() => setActiveDishKey("banhmi")}
          disabled={isScanning}
          className={`snap-start flex-none px-5 py-2 rounded-full text-[13px] font-medium transition-all duration-300 ${
            activeDishKey === "banhmi" && !customImage
              ? "bg-zinc-100 text-zinc-950 shadow-sm"
              : "bg-transparent text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900 border border-transparent"
          } active:scale-95 disabled:opacity-50`}
        >
          Bánh Mì
        </button>
        <button
          onClick={() => setActiveDishKey("buncha")}
          disabled={isScanning}
          className={`snap-start flex-none px-5 py-2 rounded-full text-[13px] font-medium transition-all duration-300 ${
            activeDishKey === "buncha" && !customImage
              ? "bg-zinc-100 text-zinc-950 shadow-sm"
              : "bg-transparent text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900 border border-transparent"
          } active:scale-95 disabled:opacity-50`}
        >
          Bún Chả
        </button>
        <button
          onClick={() => setActiveDishKey("caphetrung")}
          disabled={isScanning}
          className={`snap-start flex-none px-5 py-2 rounded-full text-[13px] font-medium transition-all duration-300 ${
            activeDishKey === "caphetrung" && !customImage
              ? "bg-zinc-100 text-zinc-950 shadow-sm"
              : "bg-transparent text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900 border border-transparent"
          } active:scale-95 disabled:opacity-50`}
        >
          Cà Phê Trứng
        </button>
        
        <div className="h-4 w-[1px] bg-zinc-800 self-center mx-2 flex-none" />

        {/* Quick trigger for custom upload */}
        <button
          onClick={triggerUploadClick}
          disabled={isScanning}
          className={`snap-start flex-none px-5 py-2 rounded-full text-[13px] font-medium transition-all duration-300 flex items-center gap-2 ${
            customImage 
              ? "bg-[#ff4f1d] text-white shadow-md shadow-[#ff4f1d]/20"
              : "bg-transparent text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900 border border-zinc-800"
          }`}
        >
          <Upload className="w-3.5 h-3.5" />
          <span>{customImage ? "Đã tải ảnh lên" : "Tải lên ảnh riêng"}</span>
        </button>
      </div>
    </div>
  );
}
