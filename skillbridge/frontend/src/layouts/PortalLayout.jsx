import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { LogOut } from "lucide-react";

export default function PortalLayout({ navItems, portalLabel }) {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("skillbridge_user") || "null");

  const logout = () => {
    localStorage.removeItem("skillbridge_token");
    localStorage.removeItem("skillbridge_user");
    navigate("/login");
  };

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 shrink-0 bg-brand-900 text-white flex flex-col">
        <div className="px-5 py-5 border-b border-white/10">
          <div className="text-lg font-semibold tracking-tight">SkillBridge</div>
          <div className="text-xs text-brand-100/60 mt-0.5">{portalLabel}</div>
        </div>
        <nav className="flex-1 px-2 py-4 space-y-1">
          {navItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to} to={to} end={end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive ? "bg-brand-600 text-white" : "text-brand-100/80 hover:bg-white/5 hover:text-white"
                }`
              }
            >
              <Icon size={17} />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 border-b bg-white flex items-center justify-between px-6">
          <div className="text-sm text-slate-500">{portalLabel}</div>
          <div className="flex items-center gap-3 text-sm">
            {user && <span className="text-slate-700">{user.full_name}</span>}
            <button onClick={logout} className="text-slate-400 hover:text-slate-700" title="Log out">
              <LogOut size={16} />
            </button>
          </div>
        </header>
        <main className="flex-1 p-6 bg-slate-50">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
