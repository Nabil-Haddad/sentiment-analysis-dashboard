import { useState, useEffect } from 'react';
import { Plus, Trash2, Tag, AlertTriangle } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import { getAspects, addAspect, toggleAspect, deleteAspect } from '../api/aspects';

function Toggle({ checked, onChange, disabled }) {
  return (
    <button
      type="button"
      onClick={onChange}
      disabled={disabled}
      aria-checked={checked}
      role="switch"
      className={`relative inline-flex h-5 w-9 flex-shrink-0 items-center rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-1 ${
        checked ? 'bg-blue-600' : 'bg-slate-200'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
    >
      <span
        className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow-sm transition-transform duration-200 ${
          checked ? 'translate-x-[19px]' : 'translate-x-[3px]'
        }`}
      />
    </button>
  );
}

export default function Aspects() {
  const [aspects, setAspects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [newName, setNewName] = useState('');
  const [adding, setAdding] = useState(false);
  const [addError, setAddError] = useState(null);

  const [togglingId, setTogglingId] = useState(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    getAspects()
      .then((res) => setAspects(res.data))
      .catch(() => setError('Failed to load aspects. Make sure the server is running.'))
      .finally(() => setLoading(false));
  }, []);

  async function handleAdd(e) {
    e.preventDefault();
    const name = newName.trim().toLowerCase();
    if (!name) return;

    setAdding(true);
    setAddError(null);
    try {
      const res = await addAspect(name);
      setAspects((prev) => [res.data, ...prev]);
      setNewName('');
    } catch (err) {
      setAddError(err.response?.data?.detail || 'Failed to add aspect.');
    } finally {
      setAdding(false);
    }
  }

  async function handleToggle(aspect) {
    setTogglingId(aspect.aspect_id);
    const next = !aspect.is_active;
    setAspects((prev) =>
      prev.map((a) => (a.aspect_id === aspect.aspect_id ? { ...a, is_active: next } : a))
    );
    try {
      await toggleAspect(aspect.aspect_id, next);
    } catch {
      setAspects((prev) =>
        prev.map((a) => (a.aspect_id === aspect.aspect_id ? { ...a, is_active: !next } : a))
      );
      setError('Failed to update aspect status.');
    } finally {
      setTogglingId(null);
    }
  }

  async function handleDelete(aspect_id) {
    setDeletingId(aspect_id);
    setConfirmDeleteId(null);
    try {
      await deleteAspect(aspect_id);
      setAspects((prev) => prev.filter((a) => a.aspect_id !== aspect_id));
    } catch {
      setError('Failed to delete aspect.');
    } finally {
      setDeletingId(null);
    }
  }

  const activeCount = aspects.filter((a) => a.is_active).length;
  const sorted = [...aspects].sort((a, b) => Number(b.is_active) - Number(a.is_active));

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="md" label="Loading aspects..." />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl">

      {/* Subtitle + active count */}
      <div className="flex items-start justify-between gap-4">
        <p className="text-sm text-slate-500">
          Aspects define which topics are detected and tracked during sentiment analysis.
          Only active aspects are used when you run a new analysis.
        </p>
        <span className="flex-shrink-0 inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full bg-blue-50 text-blue-700 ring-1 ring-blue-200">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-500 flex-shrink-0" />
          {activeCount} of {aspects.length} active
        </span>
      </div>

      {/* Page-level error */}
      {error && (
        <div className="bg-rose-50 border border-rose-200 text-rose-600 text-sm px-4 py-3 rounded-xl flex items-center justify-between gap-3">
          <span>{error}</span>
          <button
            onClick={() => setError(null)}
            className="text-rose-400 hover:text-rose-600 font-semibold text-xs flex-shrink-0"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Warning: no active aspects */}
      {!loading && activeCount === 0 && aspects.length > 0 && (
        <div className="flex items-start gap-3 bg-amber-50 border border-amber-200 px-4 py-3.5 rounded-xl">
          <AlertTriangle size={15} className="flex-shrink-0 mt-0.5 text-amber-500" />
          <p className="text-sm text-amber-800">
            No aspects are currently active. Your next analysis will not detect any
            aspect-level sentiment. Enable at least one aspect below.
          </p>
        </div>
      )}

      {/* Add aspect form */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 bg-slate-50">
          <p className="text-sm font-bold text-slate-700">Add Aspect</p>
        </div>
        <form onSubmit={handleAdd} className="px-6 py-4 flex items-start gap-3">
          <div className="flex-1">
            <input
              type="text"
              value={newName}
              onChange={(e) => {
                setNewName(e.target.value);
                setAddError(null);
              }}
              placeholder="e.g. battery, speed, packaging…"
              maxLength={50}
              disabled={adding}
              className="w-full px-4 py-2.5 text-sm text-slate-700 placeholder-slate-300 border border-slate-200 rounded-xl outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all disabled:opacity-60"
            />
            {addError && (
              <p className="text-xs text-rose-500 mt-1.5 px-0.5">{addError}</p>
            )}
          </div>
          <button
            type="submit"
            disabled={adding || !newName.trim()}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white text-sm font-semibold rounded-xl hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-sm flex-shrink-0"
          >
            {adding ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <Plus size={15} />
            )}
            Add
          </button>
        </form>
      </div>

      {/* Aspects list */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2.5">
          <p className="text-sm font-bold text-slate-700">All Aspects</p>
          <span className="text-xs text-slate-500 bg-slate-200 px-2 py-0.5 rounded-full font-semibold">
            {aspects.length}
          </span>
        </div>

        {sorted.length === 0 ? (
          <div className="py-16 flex flex-col items-center gap-3">
            <div className="w-12 h-12 bg-slate-100 rounded-2xl flex items-center justify-center">
              <Tag size={20} className="text-slate-400" />
            </div>
            <p className="text-sm font-semibold text-slate-500">No aspects yet</p>
            <p className="text-xs text-slate-400">Add your first aspect above to get started.</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100">
                <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Aspect
                </th>
                <th className="text-left px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3.5 text-xs font-semibold text-slate-400 uppercase tracking-wider text-center">
                  Enable
                </th>
                <th className="px-6 py-3.5" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sorted.map((aspect) => {
                const isToggling = togglingId === aspect.aspect_id;
                const isDeleting = deletingId === aspect.aspect_id;
                const isConfirming = confirmDeleteId === aspect.aspect_id;
                const isBusy = isToggling || isDeleting;

                return (
                  <tr
                    key={aspect.aspect_id}
                    className={`transition-colors ${
                      aspect.is_active ? 'hover:bg-slate-50/70' : 'bg-slate-50/50 hover:bg-slate-50'
                    }`}
                  >
                    {/* Name */}
                    <td className="px-6 py-3.5">
                      <span
                        className={`inline-flex px-2.5 py-1 text-xs font-semibold rounded-full ring-1 ${
                          aspect.is_active
                            ? 'bg-blue-50 text-blue-700 ring-blue-200'
                            : 'bg-slate-100 text-slate-400 ring-slate-200'
                        }`}
                      >
                        {aspect.name}
                      </span>
                    </td>

                    {/* Status label */}
                    <td className="px-6 py-3.5">
                      <span
                        className={`text-xs font-semibold ${
                          aspect.is_active ? 'text-emerald-600' : 'text-slate-400'
                        }`}
                      >
                        {isToggling ? 'Saving…' : aspect.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>

                    {/* Toggle */}
                    <td className="px-6 py-3.5 text-center">
                      <Toggle
                        checked={aspect.is_active}
                        onChange={() => handleToggle(aspect)}
                        disabled={isBusy}
                      />
                    </td>

                    {/* Delete */}
                    <td className="px-6 py-3.5 text-right">
                      {isDeleting ? (
                        <div className="inline-flex justify-center items-center w-20 h-7">
                          <div className="w-4 h-4 border-2 border-slate-200 border-t-rose-400 rounded-full animate-spin" />
                        </div>
                      ) : isConfirming ? (
                        <div className="inline-flex items-center gap-1.5">
                          <button
                            onClick={() => handleDelete(aspect.aspect_id)}
                            className="text-xs text-white bg-rose-500 hover:bg-rose-600 font-semibold px-2.5 py-1.5 rounded-lg transition-colors"
                          >
                            Confirm
                          </button>
                          <button
                            onClick={() => setConfirmDeleteId(null)}
                            className="text-xs text-slate-500 hover:text-slate-700 px-2.5 py-1.5 rounded-lg hover:bg-slate-100 transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setConfirmDeleteId(aspect.aspect_id)}
                          disabled={isBusy}
                          className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-rose-500 font-semibold px-2.5 py-1.5 rounded-lg hover:bg-rose-50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                        >
                          <Trash2 size={13} />
                          Delete
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}

        {sorted.length > 0 && (
          <div className="px-6 py-3 border-t border-slate-100 bg-slate-50">
            <p className="text-xs text-slate-400 font-medium">
              {activeCount} active · {aspects.length - activeCount} inactive ·
              Changes take effect on your next analysis
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
