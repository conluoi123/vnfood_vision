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
    <div className="bg-[#121111] p-5 border-t border-[#1e1d1d] flex flex-col gap-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-base font-bold text-zinc-100 font-sans tracking-tight flex items-center gap-2">
            Nutrition Analysis
            {isNutritionLoading && <RefreshCw className="w-4 h-4 text-[#ff4f1d] animate-spin" />}
          </h3>
          <p className="text-xs text-zinc-500 font-medium font-sans">
            Per standard serving ({activeDishKey === "pho" ? "450g" : "300g"})
          </p>
        </div>

        {/* Allergen dynamic badge */}
        <div className="bg-[#ff4f1d]/10 border border-[#ff4f1d]/20 px-3 py-1 rounded-full text-[11px] font-semibold text-[#ff4f1d]/90 flex items-center gap-1">
          <span>⚠️ Allergen:</span>
          <span className="font-bold">{currentNutrition.allergen}</span>
        </div>
      </div>

      {/* Progress bars & nutrition cards layout */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-5 items-center">
        {/* Calories & Protein Progress Bars */}
        <div className="md:col-span-7 space-y-3.5">
          {/* Calories Progress Bar */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs text-zinc-400 font-medium">
              <span>Calories</span>
              <span className="text-zinc-200 font-bold font-mono">
                {currentNutrition.calories} / {currentNutrition.caloriesTarget} kcal
              </span>
            </div>
            <div className="w-full bg-zinc-900 h-2.5 rounded-full overflow-hidden border border-[#222]">
              <div 
                className="bg-[#ff4f1d] h-full rounded-full transition-all duration-1000 shadow-[0_0_8px_rgba(255,79,29,0.5)]"
                style={{ width: `${(currentNutrition.calories / currentNutrition.caloriesTarget) * 100}%` }}
              />
            </div>
          </div>

          {/* Protein Progress Bar */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs text-zinc-400 font-medium">
              <span>Protein</span>
              <span className="text-zinc-200 font-bold font-mono">
                {currentNutrition.protein}g / {currentNutrition.proteinTarget}g
              </span>
            </div>
            <div className="w-full bg-zinc-900 h-2.5 rounded-full overflow-hidden border border-[#222]">
              <div 
                className="bg-[#ff4f1d]/75 h-full rounded-full transition-all duration-1000 shadow-[0_0_6px_rgba(255,79,29,0.3)]"
                style={{ width: `${(currentNutrition.protein / currentNutrition.proteinTarget) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Carbs & Fat Grid boxes */}
        <div className="md:col-span-5 grid grid-cols-2 gap-3">
          <div className="bg-[#18181a] border border-[#242427] rounded-xl p-3 flex flex-col justify-between">
            <span className="text-[11px] text-zinc-500 font-bold uppercase tracking-wider font-sans">
              Carbs
            </span>
            <span className="text-xl font-extrabold text-zinc-100 font-display mt-1">
              {currentNutrition.carbs}
            </span>
          </div>
          <div className="bg-[#18181a] border border-[#242427] rounded-xl p-3 flex flex-col justify-between">
            <span className="text-[11px] text-zinc-500 font-bold uppercase tracking-wider font-sans">
              Fat
            </span>
            <span className="text-xl font-extrabold text-zinc-100 font-display mt-1">
              {currentNutrition.fat}
            </span>
          </div>
        </div>
      </div>

      {/* Ingredients Breakdown Table */}
      <div className="mt-2 border border-[#242427] rounded-xl overflow-hidden bg-[#0c0c0d]">
        <div className="bg-[#18181a] px-4 py-2.5 flex items-center gap-2 border-b border-[#242427]">
          <Info className="w-3.5 h-3.5 text-zinc-400" />
          <span className="text-xs font-bold text-zinc-300 tracking-wide uppercase font-sans">
            Key Ingredients Breakdown
          </span>
        </div>
        <div className="divide-y divide-[#1e1e21]">
          {currentIngredients.map((ing, idx) => (
            <div key={idx} className="px-4 py-2.5 flex items-start gap-3 hover:bg-[#121214] transition-colors">
              <div className="mt-0.5 min-w-[16px]">
                <Check className="w-3.5 h-3.5 text-[#ff4f1d]" />
              </div>
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-zinc-200">{ing.name}</span>
                <span className="text-[11px] text-zinc-500 leading-tight mt-0.5">{ing.purpose}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
