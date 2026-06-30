import { ArrowLeft, CheckCircle2, FileJson, RadioTower } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ErrorState, LoadingState } from "../components/LoadingState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { Panel } from "../components/Panel";
import { SeverityBadge, StatusBadge } from "../components/StatusBadge";
import { api, compactRule, formatDate } from "../lib/api";
import type { PartnerDetail as PartnerDetailType } from "../types";

export default function PartnerDetail() {
  const { partnerId } = useParams();
  const [partner, setPartner] = useState<PartnerDetailType | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const id = Number(partnerId);
    if (!Number.isFinite(id)) return;
    api.partner(id).then(setPartner).catch((err) => setError(err.message));
  }, [partnerId]);

  if (error) return <ErrorState message={error} />;
  if (!partner) return <LoadingState label="Loading partner" />;

  return (
    <>
      <PageHeader title={partner.partner_name} eyebrow="Partner Detail">
        <Link to="/partners" className="inline-flex h-10 items-center gap-2 rounded-lg border border-line bg-panel px-3 text-sm font-semibold text-slate-200 hover:text-cyan-100">
          <ArrowLeft size={16} />
          Partners
        </Link>
      </PageHeader>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard icon={CheckCircle2} label="Readiness" value={`${partner.readiness_score}%`} detail={partner.integration_status} />
        <MetricCard icon={FileJson} label="Feeds" value={partner.feeds.length} detail={partner.last_feed_status} />
        <MetricCard icon={RadioTower} label="API Checks" value={partner.api_checks.length} detail="Recent endpoint history" />
        <MetricCard icon={CheckCircle2} label="SLA Age" value={`${partner.sla_age_days}d`} detail={`${partner.open_blocker_count} open blockers`} />
      </div>

      <div className="mt-5 grid gap-5 xl:grid-cols-[0.95fr_1.05fr]">
        <Panel title="Open Issues">
          <div className="space-y-3">
            {partner.open_issues.slice(0, 7).map((issue) => (
              <div key={issue.error_id} className="rounded-lg border border-line bg-slate-950/30 p-3">
                <div className="flex flex-wrap items-center gap-2">
                  <SeverityBadge severity={issue.severity} />
                  <span className="text-sm font-semibold text-white">{compactRule(issue.rule_name)}</span>
                </div>
                <p className="mt-2 text-sm text-slate-400">{issue.error_message}</p>
              </div>
            ))}
            {partner.open_issues.length === 0 ? <p className="text-sm text-slate-400">No open issues.</p> : null}
          </div>
        </Panel>

        <Panel title="Onboarding Tasks">
          <div className="dashboard-scrollbar overflow-x-auto">
            <table className="w-full min-w-[680px] text-left text-sm">
              <thead className="text-xs uppercase tracking-[0.12em] text-slate-500">
                <tr>
                  <th className="pb-3">Task</th>
                  <th className="pb-3">Owner</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3">Due</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line/70">
                {partner.onboarding_tasks.map((task) => (
                  <tr key={task.task_id} className="text-slate-300">
                    <td className="py-3 font-medium text-white">{task.task_name}</td>
                    <td className="py-3">{task.owner}</td>
                    <td className="py-3">
                      <StatusBadge status={task.status} />
                    </td>
                    <td className="py-3">{formatDate(task.due_date)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>

      <div className="mt-5 grid gap-5 xl:grid-cols-2">
        <Panel title="Feed History">
          <div className="space-y-3">
            {partner.feeds.map((feed) => (
              <div key={feed.feed_id} className="flex items-center justify-between gap-3 border-b border-line/70 pb-3 last:border-0 last:pb-0">
                <div>
                  <p className="font-semibold text-white">{feed.file_name}</p>
                  <p className="text-xs text-slate-500">{formatDate(feed.uploaded_at)}</p>
                </div>
                <StatusBadge status={feed.parse_status} />
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="API Checks">
          <div className="space-y-3">
            {partner.api_checks.slice(0, 8).map((check) => (
              <div key={check.check_id} className="flex items-center justify-between gap-3 border-b border-line/70 pb-3 last:border-0 last:pb-0">
                <div>
                  <p className="font-semibold text-white">{check.endpoint}</p>
                  <p className="text-xs text-slate-500">{check.http_status} | {check.latency_ms}ms</p>
                </div>
                <StatusBadge status={check.check_status} />
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </>
  );
}
