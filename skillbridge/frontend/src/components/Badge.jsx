const COLOR_MAP = {
  Emerging: "bg-purple-100 text-purple-700",
  Growing: "bg-emerald-100 text-emerald-700",
  Stable: "bg-slate-100 text-slate-600",
  Declining: "bg-amber-100 text-amber-700",
  "Insufficient Data": "bg-slate-100 text-slate-400",
  Covered: "bg-emerald-100 text-emerald-700",
  "Low Priority Gap": "bg-amber-100 text-amber-700",
  "Critical Gap": "bg-red-100 text-red-700",
  HIGH: "bg-red-100 text-red-700",
  MEDIUM: "bg-amber-100 text-amber-700",
  LOW: "bg-slate-100 text-slate-600",
  ADD: "bg-emerald-100 text-emerald-700",
  MODIFY: "bg-amber-100 text-amber-700",
  REDUCE: "bg-red-100 text-red-700",
  RETAIN: "bg-slate-100 text-slate-600",
  MONITOR: "bg-blue-100 text-blue-700",
};

export default function Badge({ children }) {
  const cls = COLOR_MAP[children] || "bg-slate-100 text-slate-600";
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${cls}`}>
      {children}
    </span>
  );
}
