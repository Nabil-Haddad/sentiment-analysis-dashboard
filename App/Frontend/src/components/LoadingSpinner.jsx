export default function LoadingSpinner({ size = 'md', label }) {
  const sizes = { sm: 'w-4 h-4 border-2', md: 'w-8 h-8 border-2', lg: 'w-12 h-12 border-4' };
  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div className={`${sizes[size]} border-slate-200 border-t-blue-600 rounded-full animate-spin`} />
      {label && <p className="text-sm text-slate-500">{label}</p>}
    </div>
  );
}
