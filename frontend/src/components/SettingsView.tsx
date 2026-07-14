import React from "react";
import { Settings, Cpu, Database } from "lucide-react";

export default function SettingsView() {
  return (
    <div className="flex-1 min-h-0 w-full p-4 md:p-8 overflow-y-auto">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold text-zinc-100 mb-6 flex items-center gap-3">
          <Settings className="w-6 h-6 text-[#ff4f1d]" />
          Cấu hình Hệ thống
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-zinc-900/40 border border-white/5 rounded-2xl p-6">
            <h3 className="text-lg font-bold text-zinc-200 flex items-center gap-2 mb-4">
              <Cpu className="w-5 h-5 text-[#ff4f1d]" />
              Mô hình Nhận diện (Vision)
            </h3>
            <div className="space-y-4">
              <label className="flex items-center justify-between">
                <span className="text-[14px] text-zinc-400">Backbone Model</span>
                <select className="bg-[#171719] border border-white/10 text-zinc-200 rounded-lg px-3 py-1.5 text-[14px] outline-none">
                  <option>MobileNetV3 (Fast)</option>
                  <option>EfficientNetB3 (Accurate)</option>
                </select>
              </label>
            </div>
          </div>

          <div className="bg-zinc-900/40 border border-white/5 rounded-2xl p-6">
            <h3 className="text-lg font-bold text-zinc-200 flex items-center gap-2 mb-4">
              <Database className="w-5 h-5 text-[#ff4f1d]" />
              Cấu hình RAG & LLM
            </h3>
            <div className="space-y-4">
              <label className="flex items-center justify-between">
                <span className="text-[14px] text-zinc-400">LLM Engine</span>
                <select className="bg-[#171719] border border-white/10 text-zinc-200 rounded-lg px-3 py-1.5 text-[14px] outline-none">
                  <option>Gemini 1.5 Flash</option>
                  <option>Colab / Ngrok LoRA</option>
                  <option>Local Qwen 2.5</option>
                </select>
              </label>
              <label className="flex items-center justify-between mt-3">
                <span className="text-[14px] text-zinc-400">Top-K Chunks (ChromaDB)</span>
                <input type="number" defaultValue={3} className="bg-[#171719] border border-white/10 text-zinc-200 rounded-lg px-3 py-1.5 text-[14px] outline-none w-20 text-center" />
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
