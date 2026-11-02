import { useState } from "react";
import PageHeader from "../../components/PageHeader.jsx";
import useFetch from "../../hooks/useFetch.js";
import api from "../../services/api.js";

export default function JobBrowse() {
  const { data, loading } = useFetch(() => api.browseJobs(), []);
  const jobs = data?.results || [];
  const [applyStatus, setApplyStatus] = useState({});

  const apply = async (jobId) => {
    setApplyStatus((s) => ({ ...s, [jobId]: "applying" }));
    try {
      const res = await api.applyToJob(jobId);
      setApplyStatus((s) => ({ ...s, [jobId]: `Applied — ${res.match_score}% match` }));
    } catch (err) {
      setApplyStatus((s) => ({ ...s, [jobId]: err.response?.data?.detail || "Could not apply" }));
    }
  };

  return (
    <div>
      <PageHeader title="Browse Jobs" subtitle="Jobs posted directly on SkillBridge by employers" />

      {loading && <div className="text-sm text-slate-400">Loading…</div>}

      <div className="space-y-3">
        {(jobs || []).map((j) => (
          <div key={j.job_id} className="bg-white rounded-xl border border-slate-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-slate-800">{j.title}</div>
                <div className="text-xs text-slate-500">{j.company} · {j.location || "Location not specified"}</div>
              </div>
              <button
                onClick={() => apply(j.job_id)}
                disabled={applyStatus[j.job_id] === "applying"}
                className="px-3 py-1.5 rounded-lg bg-brand-600 text-white text-xs font-medium hover:bg-brand-700 disabled:opacity-50"
              >
                {applyStatus[j.job_id] === "applying" ? "Applying…" : "Apply"}
              </button>
            </div>
            <div className="flex flex-wrap gap-1.5 mt-2">
              {(j.required_skills || []).map((s) => (
                <span key={s} className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[11px]">{s}</span>
              ))}
            </div>
            {applyStatus[j.job_id] && applyStatus[j.job_id] !== "applying" && (
              <div className="text-xs text-emerald-700 mt-2">{applyStatus[j.job_id]}</div>
            )}
          </div>
        ))}
        {(jobs || []).length === 0 && !loading && (
          <div className="text-sm text-slate-400 text-center py-10">No jobs posted yet.</div>
        )}
      </div>
    </div>
  );
}
