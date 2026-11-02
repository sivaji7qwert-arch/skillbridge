import { useState } from "react";
import { Link } from "react-router-dom";
import PageHeader from "../../components/PageHeader.jsx";
import useFetch from "../../hooks/useFetch.js";
import api from "../../services/api.js";

export default function EmployerDashboard() {
  const [refreshKey, setRefreshKey] = useState(0);
  const { data: jobs, loading } = useFetch(() => api.getMyJobs(), [refreshKey]);
  const [companyForm, setCompanyForm] = useState({ name: "", sector: "", city: "", website: "", description: "" });
  const [savingCompany, setSavingCompany] = useState(false);
  const [companySaved, setCompanySaved] = useState(false);
  const [companyError, setCompanyError] = useState(null);

  const saveCompany = async () => {
    if (!companyForm.name) return;
    setSavingCompany(true);
    setCompanyError(null);
    try {
      await api.createOrUpdateCompany(companyForm);
      setCompanySaved(true);
      setRefreshKey((k) => k + 1);
    } catch (err) {
      setCompanyError(err.response?.data?.detail || "Could not save company profile.");
    } finally {
      setSavingCompany(false);
    }
  };

  return (
    <div>
      <PageHeader title="Employer Dashboard" subtitle="Manage your company profile and job postings" />

      <div className="bg-white rounded-xl border border-slate-200 p-4 mb-6 max-w-xl">
        <div className="text-sm font-medium text-slate-700 mb-3">Company Profile</div>
        <div className="grid grid-cols-2 gap-3">
          <input placeholder="Company name" value={companyForm.name}
            onChange={(e) => setCompanyForm({ ...companyForm, name: e.target.value })}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm col-span-2" />
          <input placeholder="Sector" value={companyForm.sector}
            onChange={(e) => setCompanyForm({ ...companyForm, sector: e.target.value })}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm" />
          <input placeholder="City" value={companyForm.city}
            onChange={(e) => setCompanyForm({ ...companyForm, city: e.target.value })}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm" />
          <input placeholder="Website" value={companyForm.website}
            onChange={(e) => setCompanyForm({ ...companyForm, website: e.target.value })}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm col-span-2" />
          <textarea placeholder="Company description" value={companyForm.description}
            onChange={(e) => setCompanyForm({ ...companyForm, description: e.target.value })}
            rows={2} className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm col-span-2" />
        </div>
        <button onClick={saveCompany} disabled={savingCompany}
          className="mt-3 px-4 py-1.5 rounded-lg bg-brand-600 text-white text-sm font-medium hover:bg-brand-700 disabled:opacity-50">
          {savingCompany ? "Saving…" : "Save Company Profile"}
        </button>
        {companySaved && <span className="text-xs text-emerald-600 ml-3">Saved</span>}
        {companyError && <div className="text-xs text-red-600 mt-2">{companyError}</div>}
      </div>

      <div className="flex items-center justify-between mb-3">
        <div className="text-sm font-medium text-slate-700">Your Job Postings</div>
        <Link to="/employer/post-job" className="text-sm text-brand-600 hover:underline">+ Post a Job</Link>
      </div>

      {loading && <div className="text-sm text-slate-400">Loading…</div>}

      <div className="space-y-2">
        {(jobs || []).map((j) => (
          <div key={j.job_id} className="bg-white rounded-xl border border-slate-200 p-4 flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-slate-800">{j.title}</div>
              <div className="text-xs text-slate-500">{j.location} · {j.application_count} applications</div>
            </div>
            <Link to={`/employer/jobs/${j.job_id}/candidates`} className="text-sm text-brand-600 hover:underline">
              View Candidates →
            </Link>
          </div>
        ))}
        {(jobs || []).length === 0 && !loading && (
          <div className="text-sm text-slate-400 text-center py-10">
            No jobs posted yet. Create a company profile above, then post your first job.
          </div>
        )}
      </div>
    </div>
  );
}
