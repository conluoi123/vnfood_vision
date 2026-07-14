import React from "react";
import { motion, AnimatePresence } from "motion/react";
import { Volume2, Mic, Send } from "lucide-react";
import { Message, DishData, IngredientRow } from "../types";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

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
    <div className="flex flex-col gap-4 h-full pr-1 custom-scrollbar">
      <div className="flex items-center justify-between">
        <h2 className="text-[13px] font-bold uppercase tracking-widest text-[#ff4f1d] font-mono">
          AI Assistant
        </h2>
        
        {/* Optional RAG inspector toggle */}
        <button
          onClick={() => setShowRagInspector(!showRagInspector)}
          className="text-[11px] text-zinc-500 hover:text-[#ff4f1d] font-mono uppercase transition-colors"
        >
          {showRagInspector ? "Hide Sources" : "Show RAG"}
        </button>
      </div>

      {/* Chat main canvas box */}
      <div className="bg-transparent flex-1 flex flex-col min-h-[480px]">
        
        {/* Chat thread box */}
        <div className="flex-1 overflow-y-auto space-y-6 pr-2 mb-4 scrollbar-thin">
          <AnimatePresence initial={false}>
            {messages.map((msg, index) => {
              if (msg.role === "user") {
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 15, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ type: "spring", stiffness: 400, damping: 25 }}
                    className="flex flex-col items-end"
                  >
                    <div className="max-w-[80%] bg-zinc-100 text-zinc-950 px-5 py-3 rounded-2xl rounded-tr-sm text-[15px] leading-relaxed shadow-sm font-sans font-medium">
                      {msg.content}
                    </div>
                  </motion.div>
                );
              }

              // Assistant Message
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 15, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ type: "spring", stiffness: 400, damping: 25 }}
                  className="flex flex-col gap-3"
                >
                  <div className="flex items-start gap-4 max-w-[95%]">
                    {/* Minimalist AI Icon */}
                    <div className="w-6 h-6 rounded-md bg-[#ff4f1d] flex items-center justify-center flex-shrink-0 mt-0.5">
                      <div className="w-2 h-2 bg-white rounded-sm animate-pulse" />
                    </div>

                    <div className="flex-1 flex flex-col gap-3">
                      <div className="text-zinc-200 text-[15px] md:text-[16px] leading-relaxed font-sans">
                        <ReactMarkdown 
                          remarkPlugins={[remarkGfm]}
                          components={{
                            strong: ({node, ...props}) => <strong className="text-zinc-100 font-bold" {...props}/>,
                            ul: ({node, ...props}) => <ul className="list-disc pl-4 space-y-1 my-2" {...props}/>,
                            ol: ({node, ...props}) => <ol className="list-decimal pl-4 space-y-1 my-2" {...props}/>,
                            p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props}/>,
                            a: ({node, ...props}) => <a className="text-[#ff4f1d] hover:underline" {...props}/>,
                            table: ({node, ...props}) => <div className="overflow-x-auto my-2"><table className="w-full text-left border-collapse" {...props}/></div>,
                            th: ({node, ...props}) => <th className="border-b border-white/10 py-2 font-medium text-zinc-300" {...props}/>,
                            td: ({node, ...props}) => <td className="border-b border-white/5 py-2 text-zinc-200" {...props}/>,
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      </div>

                      {/* Render Key Ingredients Table ONLY for the very first welcome message */}
                      {index === 0 && msg.content.includes("Công nghệ nhận diện AI") === false && !msg.content.includes("This is") === false && (
                        <div className="mt-2 bg-zinc-900/30 border border-white/5 rounded-xl overflow-hidden p-4 flex flex-col gap-3">
                          <div className="grid grid-cols-2 pb-2 border-b border-white/10 text-[10px] font-medium tracking-widest uppercase text-zinc-500">
                            <span>Ingredient</span>
                            <span>Purpose</span>
                          </div>
                          <div className="text-[12px] text-zinc-300 space-y-3">
                            {currentIngredients.map((row, rIdx) => (
                              <div key={rIdx} className="grid grid-cols-2 items-start gap-4">
                                <span className="font-medium text-zinc-200">{row.name}</span>
                                <span className="text-zinc-500 leading-snug">{row.purpose}</span>
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
                          ? "text-[#ff4f1d] bg-[#ff4f1d]/10" 
                          : "text-zinc-600 hover:text-zinc-300"
                      }`}
                    >
                      <Volume2 className="w-4 h-4" />
                    </button>
                  </div>

                  {/* RAG sources drawer if active */}
                  {showRagInspector && msg.retrievedChunks && msg.retrievedChunks.length > 0 && (
                    <div className="ml-10 mt-1 bg-zinc-950 border border-white/5 p-4 rounded-xl flex flex-col gap-3">
                      <span className="text-[10px] font-medium text-zinc-500 uppercase tracking-widest">
                        Retrieved Context
                      </span>
                      {msg.retrievedChunks.map((c, ci) => (
                        <div key={ci} className="text-[12px] text-zinc-400 bg-zinc-900/50 p-3 rounded-lg border border-white/5 leading-relaxed">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-mono text-[10px] text-zinc-500">{c.source}</span>
                            {c.simScore !== undefined && (
                              <span className="font-mono text-[10px] text-[#ff4f1d]">
                                MATCH: {Math.round(c.simScore * 100)}%
                              </span>
                            )}
                          </div>
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
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-4 max-w-[80%]"
              >
                <div className="w-6 h-6 rounded-md bg-zinc-800 flex items-center justify-center">
                  <div className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-pulse" />
                </div>
                <div className="flex items-center gap-1.5 h-8">
                  <span className="w-1.5 h-1.5 bg-zinc-600 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-1.5 h-1.5 bg-zinc-600 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-1.5 h-1.5 bg-zinc-600 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div ref={chatEndRef as any} />
        </div>

        {/* Bottom Form Action Area */}
        <div className="space-y-3 pt-4 border-t border-white/10 relative z-10 bg-[#000000]">
          {/* Horizontal sliding chip container */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 max-w-full [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
            {/* Find Nearby Restaurant button – always shown when dish is identified */}
            {selectedDish && (
              <button
                onClick={() => handleFindNearby(selectedDish.foodName)}
                disabled={isScanning}
                className="flex-none bg-[#ff4f1d]/10 hover:bg-[#ff4f1d]/20 border border-transparent text-[#ff4f1d] px-4 py-2 rounded-full text-[12px] font-medium transition-all active:scale-95 disabled:opacity-50"
              >
                Find nearby {selectedDish.foodName}
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
                className="flex-none bg-zinc-900 hover:bg-zinc-800 text-zinc-300 px-4 py-2 rounded-full text-[12px] font-medium transition-all active:scale-95 disabled:opacity-50"
              >
                {prompt.replace(/[📍🥗🌿🥒🍯🥩🍜☕🍫🥚🇬🇧]/g, "").trim()}
              </button>
            ))}
          </div>

          {/* Minimally styled input box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage(inputValue);
            }}
            className="relative flex items-center bg-zinc-900/50 border border-white/10 focus-within:border-white/30 focus-within:bg-zinc-900 rounded-2xl p-1 transition-all duration-300"
          >
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask anything..."
              disabled={isScanning}
              className="flex-1 bg-transparent border-0 outline-none px-4 py-2.5 text-[13px] text-zinc-100 placeholder-zinc-500 disabled:opacity-50"
            />
            
            <button
              type="button"
              onClick={handleVoiceInput}
              disabled={isScanning}
              className={`p-2.5 mr-1 rounded-xl flex items-center justify-center transition-all ${
                isListening
                  ? "text-[#ff4f1d] animate-pulse"
                  : "text-zinc-500 hover:text-zinc-300"
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
                  ? "bg-[#ff4f1d] text-white shadow-sm"
                  : "bg-transparent text-zinc-600 cursor-not-allowed"
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
