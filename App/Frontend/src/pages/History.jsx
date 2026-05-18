import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Trash2, ExternalLink, Clock } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { getAllAnalyses, deleteAnalysis } from '../api/analysis';

export default function History() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleting, setDeleting] = useState(null);
  const [confirmId, setConfirmId] = useState(null);

  useEffect(() => {
    getAllAnalyses()
      .then((res) => setAnalyses(res.data))
      .catch((err) => {
        if (err.response?.status === 404) setAnalyses([]);
        else setError('Failed to load history.');
      })
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (id) => {
    setDeleting(id);
    try {
      await deleteAnalysis(id);
      setAnalyses((prev) => prev.filter((a) => a.analysis_id !== id));
    } catch {
      setError('Failed to delete analysis.');
    } finally {
      setDeleting(null);
      setConfirmId(null);
    }
  };

  return (
    <div className="space-y-6">
      <p className="text-sm text-slate-500">All past analyses with their results</p>

      {error && (
        <div className="bg-rose-50 border border-rose-200 text-rose-600 text-sm px-4 py-3 rounded-xl">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-20">
          <LoadingSpinner size="md" label="Loading history..." />
        </div>
      ) : analyses.length === 0 ? (
        <div className="bg-white rounded-2xl border border-dashed border-slate-300 shadow-sm">
          <EmptyState
            title="No analyses yet"
            description="Submit your first batch of comments to see results here."
            action={
              <Link
                to="/new"
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white text-sm font-semibold rounded-xl hover:bg-blue-700 transition-colors"
              >
                Run analysis
              </Link>
            }
          />
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50">
                <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">ID</th>
                <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Date & Time</th>
                <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Aspect</th>
                <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Other</th>
                <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Total</th>
                <th className="px-6 py-3.5 text-right text-xs font-semibold text-slate-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {analyses.map((a) => (
                <tr key={a.analysis_id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="px-6 py-4 font-bold text-slate-700">#{a.analysis_id}</td>
                  <td className="px-6 py-4 text-slate-500">
                    <div className="flex items-center gap-1.5">
                      <Clock size={13} className="text-slate-300 flex-shrink-0" />
                      {new Date(a.created_at).toLocaleString()}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 ring-1 ring-blue-200">
                      {a.aspect_results.length}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-600">
                      {a.without_aspect_results.length}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-500 tabular-nums font-medium">
                    {a.aspect_results.length + a.without_aspect_results.length}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-end gap-1.5">
                      <Link
                        to={`/analysis/${a.analysis_id}`}
                        className="inline-flex items-center gap-1.5 text-xs text-blue-600 hover:text-blue-700 font-semibold px-2.5 py-1.5 rounded-lg hover:bg-blue-50 transition-colors"
                      >
                        <ExternalLink size={12} />
                        View
                      </Link>

                      {confirmId === a.analysis_id ? (
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => handleDelete(a.analysis_id)}
                            disabled={deleting === a.analysis_id}
                            className="text-xs text-white bg-rose-500 hover:bg-rose-600 font-semibold px-2.5 py-1.5 rounded-lg transition-colors disabled:opacity-60"
                          >
                            {deleting === a.analysis_id ? 'Deleting…' : 'Confirm'}
                          </button>
                          <button
                            onClick={() => setConfirmId(null)}
                            className="text-xs text-slate-500 hover:text-slate-700 px-2.5 py-1.5 rounded-lg hover:bg-slate-100 transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setConfirmId(a.analysis_id)}
                          className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-rose-600 font-semibold px-2.5 py-1.5 rounded-lg hover:bg-rose-50 transition-colors"
                        >
                          <Trash2 size={12} />
                          Delete
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="px-6 py-3 border-t border-slate-100 bg-slate-50">
            <p className="text-xs text-slate-400 font-medium">
              {analyses.length} analysis{analyses.length !== 1 ? 'es' : ''} total
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
