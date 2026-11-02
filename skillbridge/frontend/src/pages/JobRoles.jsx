import PageHeader from "../components/PageHeader.jsx";
import DataTable from "../components/DataTable.jsx";
import Badge from "../components/Badge.jsx";
import useFetch from "../hooks/useFetch.js";
import api from "../services/api.js";

export default function JobRoles() {
  const { data: roles, loading } = useFetch(() => api.getTrendingRoles(30), []);

  return (
    <div>
      <PageHeader title="Job Roles" subtitle="Emerging and growing roles detected from recent posting volume, with required skills and typical locations" />

      {loading && <div className="text-sm text-slate-400">Loading…</div>}

      {!loading && (
        <DataTable
          keyField="role"
          columns={[
            { key: "role", label: "Role" },
            { key: "current_demand_postings", label: "Postings (recent)" },
            { key: "growth_pct", label: "Growth", render: (r) => `${r.growth_pct > 0 ? "+" : ""}${r.growth_pct}%` },
            { key: "trend", label: "Trend", render: (r) => <Badge>{r.trend}</Badge> },
            { key: "required_skills", label: "Top Required Skills" },
            { key: "top_locations", label: "Top Locations" },
            { key: "avg_salary", label: "Avg Salary", render: (r) => `₹${Math.round(r.avg_salary).toLocaleString("en-IN")}` },
          ]}
          rows={roles || []}
        />
      )}
    </div>
  );
}
