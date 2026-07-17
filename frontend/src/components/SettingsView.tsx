import React, { useState, useEffect } from "react";
import { Settings, Cpu, Database, Save } from "lucide-react";
import { updateSettingsAPI } from "../services/api";

export default function SettingsView() {
  const [visionModel, setVisionModel] = useState(() => localStorage.getItem("visionModel") || "MobileNetV3 (Fast)");
  const [llmEngine, setLlmEngine] = useState(() => localStorage.getItem("llmEngine") || "Gemini 3.1 Flash Lite");
  const [topK, setTopK] = useState(() => localStorage.getItem("topK") || "3");

  useEffect(() => {
    localStorage.setItem("visionModel", visionModel);
    localStorage.setItem("llmEngine", llmEngine);
    localStorage.setItem("topK", topK);
  }, [visionModel, llmEngine, topK]);

  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");

  const handleSave = async () => {
    setIsSaving(true);
    setSaveMessage("");
    try {
      await updateSettingsAPI({
        llmEngine,
        visionModel,
        topK: parseInt(topK.toString()) || 3
      });
      setSaveMessage("Đã lưu cấu hình thành công!");
      setTimeout(() => setSaveMessage(""), 3000);
    } catch (e) {
      console.error(e);
      setSaveMessage("Lỗi khi lưu cấu hình!");
      setTimeout(() => setSaveMessage(""), 3000);
    } finally {
      setIsSaving(false);
    }
  };

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
                <select 
                  value={visionModel}
                  onChange={(e) => setVisionModel(e.target.value)}
                  className="bg-[#171719] border border-white/10 text-zinc-200 rounded-lg px-3 py-1.5 text-[14px] outline-none"
                >
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
                <select 
                  value={llmEngine}
                  onChange={(e) => setLlmEngine(e.target.value)}
                  className="bg-[#171719] border border-white/10 text-zinc-200 rounded-lg px-3 py-1.5 text-[14px] outline-none"
                >
                  <option>Gemini 3.1 Flash Lite</option>
                  <option>Colab / Ngrok LoRA</option>
                  <option>Local Qwen 2.5</option>
                </select>
              </label>
              <label className="flex items-center justify-between mt-3">
                <span className="text-[14px] text-zinc-400">Top-K Chunks (ChromaDB)</span>
                <input 
                  type="number" 
                  value={topK}
                  onChange={(e) => setTopK(e.target.value)}
                  className="bg-[#171719] border border-white/10 text-zinc-200 rounded-lg px-3 py-1.5 text-[14px] outline-none w-20 text-center" 
                />
              </label>
            </div>
          </div>
        </div>

        <div className="mt-8 flex items-center gap-4">
          <button 
            onClick={handleSave}
            disabled={isSaving}
            className="flex items-center gap-2 bg-[#ff4f1d] hover:bg-[#ff6a42] text-white px-6 py-2.5 rounded-xl font-medium transition-colors disabled:opacity-50"
          >
            <Save className="w-5 h-5" />
            {isSaving ? "Đang lưu..." : "Lưu Cấu Hình"}
          </button>
          {saveMessage && (
            <span className={`text-[14px] ${saveMessage.includes("Lỗi") ? "text-red-400" : "text-green-400"}`}>
              {saveMessage}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
