export default function KPICard({ label, value, sublabel, icon: Icon }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-start justify-between">
      <div>
        <div className="text-xs font-medium text-slate-500">{label}</div>
        <div className="text-2xl font-semibold text-slate-900 mt-1">{value}</div>
        {sublabel && <div className="text-xs text-slate-400 mt-1">{sublabel}</div>}
      </div>
      {Icon && (
        <div className="w-9 h-9 rounded-lg bg-brand-50 text-brand-600 flex items-center justify-center">
          <Icon size={18} />
        </div>
      )}
    </div>
  );
}
