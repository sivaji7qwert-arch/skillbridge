import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../services/api.js";

const DEMO_ACCOUNTS = [
  { label: "Student", email: "student@skillbridge.local", password: "student123" },
  { label: "Employer", email: "employer@skillbridge.local", password: "employer123" },
  { label: "Institution", email: "institution@skillbridge.local", password: "institution123" },
  { label: "Admin", email: "admin@skillbridge.local", password: "admin123" },
];

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await api.login(email.trim(), password);
      localStorage.setItem("skillbridge_token", res.access_token);
      localStorage.setItem("skillbridge_user", JSON.stringify(res.user));
      navigate(`/${res.user.role}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="w-full max-w-sm">
        <div className="text-center mb-6">
          <div className="text-2xl font-semibold text-brand-900">SkillBridge</div>
        </div>
        <form onSubmit={handleLogin} className="bg-white border border-slate-200 rounded-xl p-6 space-y-4">
          <div>
            <label className="block text-xs text-slate-500 mb-1">Email</label>
            <input
              type="email" autoFocus value={email} onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Password</label>
            <input
              type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"
            />
          </div>
          {error && <div className="text-xs text-red-600">{error}</div>}
          <button
            type="submit" disabled={loading || !email || !password}
            className="w-full py-2 rounded-lg bg-brand-600 text-white text-sm font-medium hover:bg-brand-700 disabled:opacity-50"
          >
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <div className="mt-4">
          <div className="text-center text-xs text-slate-400 mb-2">Demo portals</div>
          <div className="grid grid-cols-2 gap-2">
            {DEMO_ACCOUNTS.map((account) => (
              <button
                key={account.email}
                type="button"
                onClick={() => {
                  setEmail(account.email);
                  setPassword(account.password);
                  setError(null);
                }}
                className="border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-600 hover:border-brand-300 hover:text-brand-700"
              >
                {account.label}
              </button>
            ))}
          </div>
        </div>
        <p className="text-center text-xs text-slate-400 mt-4">
          New here? <Link to="/register" className="text-brand-600 hover:underline">Create an account</Link>
        </p>
      </div>
    </div>
  );
}
