import { RefreshCw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { ErrorState, LoadingState } from "../components/LoadingState";
import { PageHeader } from "../components/PageHeader";
import { Panel } from "../components/Panel";
import { SeverityBadge, StatusBadge } from "../components/StatusBadge";
import { api, compactRule } from "../lib/api";
import type { PartnerSummary, ValidationIssue } from "../types";

const severities = ["", "Critical", "High", "Medium", "Low"];
const statuses = ["", "Open", "In Review", "Partner Action Needed", "Resolved"];

export default function IssueTriage() {
  const [partners, setPartners] = useState<PartnerSummary[]>([]);
  const [issues, setIssues] = useState<ValidationIssue[]>([]);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const categories = useMemo(() => ["", ...Array.from(new Set(issues.map((issue) => issue.category))).sort()], [issues]);

  async function loadIssues(nextFilters = filters) {
    setLoading(true);
    setError(null);
    try {
      const [partnerRows, issueRows] = await Promise.all([api.partners(), api.triage(nextFilters)]);
      setPartners(partnerRows);
      setIssues(issueRows);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load issues");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadIssues({});
  }, []);

  async function updateStatus(issueId: number, status: string) {
    const updated = await api.updateIssue(issueId, { status });
    setIssues((rows) => rows.map((issue) => (issue.error_id === issueId ? updated : issue)));
  }

  function setFilter(key: string, value: string) {
    const next = { ...filters, [key]: value };
    Object.keys(next).forEach((name) => {
      if (!next[name]) delete next[name];
    });
    setFilters(next);
    loadIssues(next);
  }

  if (error) return <ErrorState message={error} />;

  return (
    <>
      <PageHeader title="Issue Triage" eyebrow="Blocker Queue">
        <button className="inline-flex h-10 items-center gap-2 rounded-lg border border-line bg-panel px-3 text-sm font-semibold text-slate-200 hover:text-cyan-100" onClick={() => loadIssues()}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </PageHeader>

      <Panel title="Filters" className="mb-5">
        <div className="grid gap-3 md:grid-cols-4">
          <select className="h-10 rounded-lg border border-line bg-slate-950/50 px-3 text-sm text-slate-100" value={filters.severity ?? ""} onChange={(event) => setFilter("severity", event.target.value)}>
            {severities.map((item) => <option key={item || "All"} value={item} className="bg-panel">{item || "All severities"}</option>)}
          </select>
          <select className="h-10 rounded-lg border border-line bg-slate-950/50 px-3 text-sm text-slate-100" value={filters.category ?? ""} onChange={(event) => setFilter("category", event.target.value)}>
            {categories.map((item) => <option key={item || "All"} value={item} className="bg-panel">{item || "All categories"}</option>)}
          </select>
          <select className="h-10 rounded-lg border border-line bg-slate-950/50 px-3 text-sm text-slate-100" value={filters.partner_id ?? ""} onChange={(event) => setFilter("partner_id", event.target.value)}>
            <option value="" className="bg-panel">All partners</option>
            {partners.map((partner) => <option key={partner.partner_id} value={partner.partner_id} className="bg-panel">{partner.partner_name}</option>)}
          </select>
          <select className="h-10 rounded-lg border border-line bg-slate-950/50 px-3 text-sm text-slate-100" value={filters.status ?? ""} onChange={(event) => setFilter("status", event.target.value)}>
            {statuses.map((item) => <option key={item || "All"} value={item} className="bg-panel">{item || "All statuses"}</option>)}
          </select>
        </div>
      </Panel>

      {loading ? <LoadingState label="Loading triage" /> : (
        <Panel title="Validation and API Issues">
          <div className="dashboard-scrollbar overflow-x-auto">
            <table className="w-full min-w-[1180px] text-left text-sm">
              <thead className="text-xs uppercase tracking-[0.12em] text-slate-500">
                <tr>
                  <th className="pb-3">Severity</th>
                  <th className="pb-3">Partner</th>
                  <th className="pb-3">Category</th>
                  <th className="pb-3">Rule</th>
                  <th className="pb-3">Owner</th>
                  <th className="pb-3">SLA</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3">Fix</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line/70">
                {issues.map((issue) => (
                  <tr key={issue.error_id} className="text-slate-300 align-top">
                    <td className="py-3"><SeverityBadge severity={issue.severity} /></td>
                    <td className="py-3 font-semibold text-white">{issue.partner_name}</td>
                    <td className="py-3">{issue.category}</td>
                    <td className="py-3">{compactRule(issue.rule_name)}</td>
                    <td className="py-3">{issue.assigned_owner}</td>
                    <td className="py-3">{issue.sla_age_days ?? 0}d</td>
                    <td className="py-3">
                      <select className="h-9 rounded-lg border border-line bg-slate-950/50 px-2 text-sm text-slate-100" value={issue.status} onChange={(event) => updateStatus(issue.error_id, event.target.value)}>
                        {statuses.filter(Boolean).map((item) => <option key={item} value={item} className="bg-panel">{item}</option>)}
                      </select>
                    </td>
                    <td className="py-3 max-w-md">
                      <p>{issue.recommended_fix}</p>
                      <div className="mt-2"><StatusBadge status={issue.status} /></div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      )}
    </>
  );
}

