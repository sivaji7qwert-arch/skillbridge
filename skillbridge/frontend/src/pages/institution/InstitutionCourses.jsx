import { useState } from "react";
import PageHeader from "../../components/PageHeader.jsx";
import useFetch from "../../hooks/useFetch.js";
import api from "../../services/api.js";

export default function InstitutionCourses() {
  const [refreshKey, setRefreshKey] = useState(0);
  const { data: courses, loading } = useFetch(() => api.getInstitutionCourses(), [refreshKey]);
  const [form, setForm] = useState({ department: "", course_name: "", taught_skills: "" });
  const [saving, setSaving] = useState(false);

  const addCourse = async () => {
    if (!form.department || !form.course_name) return;
    setSaving(true);
    try {
      await api.addInstitutionCourse({
        department: form.department, course_name: form.course_name,
        taught_skills: form.taught_skills.split(",").map((s) => s.trim()).filter(Boolean),
      });
      setForm({ department: "", course_name: "", taught_skills: "" });
      setRefreshKey((k) => k + 1);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <PageHeader title="Courses" subtitle="Register your department's courses and the skills each one teaches" />

      <div className="bg-white rounded-xl border border-slate-200 p-4 mb-6 max-w-xl">
        <div className="grid grid-cols-2 gap-3">
          <input placeholder="Department" value={form.department}
            onChange={(e) => setForm({ ...form, department: e.target.value })}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm" />
          <input placeholder="Course name" value={form.course_name}
            onChange={(e) => setForm({ ...form, course_name: e.target.value })}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm" />
          <input placeholder="Taught skills (comma separated)" value={form.taught_skills}
            onChange={(e) => setForm({ ...form, taught_skills: e.target.value })}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm col-span-2" />
        </div>
        <button onClick={addCourse} disabled={saving}
          className="mt-3 px-4 py-1.5 rounded-lg bg-brand-600 text-white text-sm font-medium hover:bg-brand-700 disabled:opacity-50">
          {saving ? "Adding…" : "Add Course"}
        </button>
      </div>

      {loading && <div className="text-sm text-slate-400">Loading…</div>}

      <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
        {(courses || []).map((c) => (
          <div key={c.course_id} className="px-4 py-3">
            <div className="text-sm font-medium text-slate-800">{c.course_name}</div>
            <div className="text-xs text-slate-500">{c.department}</div>
            <div className="flex flex-wrap gap-1 mt-1.5">
              {c.taught_skills.map((s) => (
                <span key={s} className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[11px]">{s}</span>
              ))}
            </div>
          </div>
        ))}
        {(courses || []).length === 0 && !loading && (
          <div className="px-4 py-6 text-xs text-slate-400 text-center">No courses added yet.</div>
        )}
      </div>
    </div>
  );
}
