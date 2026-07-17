import React, { useState } from "react";
import Header from "./components/Header";
import DishSelector from "./components/DishSelector";
import ImagePreview from "./components/ImagePreview";
import NutritionPanel from "./components/NutritionPanel";
import ChatInterface from "./components/ChatInterface";
import Sidebar, { TabType } from "./components/Sidebar";
import HistoryView from "./components/HistoryView";
import SettingsView from "./components/SettingsView";
import AnalyticsView from "./components/AnalyticsView";
import { useAppLogic } from "./hooks/useAppLogic";
import { HelpCircle } from "lucide-react";
import { Heart } from "lucide-react";

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>("workspace");
  const [historyKey, setHistoryKey] = useState(0);

  const {
    activeDishKey, setActiveDishKey,
    selectedDish, customImage,
    isScanning, showGradCam, setShowGradCam,
    isListening, isNutritionLoading,
    showRagInspector, setShowRagInspector,
    language, setLanguage,
    messages, inputValue, setInputValue,
    isTyping, isSpeaking,
    chatEndRef, fileInputRef,
    getCoordinates, handleTTS, handleVoiceInput,
    handleFileUpload, triggerUploadClick,
    handleFindNearby, handleSendMessage, handleClearChat,
    getNutrition, getIngredients,
    restoreHistorySession
  } = useAppLogic();

  const currentNutrition = getNutrition();
  const currentIngredients = getIngredients();

  return (
    <div className="relative h-screen bg-[#0d0d0e] text-[#f4f4f5] overflow-hidden font-sans flex flex-row">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={(tab) => {
          if (tab === "history") setHistoryKey(k => k + 1);
          setActiveTab(tab);
        }}
      />
      
      <div className="flex-1 flex flex-col h-full min-w-0 relative overflow-hidden">
        {/* 🌌 Atmospheric Radial Glowing Orbs for that gorgeous premium visual aesthetic */}
        <div className="absolute top-[-5%] left-[-10%] w-[45%] h-[45%] rounded-full bg-[#ff4f1d]/5 blur-[120px] pointer-events-none animate-pulse-glow" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-[#ff4f1d]/5 blur-[140px] pointer-events-none animate-pulse-glow" style={{ animationDelay: "3s" }} />

        {/* 🏷️ VNFood Vision Premium Header */}
        <Header language={language} setLanguage={setLanguage} />

        {activeTab === "workspace" && (
          <>
            {/* Quick Dish Selection Pills */}
            <DishSelector 
              activeDishKey={activeDishKey}
              setActiveDishKey={setActiveDishKey}
              isScanning={isScanning}
              customImage={customImage}
              triggerUploadClick={triggerUploadClick}
            />

            {/* 🚀 MAIN GRID WORKSPACE */}
            <main className="flex-1 min-h-0 max-w-7xl w-full mx-auto p-4 md:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
              
              {/* 📸 COLUMN 1: VISION & DISCOVERY ZONE (lg:col-span-5, ~40%) */}
              <div className="lg:col-span-5 flex flex-col gap-4 h-full overflow-y-auto pr-1 custom-scrollbar">
                <div className="flex items-center justify-between">
                  <h2 className="text-[14px] font-bold uppercase tracking-widest text-[#ff4f1d] font-mono">
                    Vision & Discovery Zone
                  </h2>
                  {selectedDish && !isScanning && (
                    <span className="text-[12px] font-medium text-[#ff4f1d]/80 font-mono">
                      {selectedDish.confidence}% CONFIDENCE
                    </span>
                  )}
                </div>

                <ImagePreview 
                  selectedDish={selectedDish}
                  isScanning={isScanning}
                  customImage={customImage}
                  activeDishKey={activeDishKey}
                  showGradCam={showGradCam}
                  setShowGradCam={setShowGradCam}
                  coordinates={getCoordinates()}
                  triggerUploadClick={triggerUploadClick}
                  fileInputRef={fileInputRef}
                  handleFileUpload={handleFileUpload}
                />

                <NutritionPanel 
                  currentNutrition={currentNutrition}
                  currentIngredients={currentIngredients}
                  isNutritionLoading={isNutritionLoading}
                  activeDishKey={activeDishKey}
                />
              </div>

              {/* 🤖 COLUMN 2: CHEF AI ASSISTANT (lg:col-span-7, ~60%) */}
              <div className="lg:col-span-7 h-full flex flex-col min-h-0">
                <ChatInterface 
                  messages={messages}
                  isTyping={isTyping}
                  isSpeaking={isSpeaking}
                  showRagInspector={showRagInspector}
                  setShowRagInspector={setShowRagInspector}
                  currentIngredients={currentIngredients}
                  handleTTS={handleTTS}
                  chatEndRef={chatEndRef}
                  selectedDish={selectedDish}
                  isScanning={isScanning}
                  handleFindNearby={handleFindNearby}
                  handleSendMessage={handleSendMessage}
                  handleClearChat={handleClearChat}
                  inputValue={inputValue}
                  setInputValue={setInputValue}
                  isListening={isListening}
                  handleVoiceInput={handleVoiceInput}
                  language={language}
                />
              </div>
            </main>
          </>
        )}

        {activeTab === "history" && (
          <HistoryView
            key={historyKey}
            onSelectHistoryItem={(item) => {
              restoreHistorySession(item);
              setActiveTab("workspace");
            }}
          />
        )}
        {activeTab === "analytics" && <AnalyticsView />}
        {activeTab === "settings" && <SettingsView />}

        {/* Sleek footer indicator */}
        <footer className="w-full text-center py-4 bg-[#0a0a0b] border-t border-[#18181a] mt-auto text-[11px] font-mono text-zinc-400 uppercase tracking-widest relative z-10 flex items-center justify-center gap-3">
          <div className="flex items-center gap-1.5">
            <Heart className="w-4 h-4 text-[#ff4f1d] fill-[#ff4f1d]" />
            <span>VNFood Vision © 2026</span>
          </div>
          <span>•</span>
          <span>Premium AI Culinary Assistant</span>
        </footer>

        {/* Floating help / question-mark circle in the absolute bottom right matching reference exactly! */}
        <div className="fixed bottom-4 right-4 z-50">
          <button 
            onClick={() => {
              setActiveTab("workspace");
              setTimeout(() => handleSendMessage("Giới thiệu về VNFood Vision"), 100);
            }}
            className="w-10 h-10 rounded-full bg-[#171719] hover:bg-[#202023] border border-[#242427] flex items-center justify-center text-zinc-400 hover:text-[#ff4f1d] transition-all shadow-xl active:scale-90"
            title="Hỗ trợ & Hướng dẫn"
          >
            <HelpCircle className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
