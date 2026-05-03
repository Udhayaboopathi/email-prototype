interface ProgressBarProps {
  value: number;
}

export function ProgressBar({ value }: ProgressBarProps) {
  const normalized = Math.max(0, Math.min(100, value));
  return (
    <div className="h-2 w-full rounded-full bg-slate-200 dark:bg-slate-700">
      <div className="h-2 rounded-full bg-brand-600" style={{ width: `${normalized}%` }} />
    </div>
  );
}
