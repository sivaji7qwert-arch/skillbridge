import { useState, useMemo } from "react";
import PageHeader from "../components/PageHeader.jsx";
import DataTable from "../components/DataTable.jsx";
import Badge from "../components/Badge.jsx";
import useFetch from "../hooks/useFetch.js";
import api from "../services/api.js";

export default function Skills() {
  const { data: skills, loading } = useFetch(() => api.getSkills(), []);
  const [search, setSearch] = useState("");
  const [trendFilter, setTrendFilter] = useState("");

  const filtered = useMemo(() => {
    if (!skills) return [];
    return skills
      .filter((s) => s.skill.toLowerCase().includes(search.toLowerCase()))
      .filter((s) => !trendFilter || s.trend === trendFilter)
      .sort((a, b) => b.skill_demand_score - a.skill_demand_score);
  }, [skills, search, trendFilter]);

  return (
    <div>
      <PageHeader title="Skills" subtitle="All skills detected across analyzed job postings, ranked by composite demand score" />

      <div className="flex gap-2 mb-4">
        <input
          placeholder="Search skill…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm bg-white w-64"
        />
        <select
          value={trendFilter}
          onChange={(e) => setTrendFilter(e.target.value)}
          className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm bg-white"
        >
          <option value="">All trends</option>
          <option value="Emerging">Emerging</option>
          <option value="Growing">Growing</option>
          <option value="Stable">Stable</option>
          <option value="Declining">Declining</option>
        </select>
      </div>

      {loading && <div className="text-sm text-slate-400">Loading…</div>}

      {!loading && (
        <DataTable
          keyField="skill"
          columns={[
            { key: "skill", label: "Skill" },
            { key: "demand_percentage", label: "Demand %", render: (r) => `${r.demand_percentage}%` },
            { key: "growth_pct", label: "Growth", render: (r) => `${r.growth_pct > 0 ? "+" : ""}${r.growth_pct}%` },
            { key: "trend", label: "Trend", render: (r) => <Badge>{r.trend}</Badge> },
            { key: "avg_salary", label: "Avg Salary", render: (r) => `₹${Math.round(r.avg_salary).toLocaleString("en-IN")}` },
            { key: "skill_demand_score", label: "Demand Score", render: (r) => r.skill_demand_score.toFixed(1) },
          ]}
          rows={filtered}
        />
      )}
    </div>
  );
}
