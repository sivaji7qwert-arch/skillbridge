import { useState } from "react";
import PageHeader from "../components/PageHeader.jsx";
import DataTable from "../components/DataTable.jsx";
import Badge from "../components/Badge.jsx";
import useFetch from "../hooks/useFetch.js";
import api from "../services/api.js";

export default function LabourMarket() {
  const [city, setCity] = useState("");
  const { data: overview, loading } = useFetch(() => api.getLabourMarketOverview(), []);
  const { data: cityData } = useFetch(() => api.getSkillsByCity(city || undefined), [city]);

  const cities = overview ? Object.keys(overview.top_cities) : [];

  return (
    <div>
      <PageHeader
        title="Labour Market Intelligence"
        subtitle="Skill demand broken down by city — pinpoint where each skill matters most"
      />

      {loading && <div className="text-sm text-slate-400">Loading…</div>}

      {!loading && (
        <>
          <div className="flex items-center gap-2 mb-4">
            <label className="text-sm text-slate-500">Filter by city:</label>
            <select
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm bg-white"
            >
              <option value="">All cities</option>
              {cities.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <DataTable
            keyField="_rowId"
            columns={[
              { key: "city", label: "City" },
              { key: "skill", label: "Skill" },
              { key: "job_count", label: "Job Postings" },
              {
                key: "demand_pct_in_city",
                label: "Demand % in City",
                render: (r) => <Badge>{r.demand_pct_in_city >= 30 ? "High" : r.demand_pct_in_city >= 15 ? "Medium" : "Low"}</Badge>,
              },
            ]}
            rows={(cityData || []).slice(0, 100).map((r, i) => ({ ...r, _rowId: i }))}
          />
        </>
      )}
    </div>
  );
}
