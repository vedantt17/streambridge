import type { ReactNode } from "react";

interface PanelProps {
  title: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function Panel({ title, action, children, className = "" }: PanelProps) {
  return (
    <section className={`rounded-xl border border-white/10 bg-[#081423]/60 shadow-xl shadow-black/20 backdrop-blur-xl ${className}`}>
      <div className="flex min-h-14 items-center justify-between gap-3 border-b border-white/10 px-5 py-3.5">
        <h2 className="font-display text-xl italic leading-[0.95] text-white sm:text-2xl">{title}</h2>
        {action}
      </div>
      <div className="p-5">{children}</div>
    </section>
  );
}
