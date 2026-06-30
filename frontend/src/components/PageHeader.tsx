import type { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  eyebrow: string;
  children?: ReactNode;
}

export function PageHeader({ title, eyebrow, children }: PageHeaderProps) {
  return (
    <div className="mb-5 flex flex-col justify-between gap-4 border-b border-line pb-5 xl:flex-row xl:items-end">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-200">{eyebrow}</p>
        <h1 className="mt-2 text-3xl font-semibold text-white sm:text-4xl">{title}</h1>
      </div>
      {children ? <div className="flex flex-wrap items-center gap-2">{children}</div> : null}
    </div>
  );
}

