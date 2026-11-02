import { useParams } from "react-router-dom";
import PageHeader from "../../components/PageHeader.jsx";
import Badge from "../../components/Badge.jsx";
import useFetch from "../../hooks/useFetch.js";
import api from "../../services/api.js";

export default function CandidateRanking() {
  const { jobId } = useParams();
  const { data: candidates, loading, error } = useFetch(() => api.getRankedCandidates(jobId), [jobId]);

  return (
    <div>
      <PageHeader title="AI-Ranked Candidates" subtitle="Scored by skill overlap and resume/job description similarity — every score shows its evidence" />

      {loading && <div className="text-sm text-slate-400">Loading…</div>}
      {error && <div className="text-sm text-red-600">Could not load candidates for this job.</div>}

      <div className="space-y-3">
        {(candidates || []).map((c) => (
          <div key={c.student_id} className="bg-white rounded-xl border border-slate-200 p-4">
            <div className="flex items-center justify-between mb-2">
              <div>
                <div className="text-sm font-medium text-slate-800">{c.college_name || "Unknown institution"}</div>
                <div className="text-xs text-slate-500">{c.course} · {c.branch}</div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-semibold text-brand-700">{c.overall_match_score}%</div>
                <div className="text-[11px] text-slate-400">overall match</div>
              </div>
            </div>

            <div className="flex flex-wrap gap-1.5 mb-2">
              {c.matched_skills.map((s) => (
                <span key={s} className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[11px]">{s}</span>
              ))}
              {c.missing_skills.map((s) => (
                <span key={s} className="px-2 py-0.5 rounded-full bg-red-50 text-red-600 text-[11px]">missing: {s}</span>
              ))}
            </div>

            <ul className="text-xs text-slate-500 list-disc list-inside space-y-0.5">
              {c.evidence.map((e, i) => <li key={i}>{e}</li>)}
            </ul>
          </div>
        ))}
        {(candidates || []).length === 0 && !loading && (
          <div className="text-sm text-slate-400 text-center py-10">No onboarded candidates match this criteria yet.</div>
        )}
      </div>
    </div>
  );
}
