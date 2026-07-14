import React from "react";
import { motion, AnimatePresence } from "motion/react";
import { Upload, RefreshCw } from "lucide-react";
import { DishData } from "../types";

interface ImagePreviewProps {
  selectedDish: DishData | null;
  isScanning: boolean;
  customImage: string | null;
  activeDishKey: string;
  showGradCam: boolean;
  setShowGradCam: (show: boolean) => void;
  coordinates: { x: string; y: string; size: string; label: string }[];
  triggerUploadClick: () => void;
  fileInputRef: React.RefObject<HTMLInputElement | null>;
  handleFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export default function ImagePreview({
  selectedDish,
  isScanning,
  customImage,
  activeDishKey,
  showGradCam,
  setShowGradCam,
  coordinates,
  triggerUploadClick,
  fileInputRef,
  handleFileUpload
}: ImagePreviewProps) {
  return (
    <div className="relative bg-[#131315] border border-[#232326] rounded-3xl overflow-hidden flex flex-col shadow-2xl flex-1 min-h-[380px]">
      {/* Floated custom badge over photo exactly like the image! */}
      {selectedDish && !isScanning && (
        <>
          <div className="absolute top-4 left-4 z-20 bg-black/75 backdrop-blur-md border border-zinc-800 px-3.5 py-1.5 rounded-full flex items-center gap-2 shadow-lg">
            <div className="w-2 h-2 rounded-full bg-[#ff4f1d] animate-ping" />
            <span className="text-[11px] text-zinc-200 font-bold font-sans">
              Identified: {selectedDish.foodName} {activeDishKey === "pho" ? "(Beef)" : ""}
            </span>
          </div>
          <button 
            onClick={() => setShowGradCam(!showGradCam)}
            className="absolute top-4 right-4 z-20 bg-black/75 hover:bg-black backdrop-blur-md border border-zinc-800 px-3.5 py-1.5 rounded-full flex items-center gap-2 shadow-lg transition-all active:scale-95"
          >
            <span className="text-[11px] text-[#ff4f1d] font-bold font-sans">
              {showGradCam ? "Ẩn Góc Học Thuật" : "Góc Học Thuật (XAI)"}
            </span>
          </button>
        </>
      )}

      {/* The main viewport image */}
      <div className="relative flex-1 bg-[#09090a] overflow-hidden group">
        <img
          src={customImage || selectedDish?.unsplashUrl || "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?auto=format&fit=crop&w=800&q=80"}
          alt="Analyzed culinary masterpiece"
          referrerPolicy="no-referrer"
          className={`w-full h-full object-cover transition-transform duration-700 ${
            isScanning ? "blur-[2px] scale-102 brightness-75" : "scale-100"
          }`}
        />

        {/* Grad-CAM Heatmap overlay */}
        {showGradCam && !isScanning && coordinates?.map((coord, i) => (
          <div 
            key={i}
            className="absolute pointer-events-none"
            style={{
              top: coord.y,
              left: coord.x,
              width: coord.size,
              height: coord.size,
              transform: 'translate(-50%, -50%)',
              zIndex: 10
            }}
          >
            <div className="absolute inset-0 border-4 border-[#ff4f1d]/50 rounded-full animate-ping" style={{ animationDuration: "3s" }} />
            <div className="absolute inset-2 border-2 border-[#ff4f1d] rounded-full bg-[#ff4f1d]/20 backdrop-blur-sm shadow-[0_0_30px_rgba(255,79,29,0.5)] flex items-center justify-center">
              <span className="text-white text-[10px] font-bold px-2 py-1 bg-black/60 rounded uppercase tracking-widest whitespace-nowrap shadow-xl">
                {coord.label}
              </span>
            </div>
          </div>
        ))}

        {/* Laser Scanning Loop */}
        <AnimatePresence>
          {isScanning && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 pointer-events-none"
            >
              <div className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-[#ff4f1d] to-transparent animate-laser shadow-[0_0_15px_4px_rgba(255,79,29,0.7)] z-10" />
              <div className="absolute inset-0 bg-[#ff4f1d]/5 flex items-center justify-center">
                <div className="bg-[#101012]/95 border border-[#ff4f1d]/30 px-5 py-3.5 rounded-2xl shadow-[0_0_30px_rgba(255,79,29,0.15)] flex items-center gap-3 backdrop-blur-md transform scale-105">
                  <div className="relative flex items-center justify-center w-8 h-8 rounded-full bg-[#ff4f1d]/10">
                    <RefreshCw className="w-4 h-4 text-[#ff4f1d] animate-spin" />
                    <div className="absolute inset-0 rounded-full border border-[#ff4f1d]/30 animate-ping" />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[12px] font-display font-extrabold text-white tracking-widest uppercase">
                      Đang phân tích ảnh...
                    </span>
                    <span className="text-[10px] font-sans text-zinc-400 mt-0.5">
                      AI Model đang nhận diện món ăn
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Float Trigger for file input */}
        <button
          onClick={triggerUploadClick}
          disabled={isScanning}
          className="absolute bottom-4 right-4 bg-black/75 hover:bg-black text-white px-3.5 py-2 rounded-full text-xs font-bold border border-zinc-800 shadow-md flex items-center gap-2 active:scale-95 transition-all"
        >
          <Upload className="w-3.5 h-3.5 text-[#ff4f1d]" />
          <span>Upload Food Photo</span>
        </button>

        <input 
          type="file" 
          ref={fileInputRef as any} 
          onChange={handleFileUpload} 
          accept="image/*" 
          className="hidden" 
        />
      </div>
    </div>
  );
}
