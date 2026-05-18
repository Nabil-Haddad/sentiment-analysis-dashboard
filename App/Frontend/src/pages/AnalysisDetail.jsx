import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Clock } from 'lucide-react';
import SentimentBadge from '../components/SentimentBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { getAnalysisResults } from '../api/analysis';

const ScoreBar = ({ score }) => (
  <div className="flex items-center gap-2">
    <div className="w-20 h-1.5 bg-slate-100 rounded-full overflow-hidden">
      <div
        className="h-full bg-blue-500 rounded-full"
        style={{ width: `${Math.round(score * 100)}%` }}
      />
    </div>
    <span className="text-xs text-slate-500 tabular-nums w-8">{Math.round(score * 100)}%</span>
  </div>
);

export default function AnalysisDetail() {
  const { id } = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getAnalysisResults(id)
      .then((res) => setAnalysis(res.data))
      .catch((err) => {
        setError(err.response?.status === 404 ? 'Analysis not found.' : 'Failed to load analysis.');
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="md" label="Loading analysis..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <Link to="/history" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 font-medium transition-colors">
          <ArrowLeft size={15} /> Back to History
        </Link>
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm">
          <EmptyState title={error} description="The requested analysis could not be loaded." />
        </div>
      </div>
    );
  }

  const total = analysis.aspect_results.length + analysis.without_aspect_results.length;

  return (
    <div className="space-y-6 max-w-5xl">
      <Link
        to="/history"
        className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 font-medium transition-colors"
      >
        <ArrowLeft size={15} />
        Back to History
      </Link>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Analysis #{analysis.analysis_id}</h2>
          <div className="flex items-center gap-1.5 mt-1.5">
            <Clock size={13} className="text-slate-400" />
            <p className="text-sm text-slate-500">{new Date(analysis.created_at).toLocaleString()}</p>
          </div>
        </div>

        <div className="flex gap-3">
          <div className="px-5 py-3 bg-blue-50 rounded-2xl text-center border border-blue-100">
            <p className="text-2xl font-bold text-blue-700 tabular-nums">{analysis.aspect_results.length}</p>
            <p className="text-xs text-blue-500 mt-0.5 font-medium">Aspect</p>
          </div>
          <div className="px-5 py-3 bg-slate-100 rounded-2xl text-center">
            <p className="text-2xl font-bold text-slate-700 tabular-nums">{analysis.without_aspect_results.length}</p>
            <p className="text-xs text-slate-500 mt-0.5 font-medium">Other</p>
          </div>
          <div className="px-5 py-3 bg-white rounded-2xl text-center border border-slate-200 shadow-sm">
            <p className="text-2xl font-bold text-slate-700 tabular-nums">{total}</p>
            <p className="text-xs text-slate-500 mt-0.5 font-medium">Total</p>
          </div>
        </div>
      </div>

      {/* Aspect-based results */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
          <p className="text-sm font-bold text-slate-700">Aspect-Based Results</p>
          <span className="text-xs text-slate-500 bg-slate-200 px-2 py-0.5 rounded-full font-semibold">
            {analysis.aspect_results.length}
          </span>
        </div>

        {analysis.aspect_results.length === 0 ? (
          <EmptyState
            title="No aspect results"
            description="No known aspects were detected in the analysed comments."
          />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100">
                <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Phrase</th>
                <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Aspect</th>
                <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Sentiment</th>
                <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {analysis.aspect_results.map((r, i) => (
                <tr key={i} className="hover:bg-slate-50/70 transition-colors">
                  <td className="px-6 py-3.5 text-slate-600 max-w-sm">
                    <span className="line-clamp-2 leading-relaxed">{r.phrase}</span>
                  </td>
                  <td className="px-6 py-3.5">
                    <span className="inline-flex px-2.5 py-1 bg-blue-50 text-blue-700 text-xs font-semibold rounded-full ring-1 ring-blue-200">
                      {r.aspect}
                    </span>
                  </td>
                  <td className="px-6 py-3.5">
                    <SentimentBadge label={r.label} />
                  </td>
                  <td className="px-6 py-3.5">
                    <ScoreBar score={r.score} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Without-aspect results */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
          <p className="text-sm font-bold text-slate-700">Other Results</p>
          <span className="text-xs text-slate-500 bg-slate-200 px-2 py-0.5 rounded-full font-semibold">
            {analysis.without_aspect_results.length}
          </span>
          <span className="text-xs text-slate-400">· no aspect detected</span>
        </div>

        {analysis.without_aspect_results.length === 0 ? (
          <EmptyState
            title="No other results"
            description="Every phrase contained a detectable aspect."
          />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100">
                <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Phrase</th>
                <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Sentiment</th>
                <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {analysis.without_aspect_results.map((r, i) => (
                <tr key={i} className="hover:bg-slate-50/70 transition-colors">
                  <td className="px-6 py-3.5 text-slate-600 max-w-sm">
                    <span className="line-clamp-2 leading-relaxed">{r.phrase}</span>
                  </td>
                  <td className="px-6 py-3.5">
                    <SentimentBadge label={r.label} />
                  </td>
                  <td className="px-6 py-3.5">
                    <ScoreBar score={r.score} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
