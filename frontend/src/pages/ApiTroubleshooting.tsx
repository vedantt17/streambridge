import { Play, RadioTower } from "lucide-react";
import { useEffect, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ErrorState, LoadingState } from "../components/LoadingState";
import { PageHeader } from "../components/PageHeader";
import { Panel } from "../components/Panel";
import { StatusBadge } from "../components/StatusBadge";
import { api, formatDate } from "../lib/api";
import type { ApiCheck, PartnerSummary } from "../types";

export default function ApiTroubleshooting() {
  const [partners, setPartners] = useState<PartnerSummary[]>([]);
  const [partnerId, setPartnerId] = useState<number | null>(null);
  const [checks, setChecks] = useState<ApiCheck[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.partners().then((rows) => {
      setPartners(rows);
      setPartnerId(rows[0]?.partner_id ?? null);
    }).catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!partnerId) return;
    api.apiChecks(partnerId).then(setChecks).catch((err) => setError(err.message));
  }, [partnerId]);

  async function runChecks() {
    if (!partnerId) return;
    setBusy(true);
    setError(null);
    try {
      const rows = await api.runApiChecks(partnerId);
      setChecks([...rows, ...checks]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "API check failed");
    } finally {
      setBusy(false);
    }
  }

  if (error) return <ErrorState message={error} />;
  if (!partnerId) return <LoadingState label="Loading API checks" />;

  const chartRows = checks.slice(0, 24).reverse().map((check, index) => ({
    index: index + 1,
    latency_ms: check.latency_ms,
    endpoint: check.endpoint
  }));
  const failures = checks.filter((check) => check.check_status !== "Healthy");

  return (
    <>
      <PageHeader title="API Troubleshooting" eyebrow="Integration Health">
        <select className="h-10 rounded-lg border border-line bg-panel px-3 text-sm text-slate-100" value={partnerId} onChange={(event) => setPartnerId(Number(event.target.value))}>
          {partners.map((partner) => <option key={partner.partner_id} value={partner.partner_id} className="bg-panel">{partner.partner_name}</option>)}
        </select>
        <button className="inline-flex h-10 items-center gap-2 rounded-lg bg-cyan px-3 text-sm font-semibold text-slate-950 disabled:opacity-50" disabled={busy} onClick={runChecks}>
          <Play size={16} />
          Run Checks
        </button>
      </PageHeader>

      <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <Panel title="Latency History">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartRows} margin={{ left: -24, right: 10, top: 10, bottom: 0 }}>
                <CartesianGrid stroke="#263449" strokeDasharray="3 3" />
                <XAxis dataKey="index" stroke="#94a3b8" tickLine={false} />
                <YAxis stroke="#94a3b8" tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "#111827", border: "1px solid #263449", borderRadius: 8 }} />
                <Line type="monotone" dataKey="latency_ms" stroke="#20d3ee" strokeWidth={3} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Top Failures">
          <div className="space-y-3">
            {failures.slice(0, 8).map((check) => (
              <div key={check.check_id} className="rounded-lg border border-line bg-slate-950/35 p-3">
                <div className="flex items-center justify-between gap-2">
                  <RadioTower size={16} className="text-cyan-100" />
                  <StatusBadge status={check.check_status} />
                </div>
                <p className="mt-2 font-semibold text-white">{check.endpoint}</p>
                <p className="text-sm text-slate-400">{check.http_status} | {check.latency_ms}ms | {check.error_message}</p>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <Panel title="Request History" className="mt-5">
        <div className="dashboard-scrollbar overflow-x-auto">
          <table className="w-full min-w-[920px] text-left text-sm">
            <thead className="text-xs uppercase tracking-[0.12em] text-slate-500">
              <tr>
                <th className="pb-3">Endpoint</th>
                <th className="pb-3">Status</th>
                <th className="pb-3">HTTP</th>
                <th className="pb-3">Latency</th>
                <th className="pb-3">Checked</th>
                <th className="pb-3">Error</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line/70">
              {checks.map((check) => (
                <tr key={check.check_id} className="text-slate-300">
                  <td className="py-3 font-semibold text-white">{check.endpoint}</td>
                  <td className="py-3"><StatusBadge status={check.check_status} /></td>
                  <td className="py-3">{check.http_status}</td>
                  <td className="py-3">{check.latency_ms}ms</td>
                  <td className="py-3">{formatDate(check.checked_at)}</td>
                  <td className="py-3">{check.error_message ?? "None"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </>
  );
}
