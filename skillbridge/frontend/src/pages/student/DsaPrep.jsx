import { useState } from "react";
import { Flame, ExternalLink, CheckCircle2 } from "lucide-react";
import PageHeader from "../../components/PageHeader.jsx";
import Badge from "../../components/Badge.jsx";
import useFetch from "../../hooks/useFetch.js";
import api from "../../services/api.js";

export default function DsaPrep() {
  const [refreshKey, setRefreshKey] = useState(0);
  const { data: roadmap, loading: roadmapLoading } = useFetch(() => api.getDsaRoadmap(), []);
  const { data: progress, loading: progressLoading } = useFetch(() => api.getDsaProgress(), [refreshKey]);
  const { data: next, loading: nextLoading } = useFetch(() => api.getDsaNext(), [refreshKey]);

  const markSolved = async (topic, title, difficulty) => {
    await api.markDsaSolved({ topic, title, difficulty, platform: "LeetCode" });
    setRefreshKey((k) => k + 1);
  };

  return (
    <div>
      <PageHeader title="DSA Preparation" subtitle="Interview-ready problem sets, tracked progress, and a daily streak" />

      {progress && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-xl border border-slate-200 p-4">
            <div className="text-xs text-slate-500">Current Streak</div>
            <div className="text-2xl font-semibold text-slate-900 mt-1 flex items-center gap-1">
              <Flame size={18} className="text-orange-500" /> {progress.current_streak}
            </div>
          </div>
          <div className="bg-white rounded-xl border border-slate-200 p-4">
            <div className="text-xs text-slate-500">Longest Streak</div>
            <div className="text-2xl font-semibold text-slate-900 mt-1">{progress.longest_streak}</div>
          </div>
          <div className="bg-white rounded-xl border border-slate-200 p-4">
            <div className="text-xs text-slate-500">Total Solved</div>
            <div className="text-2xl font-semibold text-slate-900 mt-1">{progress.total_solved}</div>
          </div>
          <div className="bg-white rounded-xl border border-slate-200 p-4">
            <div className="text-xs text-slate-500">Easy / Medium / Hard</div>
            <div className="text-sm font-semibold text-slate-900 mt-2">
              {progress.by_difficulty.Easy} / {progress.by_difficulty.Medium} / {progress.by_difficulty.Hard}
            </div>
          </div>
        </div>
      )}

      {!nextLoading && next && next.length > 0 && (
        <div className="bg-brand-50 border border-brand-100 rounded-xl p-4 mb-6">
          <div className="text-sm font-medium text-brand-900 mb-2">Recommended Next (weakest topic first)</div>
          <div className="flex flex-wrap gap-2">
            {next.map((p) => (
              <div key={p.title} className="bg-white rounded-lg border border-slate-200 px-3 py-2 text-xs flex items-center gap-2">
                <Badge>{p.difficulty}</Badge>
                <span>{p.title}</span>
                <a href={p.leetcode_url} target="_blank" rel="noreferrer" className="text-brand-600"><ExternalLink size={12} /></a>
              </div>
            ))}
          </div>
        </div>
      )}

      {roadmapLoading && <div className="text-sm text-slate-400">Loading roadmap…</div>}

      <div className="space-y-4">
        {(roadmap || []).map((section) => (
          <div key={section.topic} className="bg-white rounded-xl border border-slate-200 p-4">
            <div className="text-sm font-medium text-slate-700 mb-3">{section.topic}</div>
            <div className="space-y-2">
              {section.problems.map((p) => (
                <div key={p.title} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Badge>{p.difficulty}</Badge>
                    <span className="text-slate-700">{p.title}</span>
                    <a href={p.leetcode_url} target="_blank" rel="noreferrer" className="text-slate-400 hover:text-brand-600">
                      <ExternalLink size={13} />
                    </a>
                  </div>
                  <button
                    onClick={() => markSolved(section.topic, p.title, p.difficulty)}
                    className="text-xs text-slate-400 hover:text-emerald-600 flex items-center gap-1"
                  >
                    <CheckCircle2 size={14} /> Mark solved
                  </button>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
