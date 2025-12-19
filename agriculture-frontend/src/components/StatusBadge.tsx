const styles: Record<string, string> = {
  OK: "bg-green-500/15 text-green-300 border border-green-400/30",
  WARNING: "bg-amber-400/15 text-amber-200 border border-amber-300/40",
  CRITICAL: "bg-red-500/15 text-red-200 border border-red-400/40",
};

export default function StatusBadge({ status }: { status: string }) {
  const tone = styles[status] ?? "bg-slate-500/15 text-slate-200 border border-slate-400/30";

  return (
    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${tone}`}>
      {status}
    </span>
  );
}
