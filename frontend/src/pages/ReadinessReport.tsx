import { ClipboardCheck, FileDown, Gauge } from "lucide-react";
import { useEffect, useState } from "react";
import { ErrorState, LoadingState } from "../components/LoadingState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { Panel } from "../components/Panel";
import { api, compactRule } from "../lib/api";
import type { Checklist, PartnerSummary, ReadinessScore, TroubleshootingSummary } from "../types";

export default function ReadinessReport() {
  const [partners, setPartners] = useState<PartnerSummary[]>([]);
  const [partnerId, setPartnerId] = useState<number | null>(null);
  const [readiness, setReadiness] = useState<ReadinessScore | null>(null);
  const [checklist, setChecklist] = useState<Checklist | null>(null);
  const [summary, setSummary] = useState<TroubleshootingSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.partners().then((rows) => {
      setPartners(rows);
      setPartnerId(rows[0]?.partner_id ?? null);
    }).catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!partnerId) return;
    Promise.all([api.readiness(partnerId), api.checklist(partnerId), api.summary(partnerId)])
      .then(([score, checklistData, summaryData]) => {
        setReadiness(score);
        setChecklist(checklistData);
        setSummary(summaryData);
      })
      .catch((err) => setError(err.message));
  }, [partnerId]);

  if (error) return <ErrorState message={error} />;
  if (!readiness || !checklist || !summary || !partnerId) return <LoadingState label="Loading readiness report" />;

  const metrics = [
    ["Valid Content", readiness.valid_content_pct],
    ["Artwork", readiness.artwork_completion_pct],
    ["Entitlement", readiness.entitlement_completion_pct],
    ["API Health", readiness.api_health_score]
  ] as const;

  return (
    <>
      <PageHeader title="Readiness Report" eyebrow="Launch Sign-Off">
        <select className="h-10 rounded-lg border border-line bg-panel px-3 text-sm text-slate-100" value={partnerId} onChange={(event) => setPartnerId(Number(event.target.value))}>
          {partners.map((partner) => <option key={partner.partner_id} value={partner.partner_id} className="bg-panel">{partner.partner_name}</option>)}
        </select>
        <button className="inline-flex h-10 items-center gap-2 rounded-lg border border-line bg-panel px-3 text-sm font-semibold text-slate-200 hover:text-cyan-100" onClick={() => window.open(`http://127.0.0.1:8000/api/partners/${partnerId}/integration-checklist`, "_blank")}>
          <FileDown size={16} />
          Export
        </button>
      </PageHeader>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard icon={Gauge} label="Readiness" value={`${readiness.readiness_score}%`} detail={checklist.launch_status} />
        <MetricCard icon={ClipboardCheck} label="Critical" value={readiness.critical_count} detail="Launch blockers" />
        <MetricCard icon={ClipboardCheck} label="High" value={readiness.high_count} detail="Partner action needed" />
        <MetricCard icon={Gauge} label="API" value={`${readiness.api_health_score}%`} detail="Recent checks" />
      </div>

      <div className="mt-5 grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <Panel title="Readiness Metrics">
          <div className="grid gap-4">
            {metrics.map(([label, value]) => (
              <div key={label}>
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span className="font-semibold text-slate-200">{label}</span>
                  <span className="text-slate-400">{value}%</span>
                </div>
                <div className="h-3 overflow-hidden rounded-md bg-slate-950">
                  <div className="h-full rounded-md bg-cyan" style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Troubleshooting Summary">
          <p className="text-base leading-7 text-slate-200">{summary.summary}</p>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {summary.top_categories.map(([category, count]) => (
              <div key={category} className="rounded-lg border border-line bg-slate-950/35 p-3">
                <p className="text-sm font-semibold text-white">{category}</p>
                <p className="mt-1 text-2xl font-semibold text-cyan-100">{count}</p>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <div className="mt-5 grid gap-5 xl:grid-cols-2">
        <Panel title="Integration Checklist">
          <ul className="grid gap-3">
            {checklist.required_before_go_live.map((item) => (
              <li key={item} className="rounded-lg border border-line bg-slate-950/35 px-3 py-2 text-sm text-slate-300">
                {item}
              </li>
            ))}
          </ul>
        </Panel>

        <Panel title="Required Fixes">
          <div className="grid gap-3">
            {checklist.current_blockers.top_rules.map(([rule, count]) => (
              <div key={rule} className="flex items-center justify-between border-b border-line/70 pb-3 last:border-0 last:pb-0">
                <span className="font-semibold text-white">{compactRule(rule)}</span>
                <span className="rounded-md border border-cyan-300/30 bg-cyan-400/10 px-2 py-1 text-sm text-cyan-100">{count}</span>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </>
  );
}

