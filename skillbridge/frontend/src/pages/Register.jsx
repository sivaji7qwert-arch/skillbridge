import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../services/api.js";

const ROLES = [
  { value: "student", label: "Student" },
  { value: "employer", label: "Employer / Recruiter" },
  { value: "institution", label: "Institution / College" },
  { value: "admin", label: "Government / Admin" },
];

export default function Register() {
  const [form, setForm] = useState({
    full_name: "", email: "", password: "", role: "student",
    college_name: "", institution_name: "",
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const payload = { ...form };
      if (form.role !== "student") delete payload.college_name;
      if (form.role !== "institution") delete payload.institution_name;

      const res = await api.register(payload);
      localStorage.setItem("skillbridge_token", res.access_token);
      localStorage.setItem("skillbridge_user", JSON.stringify(res.user));
      navigate(`/${res.user.role}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 py-10">
      <div className="w-full max-w-sm">
        <div className="text-center mb-6">
          <div className="text-2xl font-semibold text-brand-900">SkillBridge</div>
        </div>
        <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-xl p-6 space-y-4">
          <div>
            <label className="block text-xs text-slate-500 mb-1">I am a…</label>
            <select
              value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm bg-white"
            >
              {ROLES.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Full Name</label>
            <input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
          </div>
          {form.role === "student" && (
            <div>
              <label className="block text-xs text-slate-500 mb-1">College / Institution Name</label>
              <input value={form.college_name} onChange={(e) => setForm({ ...form, college_name: e.target.value })}
                placeholder="Must match your institution's registered name exactly"
                className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
            </div>
          )}
          {form.role === "institution" && (
            <div>
              <label className="block text-xs text-slate-500 mb-1">Institution Name</label>
              <input value={form.institution_name} onChange={(e) => setForm({ ...form, institution_name: e.target.value })}
                className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
            </div>
          )}
          <div>
            <label className="block text-xs text-slate-500 mb-1">Email</label>
            <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Password</label>
            <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
          </div>
          {error && <div className="text-xs text-red-600">{error}</div>}
          <button type="submit" disabled={loading}
            className="w-full py-2 rounded-lg bg-brand-600 text-white text-sm font-medium hover:bg-brand-700 disabled:opacity-50">
            {loading ? "Creating account…" : "Create account"}
          </button>
        </form>
        <p className="text-center text-xs text-slate-400 mt-4">
          Already have an account? <Link to="/login" className="text-brand-600 hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
