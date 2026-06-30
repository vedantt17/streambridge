import { AlertTriangle, Gauge, RadioTower, Users } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Link } from "react-router-dom";
import { ErrorState, LoadingState } from "../components/LoadingState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { Panel } from "../components/Panel";
import { StatusBadge } from "../components/StatusBadge";
import { api, compactRule, formatDate, toChartRows } from "../lib/api";
import type { DashboardSummary } from "../types";

const chartColors = ["#20d3ee", "#f59e0b", "#fb7185", "#34d399", "#a78bfa", "#f97316"];

export default function Dashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.dashboard().then(setData).catch((err) => setError(err.message));
  }, []);

  const categoryRows = useMemo(() => toChartRows(data?.category_counts), [data]);
  const statusRows = useMemo(() => toChartRows(data?.status_counts), [data]);

  if (error) return <ErrorState message={error} />;
  if (!data) return <LoadingState label="Loading dashboard" />;

  return (
    <>
      <PageHeader title="Partner Onboarding Dashboard" eyebrow="Launch Operations" />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard icon={Users} label="Partners" value={data.partner_count} detail="Active partner integrations" />
        <MetricCard icon={Gauge} label="Avg Readiness" value={`${data.average_readiness_score}%`} detail="Latest score per partner" />
        <MetricCard icon={AlertTriangle} label="Open Blockers" value={data.open_blockers} detail="Active validation issues" />
        <MetricCard icon={RadioTower} label="API Health" value={`${data.api_health_pct}%`} detail="Recent integration checks" />
      </div>

      <div className="mt-5 grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <Panel title="Issue Trend">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.issue_trend} margin={{ left: -24, right: 10, top: 10, bottom: 0 }}>
                <CartesianGrid stroke="#263449" strokeDasharray="3 3" />
                <XAxis dataKey="date" tickFormatter={(value) => value.slice(5)} stroke="#94a3b8" tickLine={false} />
                <YAxis stroke="#94a3b8" tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "#111827", border: "1px solid #263449", borderRadius: 8 }} />
                <Line type="monotone" dataKey="issues" stroke="#20d3ee" strokeWidth={3} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Issue Mix">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryRows} layout="vertical" margin={{ left: 24, right: 12, top: 8, bottom: 8 }}>
                <CartesianGrid stroke="#263449" strokeDasharray="3 3" />
                <XAxis type="number" stroke="#94a3b8" tickLine={false} axisLine={false} />
                <YAxis dataKey="name" type="category" width={92} stroke="#94a3b8" tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "#111827", border: "1px solid #263449", borderRadius: 8 }} />
                <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                  {categoryRows.map((_, index) => (
                    <Cell key={index} fill={chartColors[index % chartColors.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <div className="mt-5 grid gap-5 xl:grid-cols-[0.75fr_1.25fr]">
        <Panel title="Integration Status">
          <div className="grid gap-3">
            {statusRows.map((row) => (
              <div key={row.name} className="flex items-center justify-between border-b border-line/70 pb-3 last:border-0 last:pb-0">
                <StatusBadge status={row.name} />
                <span className="text-2xl font-semibold text-white">{row.value}</span>
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Partner Launch Board">
          <div className="dashboard-scrollbar overflow-x-auto">
            <table className="w-full min-w-[900px] text-left text-sm">
              <thead className="text-xs uppercase tracking-[0.12em] text-slate-500">
                <tr>
                  <th className="pb-3 font-semibold">Partner</th>
                  <th className="pb-3 font-semibold">Status</th>
                  <th className="pb-3 font-semibold">Readiness</th>
                  <th className="pb-3 font-semibold">Blockers</th>
                  <th className="pb-3 font-semibold">SLA Age</th>
                  <th className="pb-3 font-semibold">Last Upload</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line/70">
                {data.partner_cards.map((partner) => (
                  <tr key={partner.partner_id} className="text-slate-300">
                    <td className="py-3">
                      <Link className="font-semibold text-white hover:text-cyan-100" to={`/partners/${partner.partner_id}`}>
                        {partner.partner_name}
                      </Link>
                    </td>
                    <td className="py-3">
                      <StatusBadge status={partner.integration_status} />
                    </td>
                    <td className="py-3">{partner.readiness_score}%</td>
                    <td className="py-3">{partner.open_blocker_count}</td>
                    <td className="py-3">{partner.sla_age_days}d</td>
                    <td className="py-3">{formatDate(partner.last_feed_upload)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>

      <Panel title="Recurring Failures" className="mt-5">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {data.top_recurring_failures.map(([rule, count]) => (
            <div key={rule} className="rounded-lg border border-line bg-slate-950/35 p-4">
              <p className="text-sm font-semibold text-white">{compactRule(rule)}</p>
              <p className="mt-2 text-2xl font-semibold text-cyan-100">{count}</p>
            </div>
          ))}
        </div>
      </Panel>
    </>
  );
}

