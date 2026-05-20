import { NavLink } from 'react-router-dom';
import { LayoutDashboard, PlusCircle, Clock, Sparkles, User, Tag } from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard', end: true },
  { to: '/new', icon: PlusCircle, label: 'New Analysis', end: false },
  { to: '/history', icon: Clock, label: 'History', end: false },
  { to: '/aspects', icon: Tag, label: 'Aspects', end: false },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col h-screen fixed left-0 top-0 z-10">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center flex-shrink-0">
            <Sparkles size={16} className="text-white" />
          </div>
          <div>
            <p className="text-slate-900 font-bold text-sm leading-tight">Sentiment AI</p>
            <p className="text-slate-400 text-xs mt-0.5">Analysis Dashboard</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-5 space-y-0.5 overflow-y-auto">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest px-3 mb-3">
          Main Menu
        </p>
        {navItems.map(({ to, icon: Icon, label, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-500 hover:text-slate-800 hover:bg-slate-100'
              }`
            }
          >
            <Icon size={17} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User */}
      <div className="px-4 py-4 border-t border-slate-100">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
            <User size={15} className="text-blue-600" />
          </div>
          <div className="min-w-0">
            <p className="text-slate-700 text-xs font-semibold truncate">Temp User</p>
            <p className="text-slate-400 text-xs truncate">temp@dashboard.local</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
