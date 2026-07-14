import React from "react";
import { UtensilsCrossed, Languages, User } from "lucide-react";

interface HeaderProps {
  language: "VN" | "EN";
  setLanguage: (lang: "VN" | "EN") => void;
}

export default function Header({ language, setLanguage }: HeaderProps) {
  return (
    <header className="w-full bg-[#0a0a0b]/90 border-b border-[#1e1e21]/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 md:px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-[#ff4f1d] text-white p-2 rounded-xl shadow-lg shadow-[#ff4f1d]/25">
            <UtensilsCrossed className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl md:text-2xl font-extrabold tracking-tight font-display text-[#ff4f1d] flex items-center gap-1.5">
              VNFood <span className="text-white">Vision</span>
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Language Translator Badge */}
          <button 
            onClick={() => {
              setLanguage(language === "VN" ? "EN" : "VN");
            }}
            className="flex items-center gap-1.5 bg-[#171719] hover:bg-[#202023] text-zinc-300 px-3 py-1.5 rounded-full text-xs font-semibold border border-[#232326] transition-all"
          >
            <Languages className="w-3.5 h-3.5 text-[#ff4f1d]" />
            <span className="text-[10px] uppercase font-bold tracking-wider">{language}</span>
          </button>

          {/* User Account Mock Button */}
          <button className="w-8 h-8 rounded-full bg-[#171719] border border-[#232326] flex items-center justify-center text-zinc-400 hover:text-white hover:border-zinc-600 transition-colors">
            <User className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
