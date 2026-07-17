import React, { useState, useEffect } from "react";
import { Clock, Trash2, Loader2, X, AlertTriangle } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { ScanHistoryItem } from "../types";
import { getHistoryAPI, clearHistoryAPI, deleteHistoryItemAPI } from "../services/api";

interface HistoryViewProps {
  onSelectHistoryItem?: (item: ScanHistoryItem) => void;
}

export default function HistoryView({ onSelectHistoryItem }: HistoryViewProps) {
  const [history, setHistory] = useState<ScanHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Custom Confirm Dialog State
  const [confirmDialog, setConfirmDialog] = useState<{
    isOpen: boolean;
    title: string;
    description: string;
    onConfirm: () => void;
  } | null>(null);

  useEffect(() => {
    getHistoryAPI()
      .then(data => {
        if (Array.isArray(data)) {
          setHistory(data);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const clearHistory = () => {
    setConfirmDialog({
      isOpen: true,
      title: "Xóa toàn bộ lịch sử",
      description: "Bạn có chắc chắn muốn xóa tất cả lịch sử phân tích không? Hành động này không thể hoàn tác.",
      onConfirm: async () => {
        try {
          await clearHistoryAPI();
          setHistory([]);
          setConfirmDialog(null);
        } catch (e) {
          alert("Lỗi khi xóa lịch sử trên server.");
        }
      }
    });
  };

  const deleteItem = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setConfirmDialog({
      isOpen: true,
      title: "Xóa bản ghi này",
      description: "Bạn có chắc chắn muốn xóa bản ghi lịch sử này không?",
      onConfirm: async () => {
        try {
          await deleteHistoryItemAPI(id);
          setHistory(prev => prev.filter(item => item.id !== id));
          setConfirmDialog(null);
        } catch (e) {
          alert("Lỗi khi xóa lịch sử.");
        }
      }
    });
  };

  return (
    <div className="flex-1 min-h-0 w-full p-4 md:p-8 overflow-y-auto custom-scrollbar">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-zinc-100 flex items-center gap-3">
            <Clock className="w-6 h-6 text-[#ff4f1d]" />
            Lịch sử phân tích
          </h2>
          {history.length > 0 && (
            <button
              onClick={clearHistory}
              className="flex items-center gap-2 text-[13px] text-zinc-400 hover:text-red-400 transition-colors bg-zinc-900/50 hover:bg-zinc-800 px-3 py-1.5 rounded-lg border border-white/5"
            >
              <Trash2 className="w-4 h-4" />
              Xóa lịch sử
            </button>
          )}
        </div>
        
        
        {loading ? (
          <div className="bg-zinc-900/40 border border-white/5 rounded-2xl p-8 flex flex-col items-center justify-center min-h-[400px]">
            <Loader2 className="w-8 h-8 text-[#ff4f1d] animate-spin mb-4" />
            <p className="text-zinc-400 text-[15px]">Đang tải lịch sử từ máy chủ...</p>
          </div>
        ) : history.length === 0 ? (
          <div className="bg-zinc-900/40 border border-white/5 rounded-2xl p-8 flex flex-col items-center justify-center min-h-[400px]">
            <Clock className="w-12 h-12 text-zinc-700 mb-4" />
            <p className="text-zinc-400 text-[15px]">Bạn chưa tải lên bức ảnh nào trong phiên làm việc này.</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {history.map((item) => (
              <div 
                key={item.id} 
                onClick={() => onSelectHistoryItem?.(item)}
                className="relative cursor-pointer bg-zinc-900/40 border border-white/5 rounded-2xl overflow-hidden group hover:border-[#ff4f1d]/30 hover:shadow-[0_0_15px_rgba(255,79,29,0.15)] transition-all duration-300 flex flex-col"
              >
                {/* Delete single item button */}
                <button
                  onClick={(e) => deleteItem(e, item.id)}
                  className="absolute top-2 right-2 z-10 bg-black/60 hover:bg-red-500/80 backdrop-blur-md p-1.5 rounded-full text-zinc-300 hover:text-white opacity-0 group-hover:opacity-100 transition-all duration-200"
                  title="Xóa lịch sử này"
                >
                  <X className="w-4 h-4" />
                </button>

                <div className="aspect-square w-full relative overflow-hidden bg-black/50">
                  <img 
                    src={item.image} 
                    alt={item.foodName} 
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                </div>
                <div className="p-3 flex flex-col gap-1">
                  <span className="text-sm font-bold text-zinc-200 line-clamp-1">{item.foodName}</span>
                  <span className="text-[10px] text-zinc-500 font-mono">
                    {new Date(item.date).toLocaleString('vi-VN')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Custom Confirm Modal */}
      <AnimatePresence>
        {confirmDialog?.isOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setConfirmDialog(null)}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="relative w-full max-w-sm bg-zinc-900 border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
            >
              <div className="p-6">
                <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center mb-4">
                  <AlertTriangle className="w-6 h-6 text-red-500" />
                </div>
                <h3 className="text-lg font-bold text-zinc-100 mb-2">
                  {confirmDialog.title}
                </h3>
                <p className="text-zinc-400 text-[14px] leading-relaxed">
                  {confirmDialog.description}
                </p>
              </div>
              <div className="bg-zinc-950/50 px-6 py-4 flex items-center justify-end gap-3 border-t border-white/5">
                <button
                  onClick={() => setConfirmDialog(null)}
                  className="px-4 py-2 text-sm font-medium text-zinc-300 hover:text-white transition-colors"
                >
                  Hủy bỏ
                </button>
                <button
                  onClick={confirmDialog.onConfirm}
                  className="px-4 py-2 text-sm font-medium bg-red-500 hover:bg-red-600 text-white rounded-xl transition-all active:scale-95 shadow-lg shadow-red-500/20"
                >
                  Đồng ý xóa
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
