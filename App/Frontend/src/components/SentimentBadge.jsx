const config = {
  positive: {
    wrapper: 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200',
    dot: 'bg-emerald-500',
    label: 'Positive',
  },
  negative: {
    wrapper: 'bg-rose-50 text-rose-700 ring-1 ring-rose-200',
    dot: 'bg-rose-500',
    label: 'Negative',
  },
  neutral: {
    wrapper: 'bg-amber-50 text-amber-700 ring-1 ring-amber-200',
    dot: 'bg-amber-400',
    label: 'Neutral',
  },
};

export default function SentimentBadge({ label }) {
  const c = config[label?.toLowerCase()] ?? config.neutral;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${c.wrapper}`}>
      <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${c.dot}`} />
      {c.label}
    </span>
  );
}
