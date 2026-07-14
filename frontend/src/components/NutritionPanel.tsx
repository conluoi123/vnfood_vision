import React from "react";
import { RefreshCw, Info, Check } from "lucide-react";
import { NutritionStats, IngredientRow } from "../types";

interface NutritionPanelProps {
  currentNutrition: NutritionStats;
  currentIngredients: IngredientRow[];
  isNutritionLoading: boolean;
  activeDishKey: string;
}

export default function NutritionPanel({
  currentNutrition,
  currentIngredients,
  isNutritionLoading,
  activeDishKey
}: NutritionPanelProps) {
  return (
    <div className="flex flex-col gap-3 pb-6">
      <div className="flex items-center justify-between px-1">
        <h3 className="text-[14px] font-medium text-zinc-100 flex items-center gap-2">
          Thành phần dinh dưỡng
          {isNutritionLoading && <RefreshCw className="w-3 h-3 text-[#ff4f1d] animate-spin" />}
        </h3>
        <span className="text-[11px] text-zinc-500 font-mono tracking-wide">
          KHẨU PHẦN ~{activeDishKey === "pho" ? "450g" : "300g"}
        </span>
      </div>

      {/* 3-Cell Macro Bento */}
      <div className="grid grid-cols-2 gap-2">
        {/* Calories Cell (Spans full width) */}
        <div className="col-span-2 bg-zinc-900/40 border border-white/5 rounded-2xl p-4 flex flex-col justify-between relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-br from-[#ff4f1d]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
          <div className="flex justify-between items-start z-10">
            <span className="text-[13px] font-medium text-zinc-300">Calo</span>
            {currentNutrition.allergen !== "Không phát hiện dị ứng phổ biến" && (
              <span className="text-[9px] font-bold uppercase tracking-widest text-[#ff4f1d] bg-[#ff4f1d]/10 px-2 py-0.5 rounded-full">
                Cảnh Báo Dị Ứng
              </span>
            )}
          </div>
          <div className="mt-3 z-10 flex items-baseline gap-2">
            <span className="text-5xl font-light tracking-tight text-white">{currentNutrition.calories}</span>
            <span className="text-sm text-zinc-400 font-mono">/ {currentNutrition.caloriesTarget} kcal</span>
          </div>
          <div className="w-full bg-black/40 h-1.5 rounded-full mt-4 overflow-hidden z-10">
            <div 
              className="bg-[#ff4f1d] h-full rounded-full transition-all duration-1000"
              style={{ width: `${(currentNutrition.calories / currentNutrition.caloriesTarget) * 100}%` }}
            />
          </div>
        </div>

        {/* Protein Cell */}
        <div className="col-span-1 bg-zinc-900/40 border border-white/5 rounded-2xl p-4 flex flex-col justify-between">
          <span className="text-[13px] font-medium text-zinc-300">Chất đạm (Protein)</span>
          <div className="mt-2 flex flex-col">
            <span className="text-3xl font-light text-white">{currentNutrition.protein}g</span>
            <div className="w-full bg-black/40 h-1.5 rounded-full mt-3 overflow-hidden">
              <div 
                className="bg-zinc-300 h-full rounded-full transition-all duration-1000"
                style={{ width: `${(currentNutrition.protein / currentNutrition.proteinTarget) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Carbs & Fat Cell (Split) */}
        <div className="col-span-1 grid grid-rows-2 gap-2">
          <div className="bg-zinc-900/40 border border-white/5 rounded-2xl p-3 flex items-center justify-between">
            <span className="text-[13px] font-medium text-zinc-300">Tinh bột (Carbs)</span>
            <span className="text-[18px] font-light text-zinc-100">{currentNutrition.carbs}</span>
          </div>
          <div className="bg-zinc-900/40 border border-white/5 rounded-2xl p-3 flex items-center justify-between">
            <span className="text-[13px] font-medium text-zinc-300">Chất béo (Fat)</span>
            <span className="text-[18px] font-light text-zinc-100">{currentNutrition.fat}</span>
          </div>
        </div>
      </div>

      {/* Ingredients Composition (Card-per-spec style) */}
      <div className="mt-2 flex flex-col gap-2">
        <span className="text-[13px] font-medium text-zinc-400 px-1 mt-1 uppercase tracking-widest">Thành Phần Nguyên Liệu</span>
        {currentIngredients.map((ing, idx) => (
          <div key={idx} className="bg-transparent border border-white/5 rounded-xl px-4 py-3 flex flex-col gap-1 hover:bg-zinc-900/30 transition-colors">
            <span className="text-[15px] font-medium text-zinc-100">{ing.name}</span>
            <span className="text-[14px] text-zinc-400 leading-snug">{ing.purpose}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
