import PageHeader from "../../components/PageHeader.jsx";
import KPICard from "../../components/KPICard.jsx";
import useFetch from "../../hooks/useFetch.js";
import api from "../../services/api.js";
import { Users, TrendingUp } from "lucide-react";

export default function InstitutionDashboard() {
  const { data: stats, loading: statsLoading } = useFetch(() => api.getStudentSkillStats(), []);
  const { data: readiness, loading: readinessLoading } = useFetch(() => api.getPlacementReadiness(), []);

  return (
    <div>
      <PageHeader title="Institution Dashboard" subtitle="Skill statistics and placement readiness for your registered students" />

      {(statsLoading || readinessLoading) && <div className="text-sm text-slate-400">Loading…</div>}

      {readiness && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <KPICard label="Total Students" value={readiness.total_students} icon={Users} />
          <KPICard label="Placement Ready" value={readiness.readiness_breakdown["Placement Ready"]} icon={TrendingUp} />
          <KPICard label="Developing" value={readiness.readiness_breakdown["Developing"]} />
        </div>
      )}

      {stats && stats.total_students > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <div>
            <div className="text-sm font-medium text-slate-700 mb-2">Most Common Known Skills</div>
            <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
              {stats.top_known_skills.map(([skill, count]) => (
                <div key={skill} className="flex items-center justify-between px-4 py-2.5">
                  <span className="text-sm text-slate-700">{skill}</span>
                  <span className="text-xs text-slate-400">{count} students</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <div className="text-sm font-medium text-slate-700 mb-2">Common Skill Gaps (high demand, low coverage)</div>
            <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
              {stats.common_skill_gaps.map((g) => (
                <div key={g.skill} className="flex items-center justify-between px-4 py-2.5">
                  <span className="text-sm text-slate-700">{g.skill}</span>
                  <span className="text-xs text-slate-400">
                    {g.student_coverage_pct}% of students know it (industry demand: {g.industry_demand_score})
                  </span>
                </div>
              ))}
              {stats.common_skill_gaps.length === 0 && (
                <div className="px-4 py-6 text-xs text-slate-400 text-center">No significant gaps detected.</div>
              )}
            </div>
          </div>
        </div>
      )}

      {stats && stats.total_students === 0 && (
        <div className="text-sm text-slate-400 bg-white border border-slate-200 rounded-xl p-6 text-center">
          {stats.message}
        </div>
      )}
    </div>
  );
}
