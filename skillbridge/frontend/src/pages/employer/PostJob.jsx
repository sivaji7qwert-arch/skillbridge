import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/PageHeader.jsx";
import api from "../../services/api.js";

export default function PostJob() {
  const [form, setForm] = useState({
    title: "", description: "", required_skills: "", preferred_qualifications: "",
    location: "", experience_required: 0,
  });
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      await api.postJob({
        ...form,
        required_skills: form.required_skills.split(",").map((s) => s.trim()).filter(Boolean),
        experience_required: parseInt(form.experience_required, 10) || 0,
      });
      navigate("/employer");
    } catch (err) {
      setError(err.response?.data?.detail || "Could not post job. Make sure your company profile is saved first.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-xl">
      <PageHeader title="Post a Job" subtitle="Candidates will be AI-ranked against these requirements" />

      <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-xl p-6 space-y-4">
        <div>
          <label className="block text-xs text-slate-500 mb-1">Job Title</label>
          <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })}
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="block text-xs text-slate-500 mb-1">Description</label>
          <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}
            rows={4} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="block text-xs text-slate-500 mb-1">Required Skills (comma separated)</label>
          <input value={form.required_skills} onChange={(e) => setForm({ ...form, required_skills: e.target.value })}
            placeholder="Python, SQL, Power BI" className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs text-slate-500 mb-1">Location</label>
            <input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Min. Experience (years)</label>
            <input type="number" value={form.experience_required}
              onChange={(e) => setForm({ ...form, experience_required: e.target.value })}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
          </div>
        </div>
        <div>
          <label className="block text-xs text-slate-500 mb-1">Preferred Qualifications</label>
          <textarea value={form.preferred_qualifications}
            onChange={(e) => setForm({ ...form, preferred_qualifications: e.target.value })}
            rows={2} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
        </div>
        {error && <div className="text-xs text-red-600">{error}</div>}
        <button type="submit" disabled={saving}
          className="w-full py-2 rounded-lg bg-brand-600 text-white text-sm font-medium hover:bg-brand-700 disabled:opacity-50">
          {saving ? "Posting…" : "Post Job"}
        </button>
      </form>
    </div>
  );
}
