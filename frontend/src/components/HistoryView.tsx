import React from "react";
import { Clock } from "lucide-react";

export default function HistoryView() {
  return (
    <div className="flex-1 min-h-0 w-full p-4 md:p-8 overflow-y-auto">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold text-zinc-100 mb-6 flex items-center gap-3">
          <Clock className="w-6 h-6 text-[#ff4f1d]" />
          Lịch sử phân tích
        </h2>
        <div className="bg-zinc-900/40 border border-white/5 rounded-2xl p-8 flex flex-col items-center justify-center min-h-[400px]">
          <Clock className="w-12 h-12 text-zinc-700 mb-4" />
          <p className="text-zinc-400 text-[15px]">Bạn chưa phân tích món ăn nào trong phiên này.</p>
        </div>
      </div>
    </div>
  );
}
