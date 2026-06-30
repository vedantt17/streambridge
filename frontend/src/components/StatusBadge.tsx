import type { SeverityName, StatusName } from "../types";

const statusStyles: Record<string, string> = {
  Draft: "border-slate-500/50 bg-slate-500/10 text-slate-200",
  Testing: "border-cyan-400/50 bg-cyan-400/10 text-cyan-100",
  Blocked: "border-rose-400/50 bg-rose-500/15 text-rose-100",
  Ready: "border-emerald-400/50 bg-emerald-500/15 text-emerald-100",
  Live: "border-teal-400/50 bg-teal-500/15 text-teal-100",
  Open: "border-rose-400/50 bg-rose-500/15 text-rose-100",
  "In Review": "border-amber-300/50 bg-amber-400/15 text-amber-100",
  "Partner Action Needed": "border-orange-300/50 bg-orange-400/15 text-orange-100",
  Resolved: "border-emerald-400/50 bg-emerald-500/15 text-emerald-100",
  Parsed: "border-emerald-400/50 bg-emerald-500/15 text-emerald-100",
  Pending: "border-slate-500/50 bg-slate-500/10 text-slate-200",
  Failed: "border-rose-400/50 bg-rose-500/15 text-rose-100",
  Healthy: "border-emerald-400/50 bg-emerald-500/15 text-emerald-100"
};

const severityStyles: Record<string, string> = {
  Critical: "border-red-400/60 bg-red-500/15 text-red-100",
  High: "border-orange-400/60 bg-orange-500/15 text-orange-100",
  Medium: "border-amber-300/60 bg-amber-400/15 text-amber-100",
  Low: "border-sky-300/60 bg-sky-400/15 text-sky-100"
};

export function StatusBadge({ status }: { status: StatusName }) {
  return (
    <span className={`inline-flex min-w-[4.75rem] justify-center rounded-md border px-2 py-1 text-xs font-semibold ${statusStyles[status] ?? statusStyles.Draft}`}>
      {status}
    </span>
  );
}

export function SeverityBadge({ severity }: { severity: SeverityName }) {
  return (
    <span className={`inline-flex min-w-[4.5rem] justify-center rounded-md border px-2 py-1 text-xs font-semibold ${severityStyles[severity] ?? severityStyles.Low}`}>
      {severity}
    </span>
  );
}
