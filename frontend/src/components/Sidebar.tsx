import React from "react";
import { LayoutDashboard, History, Settings, User, Activity } from "lucide-react";

export type TabType = "trang-chu" | "history" | "analytics" | "settings";

interface SidebarProps {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
}

export default function Sidebar({ activeTab, setActiveTab }: SidebarProps) {
  const tabs = [
    { id: "trang-chu" as TabType, label: "Trang Chủ", icon: LayoutDashboard },
    { id: "history" as TabType, label: "Lịch sử", icon: History },
    { id: "analytics" as TabType, label: "Thống kê", icon: Activity },
    { id: "settings" as TabType, label: "Cấu hình", icon: Settings },
  ];

  return (
    <aside className="w-20 md:w-64 bg-[#0a0a0b]/90 border-r border-[#1e1e21]/80 backdrop-blur-md flex flex-col justify-between py-6 h-full transition-all duration-300 z-40">
      <div className="flex flex-col gap-2 px-3">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-4 px-4 py-3.5 rounded-xl transition-all duration-200 group ${
                isActive
                  ? "bg-[#ff4f1d]/10 text-[#ff4f1d] shadow-[inset_4px_0_0_#ff4f1d]"
                  : "text-zinc-500 hover:text-zinc-200 hover:bg-[#171719]"
              }`}
            >
              <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? "text-[#ff4f1d]" : "text-zinc-500 group-hover:text-zinc-300"}`} />
              <span className={`text-[14px] font-medium hidden md:block whitespace-nowrap ${isActive ? "text-zinc-100" : ""}`}>
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>

      <div className="px-3 pb-2 hidden md:block">
        <div className="bg-[#171719] border border-[#232326] p-4 rounded-xl flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-zinc-800 flex items-center justify-center flex-shrink-0">
            <User className="w-5 h-5 text-zinc-400" />
          </div>
          <div className="flex flex-col overflow-hidden">
            <span className="text-[13px] font-bold text-zinc-200 truncate">Hội Đồng Demo</span>
            <span className="text-[11px] text-[#ff4f1d] truncate">Admin</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
