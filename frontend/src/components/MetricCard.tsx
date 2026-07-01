import type { LucideIcon } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string | number;
  detail?: string;
  icon: LucideIcon;
}

export function MetricCard({ label, value, detail, icon: Icon }: MetricCardProps) {
  return (
    <section className="rounded-xl border border-white/10 bg-[#081423]/60 p-5 shadow-xl shadow-black/20 backdrop-blur-xl transition duration-200 hover:-translate-y-0.5 hover:bg-[#0a1828]/70">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-[0.68rem] font-bold uppercase tracking-[0.2em] text-cyan-100/70">{label}</p>
          <p className="mt-2 font-display text-5xl italic leading-none text-white">{value}</p>
        </div>
        <span className="grid h-10 w-10 place-items-center rounded-lg border border-cyan-200/30 bg-white/10 text-cyan-100">
          <Icon size={20} />
        </span>
      </div>
      {detail ? <p className="mt-4 text-sm leading-6 text-slate-300/80">{detail}</p> : null}
    </section>
  );
}
