import React from "react";
import { motion, AnimatePresence } from "motion/react";
import { Volume2, Mic, Send } from "lucide-react";
import { Message, DishData, IngredientRow } from "../types";

interface ChatInterfaceProps {
  messages: Message[];
  isTyping: boolean;
  isSpeaking: boolean;
  showRagInspector: boolean;
  setShowRagInspector: (show: boolean) => void;
  currentIngredients: IngredientRow[];
  handleTTS: (text: string) => void;
  chatEndRef: React.RefObject<HTMLDivElement | null>;
  selectedDish: DishData | null;
  isScanning: boolean;
  handleFindNearby: (foodName: string) => void;
  handleSendMessage: (message: string) => void;
  inputValue: string;
  setInputValue: (value: string) => void;
  isListening: boolean;
  handleVoiceInput: () => void;
  language: "VN" | "EN";
}

export default function ChatInterface({
  messages,
  isTyping,
  isSpeaking,
  showRagInspector,
  setShowRagInspector,
  currentIngredients,
  handleTTS,
  chatEndRef,
  selectedDish,
  isScanning,
  handleFindNearby,
  handleSendMessage,
  inputValue,
  setInputValue,
  isListening,
  handleVoiceInput,
  language
}: ChatInterfaceProps) {
  return (
    <div className="lg:col-span-6 flex flex-col gap-4 h-full overflow-y-auto pr-1 custom-scrollbar">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold uppercase tracking-wider text-[#ff4f1d] font-display">
          Chef AI Assistant
        </h2>
        
        {/* Optional RAG inspector toggle */}
        <button
          onClick={() => setShowRagInspector(!showRagInspector)}
          className="text-[11px] text-zinc-400 hover:text-[#ff4f1d] font-bold uppercase transition-colors"
        >
          {showRagInspector ? "Hide Sources" : "Show RAG Sources"}
        </button>
      </div>

      {/* Chat main canvas box */}
      <div className="bg-[#121111] border border-[#222124] rounded-3xl p-4 md:p-5 flex-1 flex flex-col shadow-2xl overflow-hidden min-h-[480px]">
        
        {/* Chat thread box */}
        <div className="flex-1 overflow-y-auto space-y-4 pr-1 mb-4 scrollbar-thin">
          <AnimatePresence initial={false}>
            {messages.map((msg, index) => {
              if (msg.role === "user") {
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex flex-col items-end"
                  >
                    <div className="max-w-[85%] bg-[#242426] text-white px-4 py-3 rounded-2xl rounded-tr-none text-xs md:text-sm leading-relaxed shadow-sm font-sans">
                      {msg.content}
                    </div>
                  </motion.div>
                );
              }

              // Assistant Message
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex flex-col gap-3.5"
                >
                  <div className="flex items-start gap-3 max-w-[95%]">
                    {/* Chef Orange Circle avatar */}
                    <div className="w-8 h-8 rounded-full bg-[#ff4f1d] flex items-center justify-center text-white flex-shrink-0 shadow-lg shadow-[#ff4f1d]/20 border border-[#ff4f1d]/30 text-xs">
                      🍴
                    </div>

                    <div className="flex-1 flex flex-col gap-3.5">
                      <div className="bg-transparent text-zinc-200 text-xs md:text-sm leading-relaxed font-sans whitespace-pre-wrap">
                        {/* Parse markdown nicely */}
                        {msg.content.split("**").map((part, i) => 
                          i % 2 === 1 ? <strong key={i} className="text-[#ff4f1d] font-black">{part}</strong> : part
                        )}
                      </div>

                      {/* Render Key Ingredients Table ONLY for the very first welcome message */}
                      {index === 0 && msg.content.includes("Công nghệ nhận diện AI") === false && !msg.content.includes("This is") === false && (
                        <div className="mt-2 bg-[#171719] border border-[#242427] rounded-xl overflow-hidden p-4 flex flex-col gap-2.5">
                          <div className="grid grid-cols-2 pb-2 border-b border-[#28282b] text-[11px] font-bold tracking-wider uppercase">
                            <span className="text-[#ff4f1d]">Key Ingredients</span>
                            <span className="text-[#ff4f1d]">Purpose</span>
                          </div>
                          <div className="divide-y divide-[#242427]/50 text-xs text-zinc-300 space-y-2">
                            {currentIngredients.map((row, rIdx) => (
                              <div key={rIdx} className="grid grid-cols-2 pt-2 first:pt-0 items-center">
                                <span className="font-semibold text-zinc-100">{row.name}</span>
                                <span className="text-zinc-400">{row.purpose}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* TTS speaker button */}
                    <button
                      onClick={() => handleTTS(msg.content)}
                      className={`p-2 rounded-full hover:scale-105 active:scale-95 transition-all flex-shrink-0 ${
                        isSpeaking 
                          ? "bg-[#ff4f1d]/20 text-[#ff4f1d] border border-[#ff4f1d]/40" 
                          : "bg-[#18181a] hover:bg-[#202023] text-zinc-400 border border-[#232326]"
                      }`}
                      title="Đọc văn bản AI"
                    >
                      <Volume2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  {/* RAG sources drawer if active */}
                  {showRagInspector && msg.retrievedChunks && msg.retrievedChunks.length > 0 && (
                    <div className="ml-11 mt-1 bg-[#0f0f10] border border-zinc-800 p-3 rounded-xl flex flex-col gap-2">
                      <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">
                        RAG Retrieved Knowledge:
                      </span>
                      {msg.retrievedChunks.map((c, ci) => (
                        <div key={ci} className="text-[11px] text-zinc-400 bg-[#161618] p-2 rounded border border-zinc-900">
                          <span className="font-bold text-[#ff4f1d] flex items-center justify-between mb-1">
                            <span>Source: {c.source}</span>
                            {c.simScore !== undefined && (
                              <span className="bg-[#ff4f1d]/20 text-[#ff4f1d] px-1.5 py-0.5 rounded text-[9px]">
                                Match: {Math.round(c.simScore * 100)}%
                              </span>
                            )}
                          </span>
                          "{c.content}"
                        </div>
                      ))}
                    </div>
                  )}
                </motion.div>
              );
            })}

            {isTyping && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-2 max-w-[80%]"
              >
                <div className="w-8 h-8 rounded-full bg-[#ff4f1d] flex items-center justify-center text-white text-xs">
                  🍳
                </div>
                <div className="bg-[#1a1a1c] px-4 py-2.5 rounded-2xl flex items-center gap-1 border border-zinc-800">
                  <span className="w-1.5 h-1.5 bg-[#ff4f1d] rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-1.5 h-1.5 bg-[#ff4f1d] rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-1.5 h-1.5 bg-[#ff4f1d] rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div ref={chatEndRef as any} />
        </div>

        {/* Bottom Form Action Area */}
        <div className="space-y-3 pt-3 border-t border-[#1e1e21]">
          {/* Horizontal sliding chip container */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 max-w-full">
            {/* Find Nearby Restaurant button – always shown when dish is identified */}
            {selectedDish && (
              <button
                onClick={() => handleFindNearby(selectedDish.foodName)}
                disabled={isScanning}
                className="flex-none bg-[#ff4f1d]/10 hover:bg-[#ff4f1d]/20 border border-[#ff4f1d]/40 hover:border-[#ff4f1d]/80 text-[#ff4f1d] px-3.5 py-2 rounded-xl text-[11px] font-bold flex items-center transition-all shadow-sm active:scale-95 disabled:opacity-50"
              >
                <span>Tim quan {selectedDish.foodName} gan day</span>
              </button>
            )}

            {selectedDish?.prompts.map((prompt, pIdx) => (
              <button
                key={pIdx}
                onClick={() => {
                  if (prompt.startsWith("📍") || prompt.toLowerCase().startsWith("quan") || prompt.toLowerCase().startsWith("tim")) {
                    handleFindNearby(selectedDish?.foodName || "");
                  } else {
                    handleSendMessage(prompt);
                  }
                }}
                disabled={isScanning}
                className="flex-none bg-[#171719] hover:bg-[#202023] hover:border-[#ff4f1d]/50 text-zinc-300 border border-[#242427] px-3.5 py-2 rounded-xl text-[11px] font-semibold flex items-center transition-all shadow-sm active:scale-95 disabled:opacity-50"
              >
                <span>{prompt.replace(/[📍🥗🌿🥒🍯🥩🍜☕🍫🥚🇬🇧]/g, "").trim()}</span>
              </button>
            ))}
          </div>

          {/* Minimally styled input box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage(inputValue);
            }}
            className="relative flex items-center bg-[#171719] border border-[#242427] focus-within:border-[#ff4f1d]/80 rounded-2xl p-1 transition-all"
          >
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask me anything about this recipe or search..."
              disabled={isScanning}
              className="flex-1 bg-transparent border-0 outline-none px-4 py-2.5 text-xs md:text-sm text-zinc-100 placeholder-zinc-500 disabled:opacity-50"
            />
            
            <button
              type="button"
              onClick={handleVoiceInput}
              disabled={isScanning}
              className={`p-2.5 mr-1 rounded-xl flex items-center justify-center transition-all ${
                isListening
                  ? "bg-[#ff4f1d]/20 text-[#ff4f1d] animate-pulse"
                  : "text-zinc-500 hover:text-zinc-300 hover:bg-[#202022]"
              }`}
              title={language === "VN" ? "Nhập bằng giọng nói" : "Voice input"}
            >
              <Mic className="w-4 h-4" />
            </button>

            <button
              type="submit"
              disabled={!inputValue.trim() || isScanning}
              className={`p-2.5 rounded-xl flex items-center justify-center transition-all ${
                inputValue.trim() && !isScanning
                  ? "bg-[#ff4f1d] text-white shadow-lg shadow-[#ff4f1d]/20 hover:scale-103"
                  : "bg-[#202022] text-zinc-600 cursor-not-allowed"
              }`}
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
