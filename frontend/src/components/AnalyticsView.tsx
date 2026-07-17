import React, { useEffect, useState } from "react";
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, 
  PieChart, Pie, Cell
} from "recharts";
import { Activity, Flame, Utensils, Award, Loader2 } from "lucide-react";
import { getAnalyticsAPI } from "../services/api";

const PIE_COLORS = ['#ff4f1d', '#3b82f6', '#10b981'];

export default function AnalyticsView() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAnalyticsAPI()
      .then(res => {
        if (res.success) {
          setData(res);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex-1 w-full flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 text-[#ff4f1d] animate-spin" />
          <p className="text-zinc-400">Đang tổng hợp dữ liệu dinh dưỡng...</p>
        </div>
      </div>
    );
  }

  if (!data || data.summary.totalScans === 0) {
    return (
      <div className="flex-1 w-full p-4 md:p-8 flex items-center justify-center">
        <div className="bg-zinc-900/50 border border-white/10 rounded-2xl p-8 flex flex-col items-center max-w-md text-center">
          <Activity className="w-12 h-12 text-zinc-600 mb-4" />
          <h3 className="text-xl font-bold text-zinc-200 mb-2">Chưa có dữ liệu</h3>
          <p className="text-zinc-400">Hãy dùng VNFood Vision để quét nhận diện các món ăn của bạn. Hệ thống sẽ tự động tổng hợp số liệu dinh dưỡng tại đây.</p>
        </div>
      </div>
    );
  }

  const { summary, macros, topDishes, timeline } = data;

  const pieData = [
    { name: 'Protein', value: macros.protein },
    { name: 'Carbs', value: macros.carbs },
    { name: 'Fat', value: macros.fat }
  ];

  return (
    <div className="flex-1 min-h-0 w-full p-4 md:p-8 overflow-y-auto custom-scrollbar">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <div>
          <h2 className="text-3xl font-bold text-zinc-100 flex items-center gap-3">
            <Activity className="w-8 h-8 text-[#ff4f1d]" />
            Bảng điều khiển Dinh dưỡng
          </h2>
          <p className="text-zinc-400 mt-2 text-[15px]">Theo dõi tổng quan thói quen ăn uống và lượng dưỡng chất nạp vào từ các món ăn.</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-zinc-900/40 border border-white/5 hover:border-white/10 transition-colors p-6 rounded-2xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Utensils className="w-16 h-16 text-zinc-100" />
            </div>
            <div className="flex items-center gap-3 text-zinc-400 mb-2 relative z-10">
              <Utensils className="w-5 h-5 text-[#ff4f1d]" /> Món ăn đã phân tích
            </div>
            <div className="text-4xl font-black text-zinc-100 relative z-10 font-mono">
              {summary.totalScans}
            </div>
          </div>

          <div className="bg-zinc-900/40 border border-white/5 hover:border-white/10 transition-colors p-6 rounded-2xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Flame className="w-16 h-16 text-orange-400" />
            </div>
            <div className="flex items-center gap-3 text-zinc-400 mb-2 relative z-10">
              <Flame className="w-5 h-5 text-orange-400" /> Tổng Calo (Kcal)
            </div>
            <div className="text-4xl font-black text-zinc-100 relative z-10 font-mono">
              {summary.totalCalories.toLocaleString()}
            </div>
          </div>

          <div className="bg-zinc-900/40 border border-white/5 hover:border-white/10 transition-colors p-6 rounded-2xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Activity className="w-16 h-16 text-emerald-400" />
            </div>
            <div className="flex items-center gap-3 text-zinc-400 mb-2 relative z-10">
              <Activity className="w-5 h-5 text-emerald-400" /> T.Bình Calo / Món
            </div>
            <div className="text-4xl font-black text-zinc-100 relative z-10 font-mono">
              {summary.avgCalories.toLocaleString()}
            </div>
          </div>

          <div className="bg-zinc-900/40 border border-white/5 hover:border-white/10 transition-colors p-6 rounded-2xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Award className="w-16 h-16 text-purple-400" />
            </div>
            <div className="flex items-center gap-3 text-zinc-400 mb-2 relative z-10">
              <Award className="w-5 h-5 text-purple-400" /> Món ăn yêu thích
            </div>
            <div className="text-2xl font-bold text-zinc-100 relative z-10 mt-1 line-clamp-2">
              {summary.topFood}
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Main Line Chart (Timeline) */}
          <div className="lg:col-span-2 bg-zinc-900/40 border border-white/5 p-6 rounded-3xl">
            <div className="flex flex-col mb-6">
              <h3 className="text-lg font-bold text-zinc-100">Lượng Calo theo thời gian</h3>
              <p className="text-sm text-zinc-500">Thống kê lượng Kcal bạn đã nạp trong các ngày qua</p>
            </div>
            
            <div className="h-[320px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={timeline} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis 
                    dataKey="date" 
                    stroke="#52525b" 
                    tick={{ fill: '#a1a1aa', fontSize: 12 }}
                    tickMargin={10}
                    axisLine={false}
                    tickLine={false}
                    tickFormatter={(val) => val.split('-').slice(1).join('/')}
                  />
                  <YAxis 
                    stroke="#52525b" 
                    tick={{ fill: '#a1a1aa', fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <RechartsTooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(9, 9, 11, 0.9)', 
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '12px',
                      color: '#fff'
                    }}
                    itemStyle={{ color: '#ff4f1d', fontWeight: 'bold' }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="calories" 
                    name="Calo" 
                    stroke="#ff4f1d" 
                    strokeWidth={4}
                    dot={{ fill: '#09090b', stroke: '#ff4f1d', strokeWidth: 2, r: 5 }}
                    activeDot={{ r: 7, fill: '#ff4f1d', stroke: '#09090b' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Side Charts (Pie Macros + Top List) */}
          <div className="lg:col-span-1 flex flex-col gap-6">
            
            {/* Pie Chart Macros */}
            <div className="bg-zinc-900/40 border border-white/5 p-6 rounded-3xl flex flex-col">
              <h3 className="text-lg font-bold text-zinc-100">Tỉ lệ Dinh dưỡng (Macros)</h3>
              <div className="h-[200px] w-full relative mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={85}
                      paddingAngle={5}
                      dataKey="value"
                      stroke="none"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip 
                      contentStyle={{ 
                        backgroundColor: 'rgba(9, 9, 11, 0.9)', 
                        border: '1px solid rgba(255,255,255,0.1)',
                        borderRadius: '8px',
                        color: '#fff'
                      }}
                      itemStyle={{ color: '#fff' }}
                      formatter={(value) => [`${value ?? 0}g`, ' Khối lượng']}
                    />
                  </PieChart>
                </ResponsiveContainer>
                {/* Center text overlay */}
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="text-[10px] text-zinc-500 font-mono tracking-widest uppercase">Macros</span>
                </div>
              </div>
              <div className="flex justify-center gap-4 mt-2">
                {pieData.map((entry, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: PIE_COLORS[idx] }} />
                    <span className="text-[12px] text-zinc-300 font-medium">{entry.name}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Dishes List */}
            <div className="bg-zinc-900/40 border border-white/5 p-6 rounded-3xl flex-1">
              <h3 className="text-lg font-bold text-zinc-100 mb-4">Các món hay ăn</h3>
              <div className="space-y-3">
                {topDishes.map((dish: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between group">
                    <div className="flex items-center gap-3">
                      <div className="w-7 h-7 rounded-full bg-zinc-800 flex items-center justify-center text-[11px] font-bold text-zinc-400 group-hover:bg-[#ff4f1d] group-hover:text-white transition-colors">
                        #{idx + 1}
                      </div>
                      <span className="text-sm text-zinc-200 font-medium line-clamp-1">{dish.name}</span>
                    </div>
                    <span className="text-[12px] text-zinc-500 font-mono bg-black/50 px-2 py-1 rounded">
                      x{dish.count}
                    </span>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}
