export default function StatCard({ label, value, icon: Icon, iconBg, sub, subColor }) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center gap-3 mb-4">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${iconBg}`}>
          <Icon size={18} className="text-white" />
        </div>
        <p className="text-sm font-semibold text-slate-600">{label}</p>
      </div>
      <p className="text-3xl font-bold text-slate-900 tabular-nums">{value ?? '—'}</p>
      {sub && (
        <p className={`text-xs mt-2 font-medium ${subColor ?? 'text-slate-400'}`}>{sub}</p>
      )}
    </div>
  );
}
