import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api.js";

const PROGRAMMING_LANGUAGES = ["Python", "Java", "JavaScript", "C++", "C", "Go", "TypeScript", "SQL"];

export default function StudentOnboarding() {
  const [form, setForm] = useState({
    college_name: "", course: "", branch: "", graduation_year: new Date().getFullYear(),
    career_interest: "", known_skills: "", programming_languages: [], target_role: "Data Analyst",
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const toggleLanguage = (lang) => {
    setForm((f) => ({
      ...f,
      programming_languages: f.programming_languages.includes(lang)
        ? f.programming_languages.filter((l) => l !== lang)
        : [...f.programming_languages, lang],
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.completeOnboarding({
        ...form,
        graduation_year: parseInt(form.graduation_year, 10),
        known_skills: form.known_skills.split(",").map((s) => s.trim()).filter(Boolean),
      });
      navigate("/student");
    } catch (err) {
      setError(err.response?.data?.detail || "Could not save your profile.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto">
      <h1 className="text-xl font-semibold text-slate-900 mb-1">Tell us about yourself</h1>
      <p className="text-sm text-slate-500 mb-5">This powers your personalized skill-gap analysis and recommendations.</p>

      <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-xl p-6 space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs text-slate-500 mb-1">College / Institution</label>
            <input value={form.college_name} onChange={(e) => setForm({ ...form, college_name: e.target.value })}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Graduation Year</label>
            <input type="number" value={form.graduation_year} onChange={(e) => setForm({ ...form, graduation_year: e.target.value })}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Course</label>
            <input value={form.course} onChange={(e) => setForm({ ...form, course: e.target.value })}
              placeholder="e.g. B.Tech" className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Branch</label>
            <input value={form.branch} onChange={(e) => setForm({ ...form, branch: e.target.value })}
              placeholder="e.g. Computer Science" className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
          </div>
        </div>

        <div>
          <label className="block text-xs text-slate-500 mb-1">Target Role</label>
          <input value={form.target_role} onChange={(e) => setForm({ ...form, target_role: e.target.value })}
            placeholder="e.g. Data Analyst, Machine Learning Engineer"
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
        </div>

        <div>
          <label className="block text-xs text-slate-500 mb-1">Career Interest</label>
          <input value={form.career_interest} onChange={(e) => setForm({ ...form, career_interest: e.target.value })}
            placeholder="e.g. Data Science, Software Development"
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
        </div>

        <div>
          <label className="block text-xs text-slate-500 mb-1">Known Skills (comma separated)</label>
          <textarea value={form.known_skills} onChange={(e) => setForm({ ...form, known_skills: e.target.value })}
            placeholder="Python, SQL, Excel" rows={2}
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
          <p className="text-[11px] text-slate-400 mt-1">You can also upload a resume later to auto-detect skills.</p>
        </div>

        <div>
          <label className="block text-xs text-slate-500 mb-2">Programming Languages</label>
          <div className="flex flex-wrap gap-2">
            {PROGRAMMING_LANGUAGES.map((lang) => (
              <button type="button" key={lang} onClick={() => toggleLanguage(lang)}
                className={`px-3 py-1 rounded-full text-xs border ${
                  form.programming_languages.includes(lang)
                    ? "bg-brand-600 text-white border-brand-600"
                    : "bg-white text-slate-600 border-slate-200"
                }`}>
                {lang}
              </button>
            ))}
          </div>
        </div>

        {error && <div className="text-xs text-red-600">{error}</div>}
        <button type="submit" disabled={loading}
          className="w-full py-2 rounded-lg bg-brand-600 text-white text-sm font-medium hover:bg-brand-700 disabled:opacity-50">
          {loading ? "Saving…" : "Finish Setup"}
        </button>
      </form>
    </div>
  );
}
