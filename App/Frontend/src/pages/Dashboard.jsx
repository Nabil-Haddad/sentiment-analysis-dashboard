import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { BarChart2, CheckCircle, XCircle, Layers, PlusCircle, Clock, ChevronRight, ArrowRight } from 'lucide-react';
import StatCard from '../components/StatCard';
import SentimentBadge from '../components/SentimentBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { getSummary, getAllAnalyses } from '../api/analysis';

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      getSummary().catch((e) => (e.response?.status === 404 ? null : Promise.reject(e))),
      getAllAnalyses().catch((e) => (e.response?.status === 404 ? { data: [] } : Promise.reject(e))),
    ])
      .then(([summaryRes, analysesRes]) => {
        setSummary(summaryRes?.data ?? null);
        setRecent((analysesRes?.data ?? []).slice(0, 5));
      })
      .catch(() => setError('Failed to load dashboard data.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="md" label="Loading dashboard..." />
      </div>
    );
  }

  const positiveRate =
    summary && summary.total_aspect_results > 0
      ? Math.round((summary.positive_count / summary.total_aspect_results) * 100)
      : null;

  return (
    <div className="space-y-8">
      {/* Action row */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">Monitor and track your sentiment analyses</p>
        <Link
          to="/new"
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white text-sm font-semibold rounded-xl hover:bg-blue-700 transition-colors shadow-sm"
        >
          <PlusCircle size={15} />
          New Analysis
        </Link>
      </div>

      {error && (
        <div className="bg-rose-50 border border-rose-200 text-rose-600 text-sm px-4 py-3 rounded-xl">
          {error}
        </div>
      )}

      {/* Stat cards */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-5">
        <StatCard
          label="Total Analyses"
          value={summary?.total_analyses ?? 0}
          icon={Layers}
          iconBg="bg-blue-600"
          sub="All time"
        />
        <StatCard
          label="Aspect Results"
          value={summary?.total_aspect_results ?? 0}
          icon={BarChart2}
          iconBg="bg-violet-500"
          sub="Phrases with aspect"
        />
        <StatCard
          label="Positive"
          value={summary?.positive_count ?? 0}
          icon={CheckCircle}
          iconBg="bg-emerald-500"
          sub={positiveRate != null ? `${positiveRate}% of aspect results` : 'No data yet'}
          subColor="text-emerald-600"
        />
        <StatCard
          label="Negative"
          value={summary?.negative_count ?? 0}
          icon={XCircle}
          iconBg="bg-rose-500"
          sub="Aspect-level results"
          subColor="text-rose-500"
        />
      </div>

      {/* Recent analyses */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-bold text-slate-800">Recent Analyses</h2>
          {recent.length > 0 && (
            <Link
              to="/history"
              className="inline-flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700 font-semibold"
            >
              See All <ArrowRight size={14} />
            </Link>
          )}
        </div>

        {recent.length === 0 ? (
          <div className="bg-white rounded-2xl border border-dashed border-slate-300 py-16 flex flex-col items-center gap-3 shadow-sm">
            <div className="w-12 h-12 bg-slate-100 rounded-2xl flex items-center justify-center">
              <Clock size={22} className="text-slate-400" />
            </div>
            <p className="text-sm font-semibold text-slate-500">No analyses yet</p>
            <Link to="/new" className="text-sm text-blue-600 hover:text-blue-700 font-semibold">
              Run your first analysis →
            </Link>
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50">
                  <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">ID</th>
                  <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Date</th>
                  <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Top Sentiment</th>
                  <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Results</th>
                  <th className="px-6 py-3.5" />
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {recent.map((a) => {
                  const allResults = [...a.aspect_results, ...a.without_aspect_results];
                  const topLabel = allResults.length > 0
                    ? allResults.sort((x, y) => y.score - x.score)[0].label
                    : null;
                  return (
                    <tr key={a.analysis_id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="px-6 py-4 font-bold text-slate-700">
                        #{a.analysis_id}
                      </td>
                      <td className="px-6 py-4 text-slate-500">
                        {new Date(a.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4">
                        {topLabel ? <SentimentBadge label={topLabel} /> : <span className="text-slate-300 text-xs">—</span>}
                      </td>
                      <td className="px-6 py-4 text-slate-500">
                        {a.aspect_results.length + a.without_aspect_results.length} phrases
                      </td>
                      <td className="px-6 py-4 text-right">
                        <Link
                          to={`/analysis/${a.analysis_id}`}
                          className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 font-semibold"
                        >
                          View <ChevronRight size={12} />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
