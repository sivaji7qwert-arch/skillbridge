import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react";
import PageHeader from "../components/PageHeader.jsx";
import Badge from "../components/Badge.jsx";
import useFetch from "../hooks/useFetch.js";
import api from "../services/api.js";

function StatusIcon({ status }) {
  if (status === "Covered") return <CheckCircle2 size={16} className="text-emerald-500" />;
  if (status === "Critical Gap") return <XCircle size={16} className="text-red-500" />;
  return <AlertTriangle size={16} className="text-amber-500" />;
}

export default function CurriculumAnalysis() {
  const location = useLocation();
  const { data: roles } = useFetch(() => api.getRoles(), []);
  const { data: curricula } = useFetch(() => api.getCurricula(), []);

  const [role, setRole] = useState("Data Analyst");
  const [curriculumId, setCurriculumId] = useState(location.state?.curriculumId || "");
  const [result, setResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (curricula && curricula.length && !curriculumId) {
      setCurriculumId(curricula[0].curriculum_id);
    }
  }, [curricula]); // eslint-disable-line react-hooks/exhaustive-deps

  const runAnalysis = async () => {
    if (!role || !curriculumId) return;
    setAnalyzing(true);
    setError(null);
    try {
      const res = await api.analyzeCurriculum(role, curriculumId);
      setResult(res);
    } catch (e) {
      setError("Could not analyze this role/curriculum combination. Make sure the data pipeline has been run.");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Industry vs Curriculum Skill Gap Analysis"
        subtitle="Compares a target role's real industry skill demand against a training curriculum, and generates explainable recommendations"
      />

      <div className="bg-white rounded-xl border border-slate-200 p-4 mb-5 flex flex-wrap items-end gap-3">
        <div>
          <label className="block text-xs text-slate-500 mb-1">Target Role</label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm bg-white w-64"
          >
            {(roles || []).map((r) => (
              <option key={r.role_id} value={r.name}>{r.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-500 mb-1">Curriculum</label>
          <select
            value={curriculumId}
            onChange={(e) => setCurriculumId(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm bg-white w-64"
          >
            {(curricula || []).map((c) => (
              <option key={c.curriculum_id} value={c.curriculum_id}>
                {c.curriculum_id} — {c.institute_name}
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={runAnalysis}
          disabled={analyzing}
          className="px-4 py-1.5 rounded-lg bg-brand-600 text-white text-sm font-medium hover:bg-brand-700 disabled:opacity-50"
        >
          {analyzing ? "Analyzing…" : "Analyze Alignment"}
        </button>
      </div>

      {error && <div className="text-sm text-red-600 mb-4">{error}</div>}

      {result && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
            <div className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="text-xs text-slate-500">Current Alignment</div>
              <div className="text-3xl font-semibold text-slate-900 mt-1">{result.alignment_before_pct}%</div>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="text-xs text-slate-500">Estimated Alignment After Recommendations</div>
              <div className="text-3xl font-semibold text-emerald-600 mt-1">{result.alignment_after_estimate_pct}%</div>
            </div>
            <div className="bg-amber-50 rounded-xl border border-amber-200 p-4 text-xs text-amber-800 flex items-center">
              {result.note}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div>
              <div className="text-sm font-medium text-slate-700 mb-2">Skill Gap Breakdown</div>
              <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
                {result.gaps.map((g) => (
                  <div key={g.skill} className="flex items-center justify-between px-4 py-2.5">
                    <div className="flex items-center gap-2">
                      <StatusIcon status={g.status} />
                      <span className="text-sm text-slate-800">{g.skill}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-slate-400">
                        industry {g.industry_demand_pct}% · curriculum {g.curriculum_coverage_score}
                      </span>
                      <Badge>{g.status}</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <div className="text-sm font-medium text-slate-700 mb-2">AI Recommendations (with evidence)</div>
              <div className="space-y-3">
                {result.recommendations.map((rec) => (
                  <div key={rec.skill} className="bg-white rounded-xl border border-slate-200 p-3">
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center gap-2">
                        <Badge>{rec.action}</Badge>
                        <span className="font-medium text-sm text-slate-800">{rec.skill}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge>{rec.priority}</Badge>
                        <span className="text-xs text-slate-400">{rec.confidence}% confidence</span>
                      </div>
                    </div>
                    <ul className="text-xs text-slate-500 space-y-0.5 mt-1.5 list-disc list-inside">
                      {rec.evidence.map((e, i) => (
                        <li key={i}>{e}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
