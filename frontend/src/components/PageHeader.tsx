import type { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  eyebrow: string;
  children?: ReactNode;
}

export function PageHeader({ title, eyebrow, children }: PageHeaderProps) {
  return (
    <div className="mb-7 flex flex-col justify-between gap-5 border-b border-white/10 pb-7 xl:flex-row xl:items-end">
      <div>
        <p className="text-[0.7rem] font-bold uppercase tracking-[0.26em] text-cyan-100/80">{eyebrow}</p>
        <h1 className="mt-2 max-w-5xl font-display text-5xl italic leading-[0.95] text-white sm:text-6xl xl:text-7xl">
          {title}
        </h1>
      </div>
      {children ? <div className="flex flex-wrap items-center gap-2">{children}</div> : null}
    </div>
  );
}
