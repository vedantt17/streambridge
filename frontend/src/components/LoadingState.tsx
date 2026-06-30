export function LoadingState({ label = "Loading" }: { label?: string }) {
  return (
    <div className="grid min-h-[18rem] place-items-center rounded-lg border border-line bg-panel/60">
      <div className="flex items-center gap-3 text-sm text-slate-300">
        <span className="h-3 w-3 animate-pulse rounded-full bg-cyan" />
        {label}
      </div>
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-rose-400/40 bg-rose-500/10 p-4 text-sm text-rose-100">
      {message}
    </div>
  );
}
