import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Send, RotateCcw, ChevronRight, Sparkles } from 'lucide-react';
import SentimentBadge from '../components/SentimentBadge';
import { submitAnalysis } from '../api/analysis';

const ScoreBar = ({ score }) => (
  <div className="flex items-center gap-2">
    <div className="w-20 h-1.5 bg-slate-100 rounded-full overflow-hidden">
      <div
        className="h-full bg-blue-500 rounded-full transition-all"
        style={{ width: `${Math.round(score * 100)}%` }}
      />
    </div>
    <span className="text-xs text-slate-500 tabular-nums w-8">{Math.round(score * 100)}%</span>
  </div>
);

export default function NewAnalysis() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const comments = text.split('\n').map((c) => c.trim()).filter(Boolean);

  const handleSubmit = async () => {
    if (comments.length === 0) return;
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const res = await submitAnalysis(comments);
      setResults(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResults(null);
    setError(null);
    setText('');
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <p className="text-sm text-slate-500">
        Enter one comment per line — complex sentences with "but" and "however" are split automatically
      </p>

      {/* Input card */}
      {!results && (
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50">
            <p className="text-sm font-bold text-slate-700">Comments</p>
            {comments.length > 0 && (
              <span className="text-xs bg-blue-50 text-blue-600 font-semibold px-2.5 py-1 rounded-full ring-1 ring-blue-200">
                {comments.length} comment{comments.length !== 1 ? 's' : ''}
              </span>
            )}
          </div>

          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => { if (e.ctrlKey && e.key === 'Enter') handleSubmit(); }}
            placeholder={
              'The design is beautiful but the price is too high.\nThe staff and service are amazing.\nI really loved the overall experience.\nThe delivery was fast however the packaging looked damaged.'
            }
            className="w-full px-6 py-5 text-sm text-slate-700 placeholder-slate-300 resize-none outline-none font-mono leading-relaxed"
            rows={10}
            disabled={loading}
          />

          <div className="px-6 py-3.5 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
            <p className="text-xs text-slate-400">
              One comment per line ·{' '}
              <kbd className="font-sans bg-white border border-slate-200 text-slate-500 px-1.5 py-0.5 rounded text-xs">Ctrl</kbd>
              {' + '}
              <kbd className="font-sans bg-white border border-slate-200 text-slate-500 px-1.5 py-0.5 rounded text-xs">↵</kbd>
              {' to submit'}
            </p>
            <button
              onClick={handleSubmit}
              disabled={loading || comments.length === 0}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white text-sm font-semibold rounded-xl hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-sm"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Send size={14} />
                  Analyze
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Loading overlay */}
      {loading && (
        <div className="bg-white rounded-2xl border border-slate-200 py-16 flex flex-col items-center gap-4 shadow-sm">
          <div className="w-10 h-10 border-2 border-slate-200 border-t-blue-600 rounded-full animate-spin" />
          <div className="text-center">
            <p className="text-sm font-semibold text-slate-700">Running analysis</p>
            <p className="text-xs text-slate-400 mt-1">The model is processing your comments…</p>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-rose-50 border border-rose-200 text-rose-600 text-sm px-4 py-3 rounded-xl">
          {error}
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="space-y-5">
          {/* Success banner */}
          <div className="bg-emerald-50 border border-emerald-200 rounded-2xl px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center flex-shrink-0">
                <Sparkles size={17} className="text-white" />
              </div>
              <div>
                <p className="text-sm font-bold text-emerald-800">
                  Analysis complete · #{results.analysis_id}
                </p>
                <p className="text-xs text-emerald-600 mt-0.5">
                  {results.ResultsAspect.length} aspect-based · {results.ResultsWithoutAspect.length} other
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Link
                to={`/analysis/${results.analysis_id}`}
                className="inline-flex items-center gap-1 text-xs text-emerald-700 hover:text-emerald-900 font-semibold"
              >
                Saved view <ChevronRight size={12} />
              </Link>
              <button
                onClick={handleReset}
                className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800 px-3 py-1.5 rounded-lg bg-white border border-slate-200 hover:border-slate-300 transition-all font-medium"
              >
                <RotateCcw size={12} />
                New
              </button>
            </div>
          </div>

          {/* Aspect-based results */}
          {results.ResultsAspect.length > 0 && (
            <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
              <div className="px-6 py-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
                <p className="text-sm font-bold text-slate-700">Aspect-Based Results</p>
                <span className="text-xs text-slate-500 bg-slate-200 px-2 py-0.5 rounded-full font-semibold">
                  {results.ResultsAspect.length}
                </span>
              </div>
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
                  {results.ResultsAspect.map((r, i) => (
                    <tr key={i} className="hover:bg-slate-50/70 transition-colors">
                      <td className="px-6 py-3.5 text-slate-600 max-w-xs">
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
            </div>
          )}

          {/* Without-aspect results */}
          {results.ResultsWithoutAspect.length > 0 && (
            <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
              <div className="px-6 py-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
                <p className="text-sm font-bold text-slate-700">Other Results</p>
                <span className="text-xs text-slate-500 bg-slate-200 px-2 py-0.5 rounded-full font-semibold">
                  {results.ResultsWithoutAspect.length}
                </span>
                <span className="text-xs text-slate-400">· no aspect detected</span>
              </div>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Phrase</th>
                    <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Sentiment</th>
                    <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Confidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {results.ResultsWithoutAspect.map((r, i) => (
                    <tr key={i} className="hover:bg-slate-50/70 transition-colors">
                      <td className="px-6 py-3.5 text-slate-600 max-w-xs">
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
            </div>
          )}
        </div>
      )}
    </div>
  );
}
