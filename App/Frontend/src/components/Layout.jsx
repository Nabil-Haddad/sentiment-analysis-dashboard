import { useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import { Search } from 'lucide-react';

const pageTitles = {
  '/': 'Dashboard',
  '/new': 'New Analysis',
  '/history': 'History',
};

export default function Layout({ children }) {
  const { pathname } = useLocation();
  const title = pageTitles[pathname] ?? 'Analysis Detail';

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col overflow-hidden">
        {/* Top header */}
        <header className="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between flex-shrink-0">
          <h1 className="text-xl font-bold text-slate-900">{title}</h1>
          <div className="flex items-center gap-2.5 bg-slate-100 rounded-xl px-4 py-2.5 w-60">
            <Search size={14} className="text-slate-400 flex-shrink-0" />
            <input
              type="text"
              placeholder="Search..."
              className="bg-transparent text-sm text-slate-700 placeholder-slate-400 outline-none w-full"
            />
          </div>
        </header>

        <main className="flex-1 overflow-y-auto">
          <div className="min-h-full px-8 py-8 max-w-6xl">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
