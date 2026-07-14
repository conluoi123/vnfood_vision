import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from "recharts";
import { Activity, Database, Server, Clock } from "lucide-react";

interface LogEntry {
  timestamp: string;
  type: string;
  data: any;
}

const mockTrainingData = [
  { epoch: 1, loss: 1.2, accuracy: 45 },
  { epoch: 5, loss: 0.8, accuracy: 65 },
  { epoch: 10, loss: 0.5, accuracy: 82 },
  { epoch: 15, loss: 0.3, accuracy: 91 },
  { epoch: 20, loss: 0.15, accuracy: 96 },
];

export default function AnalyticsView() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/rag/logs")
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) setLogs(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch logs", err);
        setLoading(false);
      });
  }, []);

  const totalPredictions = logs.filter(l => l.type === "prediction").length;
  const totalRAG = logs.filter(l => l.type === "rag_query").length;

  return (
    <div className="flex-1 min-h-0 w-full p-4 md:p-8 overflow-y-auto">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <div>
          <h2 className="text-3xl font-bold text-zinc-100 flex items-center gap-3">
            <Activity className="w-8 h-8 text-[#ff4f1d]" />
            System Analytics
          </h2>
          <p className="text-zinc-400 mt-2 text-[15px]">Giám sát thông số huấn luyện mô hình và nhật ký hoạt động hệ thống.</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-zinc-900/50 border border-white/10 p-6 rounded-2xl">
            <div className="flex items-center gap-3 text-zinc-400 mb-2">
              <Server className="w-5 h-5 text-emerald-400" /> API Status
            </div>
            <div className="text-3xl font-bold text-zinc-100">Healthy</div>
          </div>
          <div className="bg-zinc-900/50 border border-white/10 p-6 rounded-2xl">
            <div className="flex items-center gap-3 text-zinc-400 mb-2">
              <Database className="w-5 h-5 text-blue-400" /> Vector DB
            </div>
            <div className="text-3xl font-bold text-zinc-100">27K Docs</div>
          </div>
          <div className="bg-zinc-900/50 border border-white/10 p-6 rounded-2xl">
            <div className="flex items-center gap-3 text-zinc-400 mb-2">
              <Activity className="w-5 h-5 text-[#ff4f1d]" /> Predictions
            </div>
            <div className="text-3xl font-bold text-zinc-100">{totalPredictions}</div>
          </div>
          <div className="bg-zinc-900/50 border border-white/10 p-6 rounded-2xl">
            <div className="flex items-center gap-3 text-zinc-400 mb-2">
              <Clock className="w-5 h-5 text-purple-400" /> RAG Queries
            </div>
            <div className="text-3xl font-bold text-zinc-100">{totalRAG}</div>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-zinc-900/50 border border-white/10 p-6 rounded-2xl">
            <h3 className="text-xl font-semibold text-zinc-200 mb-6">Model Training Progress</h3>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={mockTrainingData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="epoch" stroke="#888" />
                  <YAxis yAxisId="left" stroke="#888" />
                  <YAxis yAxisId="right" orientation="right" stroke="#888" />
                  <Tooltip contentStyle={{ backgroundColor: '#18181b', border: '1px solid #333' }} />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="loss" stroke="#ff4f1d" name="Loss" />
                  <Line yAxisId="right" type="monotone" dataKey="accuracy" stroke="#10b981" name="Accuracy (%)" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* System Logs */}
          <div className="bg-zinc-900/50 border border-white/10 p-6 rounded-2xl flex flex-col">
            <h3 className="text-xl font-semibold text-zinc-200 mb-6">Live System Logs</h3>
            <div className="flex-1 bg-black/40 rounded-xl border border-white/5 p-4 overflow-y-auto max-h-[300px]">
              {loading ? (
                <div className="text-zinc-500 text-center mt-10">Loading logs...</div>
              ) : logs.length === 0 ? (
                <div className="text-zinc-500 text-center mt-10">No logs yet. Try predicting a food!</div>
              ) : (
                <div className="space-y-3">
                  {logs.map((log, idx) => (
                    <div key={idx} className="flex gap-3 text-sm font-mono items-start">
                      <span className="text-zinc-500 min-w-[70px]">
                        {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                        log.type === "prediction" ? "bg-blue-500/20 text-blue-400" : "bg-purple-500/20 text-purple-400"
                      }`}>
                        {log.type.toUpperCase()}
                      </span>
                      <span className="text-zinc-300">
                        {log.type === "prediction" 
                          ? `Analyzed image: ${log.data.foodName} (${log.data.confidence}%)`
                          : `RAG Query: "${log.data.query}"`}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
