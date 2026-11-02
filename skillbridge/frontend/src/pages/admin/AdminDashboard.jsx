import PageHeader from "../../components/PageHeader.jsx";
import KPICard from "../../components/KPICard.jsx";
import DataTable from "../../components/DataTable.jsx";
import Badge from "../../components/Badge.jsx";
import useFetch from "../../hooks/useFetch.js";
import api from "../../services/api.js";
import { Users, Briefcase, Building2, Sparkles } from "lucide-react";

export default function AdminDashboard() {
  const { data: overview, loading: overviewLoading } = useFetch(() => api.getAdminOverview(), []);
  const { data: districtGaps, loading: districtLoading } = useFetch(() => api.getDistrictSkillGaps(), []);
  const { data: institutionReadiness, loading: instLoading } = useFetch(() => api.getInstitutionReadiness(), []);
  const { data: emergingRoles, loading: rolesLoading } = useFetch(() => api.getAdminEmergingRoles(), []);

  return (
    <div>
      <PageHeader title="Government Dashboard" subtitle="Platform-wide labour market and skill development analytics" />

      {overviewLoading && <div className="text-sm text-slate-400">Loading…</div>}

      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <KPICard label="Total Users" value={overview.total_users} icon={Users} />
          <KPICard label="Students" value={overview.total_students} icon={Users} />
          <KPICard label="Employers" value={overview.total_employers} icon={Briefcase} />
          <KPICard label="Institutions" value={overview.total_institutions} icon={Building2} />
        </div>
      )}

      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
          <KPICard label="Jobs Analyzed" value={overview.jobs_analyzed.toLocaleString()} icon={Sparkles} />
          <KPICard label="Skills Tracked" value={overview.skills_tracked} />
          <KPICard label="Emerging Roles" value={overview.emerging_roles} />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
        <div>
          <div className="text-sm font-medium text-slate-700 mb-2">City-wise Top Skill Demand</div>
          {districtLoading && <div className="text-sm text-slate-400">Loading…</div>}
          <div className="space-y-3">
            {Object.entries(districtGaps || {}).slice(0, 6).map(([city, skills]) => (
              <div key={city} className="bg-white rounded-xl border border-slate-200 p-3">
                <div className="text-sm font-medium text-slate-800 mb-1.5">{city}</div>
                <div className="flex flex-wrap gap-1.5">
                  {skills.map((s) => (
                    <span key={s.skill} className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[11px]">
                      {s.skill} ({s.demand_pct_in_city}%)
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="text-sm font-medium text-slate-700 mb-2">Institution Placement Readiness</div>
          {instLoading && <div className="text-sm text-slate-400">Loading…</div>}
          <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
            {(institutionReadiness || []).map((inst) => (
              <div key={inst.institution_name} className="flex items-center justify-between px-4 py-2.5">
                <div>
                  <div className="text-sm text-slate-800">{inst.institution_name}</div>
                  <div className="text-[11px] text-slate-400">{inst.total_students} students</div>
                </div>
                <span className="text-sm font-medium text-brand-700">{inst.placement_ready_pct}%</span>
              </div>
            ))}
            {(institutionReadiness || []).length === 0 && !instLoading && (
              <div className="px-4 py-6 text-xs text-slate-400 text-center">No institutions registered yet.</div>
            )}
          </div>
        </div>
      </div>

      <div className="text-sm font-medium text-slate-700 mb-2">Emerging Job Roles</div>
      {rolesLoading && <div className="text-sm text-slate-400">Loading…</div>}
      {emergingRoles && (
        <DataTable
          keyField="role"
          columns={[
            { key: "role", label: "Role" },
            { key: "current_demand_postings", label: "Postings" },
            { key: "growth_pct", label: "Growth", render: (r) => `${r.growth_pct > 0 ? "+" : ""}${r.growth_pct}%` },
            { key: "trend", label: "Trend", render: (r) => <Badge>{r.trend}</Badge> },
            { key: "top_locations", label: "Top Locations" },
          ]}
          rows={emergingRoles}
        />
      )}
    </div>
  );
}
