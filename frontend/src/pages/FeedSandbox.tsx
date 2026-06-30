import { FileDown, Play, ShieldCheck, Upload } from "lucide-react";
import { useEffect, useState } from "react";
import { ErrorState } from "../components/LoadingState";
import { PageHeader } from "../components/PageHeader";
import { Panel } from "../components/Panel";
import { SeverityBadge } from "../components/StatusBadge";
import { api, compactRule } from "../lib/api";
import type { PartnerSummary, ValidationIssue } from "../types";

export default function FeedSandbox() {
  const [partners, setPartners] = useState<PartnerSummary[]>([]);
  const [partnerId, setPartnerId] = useState<number | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [feedId, setFeedId] = useState<number | null>(null);
  const [parseResult, setParseResult] = useState<string | null>(null);
  const [validation, setValidation] = useState<Record<string, number> | null>(null);
  const [errors, setErrors] = useState<ValidationIssue[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.partners().then((rows) => {
      setPartners(rows);
      setPartnerId(rows[0]?.partner_id ?? null);
    }).catch((err) => setError(err.message));
  }, []);

  async function uploadFeed() {
    if (!partnerId || !file) return;
    setBusy(true);
    setError(null);
    const formData = new FormData();
    formData.append("partner_id", String(partnerId));
    formData.append("file", file);
    try {
      const uploaded = await api.uploadFeed(formData);
      setFeedId(uploaded.feed_id);
      setParseResult(null);
      setValidation(null);
      setErrors([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  async function parseFeed() {
    if (!feedId) return;
    setBusy(true);
    setError(null);
    try {
      const parsed = await api.parseFeed(feedId);
      setParseResult(`${parsed.parse_status}: ${parsed.content_records} records`);
      if (parsed.parser_error) setError(parsed.parser_error);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Parse failed");
    } finally {
      setBusy(false);
    }
  }

  async function validateFeed() {
    if (!feedId) return;
    setBusy(true);
    setError(null);
    try {
      const result = await api.validateFeed(feedId);
      setValidation({ ...result.severity_counts, readiness_score: result.readiness.readiness_score });
      setErrors(await api.feedErrors(feedId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Validation failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <PageHeader title="Feed Upload Sandbox" eyebrow="Partner Self-Service">
        <button
          className="inline-flex h-10 items-center gap-2 rounded-lg border border-line bg-panel px-3 text-sm font-semibold text-slate-200 hover:text-cyan-100"
          onClick={() => partnerId && window.open(`http://127.0.0.1:8000/api/partners/${partnerId}/integration-checklist`, "_blank")}
        >
          <FileDown size={16} />
          Checklist
        </button>
      </PageHeader>

      {error ? <div className="mb-5"><ErrorState message={error} /></div> : null}

      <div className="grid gap-5 xl:grid-cols-[0.75fr_1.25fr]">
        <Panel title="Upload Feed">
          <div className="grid gap-4">
            <label className="grid gap-2 text-sm font-semibold text-slate-300">
              Partner
              <select className="h-11 rounded-lg border border-line bg-slate-950/50 px-3 text-slate-100 outline-none" value={partnerId ?? ""} onChange={(event) => setPartnerId(Number(event.target.value))}>
                {partners.map((partner) => (
                  <option key={partner.partner_id} value={partner.partner_id} className="bg-panel">
                    {partner.partner_name}
                  </option>
                ))}
              </select>
            </label>
            <label className="grid gap-2 text-sm font-semibold text-slate-300">
              Feed File
              <input
                className="rounded-lg border border-line bg-slate-950/50 px-3 py-2 text-sm text-slate-200 file:mr-4 file:rounded-md file:border-0 file:bg-cyan-400/15 file:px-3 file:py-2 file:text-cyan-50"
                type="file"
                accept=".json,.xml,.csv"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              />
            </label>
            <div className="grid gap-2 sm:grid-cols-3">
              <button className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-cyan px-3 text-sm font-semibold text-slate-950 disabled:opacity-40" disabled={!file || !partnerId || busy} onClick={uploadFeed}>
                <Upload size={16} />
                Upload
              </button>
              <button className="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-line bg-slate-950/40 px-3 text-sm font-semibold text-slate-200 disabled:opacity-40" disabled={!feedId || busy} onClick={parseFeed}>
                <Play size={16} />
                Parse
              </button>
              <button className="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-emerald-300/30 bg-emerald-500/10 px-3 text-sm font-semibold text-emerald-100 disabled:opacity-40" disabled={!feedId || busy} onClick={validateFeed}>
                <ShieldCheck size={16} />
                Validate
              </button>
            </div>
            <div className="rounded-lg border border-line bg-slate-950/35 p-3 text-sm text-slate-300">
              <p>Feed ID: <span className="font-semibold text-white">{feedId ?? "Not uploaded"}</span></p>
              <p>Parse: <span className="font-semibold text-white">{parseResult ?? "Pending"}</span></p>
            </div>
          </div>
        </Panel>

        <Panel title="Validation Summary">
          {validation ? (
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
              {Object.entries(validation).map(([name, value]) => (
                <div key={name} className="rounded-lg border border-line bg-slate-950/35 p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">{compactRule(name)}</p>
                  <p className="mt-2 text-3xl font-semibold text-white">{value}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-400">No validation run selected.</p>
          )}
        </Panel>
      </div>

      <Panel title="Validation Errors" className="mt-5">
        <div className="dashboard-scrollbar overflow-x-auto">
          <table className="w-full min-w-[960px] text-left text-sm">
            <thead className="text-xs uppercase tracking-[0.12em] text-slate-500">
              <tr>
                <th className="pb-3">Severity</th>
                <th className="pb-3">Category</th>
                <th className="pb-3">Rule</th>
                <th className="pb-3">Message</th>
                <th className="pb-3">Recommended Fix</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line/70">
              {errors.map((issue) => (
                <tr key={issue.error_id} className="text-slate-300">
                  <td className="py-3"><SeverityBadge severity={issue.severity} /></td>
                  <td className="py-3">{issue.category}</td>
                  <td className="py-3">{compactRule(issue.rule_name)}</td>
                  <td className="py-3">{issue.error_message}</td>
                  <td className="py-3">{issue.recommended_fix}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {errors.length === 0 ? <p className="py-5 text-sm text-slate-400">No errors to display.</p> : null}
        </div>
      </Panel>
    </>
  );
}
