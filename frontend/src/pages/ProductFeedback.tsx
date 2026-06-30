import { Lightbulb, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ErrorState, LoadingState } from "../components/LoadingState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { Panel } from "../components/Panel";
import { api, compactRule } from "../lib/api";
import type { ProductFeedbackReport } from "../types";

const colors = ["#20d3ee", "#34d399", "#f59e0b", "#fb7185", "#a78bfa", "#f97316"];

export default function ProductFeedback() {
  const [report, setReport] = useState<ProductFeedbackReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.productFeedback().then(setReport).catch((err) => setError(err.message));
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!report) return <LoadingState label="Loading product feedback" />;

  const validationRows = report.top_validation_failures.map(([name, value]) => ({ name: compactRule(name), value }));
  const partnerRows = report.partners_with_repeated_blockers.map((row) => ({ name: row.partner, value: row.blockers }));

  return (
    <>
      <PageHeader title="Product Feedback" eyebrow="Recurring Integration Trends" />

      <div className="grid gap-4 md:grid-cols-2">
        <MetricCard icon={TrendingUp} label="Validation Patterns" value={report.top_validation_failures.length} detail="Recurring rule failures" />
        <MetricCard icon={Lightbulb} label="Self-Service Ideas" value={report.suggested_self_service_features.length} detail="Prioritized workflow improvements" />
      </div>

      <div className="mt-5 grid gap-5 xl:grid-cols-2">
        <Panel title="Top Validation Failures">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={validationRows} layout="vertical" margin={{ left: 74, right: 16, top: 8, bottom: 8 }}>
                <CartesianGrid stroke="#263449" strokeDasharray="3 3" />
                <XAxis type="number" stroke="#94a3b8" tickLine={false} axisLine={false} />
                <YAxis dataKey="name" type="category" width={140} stroke="#94a3b8" tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "#111827", border: "1px solid #263449", borderRadius: 8 }} />
                <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                  {validationRows.map((_, index) => <Cell key={index} fill={colors[index % colors.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Partners With Repeated Blockers">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={partnerRows} margin={{ left: -18, right: 12, top: 8, bottom: 64 }}>
                <CartesianGrid stroke="#263449" strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-30} textAnchor="end" interval={0} stroke="#94a3b8" tickLine={false} height={80} />
                <YAxis stroke="#94a3b8" tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "#111827", border: "1px solid #263449", borderRadius: 8 }} />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {partnerRows.map((_, index) => <Cell key={index} fill={colors[index % colors.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <div className="mt-5 grid gap-5 xl:grid-cols-2">
        <Panel title="Suggested Self-Service Features">
          <div className="grid gap-3">
            {report.suggested_self_service_features.map((item) => (
              <div key={item} className="rounded-lg border border-line bg-slate-950/35 p-3 text-sm font-semibold text-white">
                {item}
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Recommended Product Improvements">
          <div className="grid gap-3">
            {report.recommended_product_improvements.map((item) => (
              <div key={item} className="rounded-lg border border-line bg-slate-950/35 p-3 text-sm leading-6 text-slate-300">
                {item}
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </>
  );
}
