import { Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ErrorState, LoadingState } from "../components/LoadingState";
import { PageHeader } from "../components/PageHeader";
import { Panel } from "../components/Panel";
import { StatusBadge } from "../components/StatusBadge";
import { api, formatDate } from "../lib/api";
import type { PartnerSummary } from "../types";

export default function Partners() {
  const [partners, setPartners] = useState<PartnerSummary[]>([]);
  const [status, setStatus] = useState("All");
  const [region, setRegion] = useState("All");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .partners()
      .then(setPartners)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const regions = useMemo(
    () => ["All", ...Array.from(new Set(partners.flatMap((partner) => partner.region_coverage))).sort()],
    [partners]
  );
  const statuses = useMemo(() => ["All", ...Array.from(new Set(partners.map((partner) => partner.integration_status))).sort()], [partners]);
  const filtered = partners.filter((partner) => {
    const statusMatch = status === "All" || partner.integration_status === status;
    const regionMatch = region === "All" || partner.region_coverage.includes(region);
    return statusMatch && regionMatch;
  });

  if (error) return <ErrorState message={error} />;
  if (loading) return <LoadingState label="Loading partners" />;

  return (
    <>
      <PageHeader title="Partners" eyebrow="Integration Portfolio">
        <label className="flex items-center gap-2 rounded-lg border border-line bg-panel px-3 py-2 text-sm text-slate-300">
          <Search size={16} className="text-slate-500" />
          <select className="bg-transparent text-slate-100 outline-none" value={status} onChange={(event) => setStatus(event.target.value)}>
            {statuses.map((item) => (
              <option key={item} value={item} className="bg-panel">
                {item}
              </option>
            ))}
          </select>
        </label>
        <select className="rounded-lg border border-line bg-panel px-3 py-2 text-sm text-slate-100 outline-none" value={region} onChange={(event) => setRegion(event.target.value)}>
          {regions.map((item) => (
            <option key={item} value={item} className="bg-panel">
              {item}
            </option>
          ))}
        </select>
      </PageHeader>

      <Panel title="Partner Integrations">
        <div className="dashboard-scrollbar overflow-x-auto">
          <table className="w-full min-w-[980px] text-left text-sm">
            <thead className="text-xs uppercase tracking-[0.12em] text-slate-500">
              <tr>
                <th className="pb-3">Partner</th>
                <th className="pb-3">Status</th>
                <th className="pb-3">Regions</th>
                <th className="pb-3">Readiness</th>
                <th className="pb-3">Open Blockers</th>
                <th className="pb-3">Entitlements</th>
                <th className="pb-3">Launch Target</th>
                <th className="pb-3">Last Feed</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line/70">
              {filtered.map((partner) => (
                <tr key={partner.partner_id} className="text-slate-300">
                  <td className="py-3">
                    <Link className="font-semibold text-white hover:text-cyan-100" to={`/partners/${partner.partner_id}`}>
                      {partner.partner_name}
                    </Link>
                    <p className="text-xs text-slate-500">{partner.contact_email}</p>
                  </td>
                  <td className="py-3">
                    <StatusBadge status={partner.integration_status} />
                  </td>
                  <td className="py-3">{partner.region_coverage.join(", ")}</td>
                  <td className="py-3">{partner.readiness_score}%</td>
                  <td className="py-3">{partner.open_blocker_count}</td>
                  <td className="py-3">{partner.entitlement_package_status}</td>
                  <td className="py-3">{formatDate(partner.launch_target_date)}</td>
                  <td className="py-3">{formatDate(partner.last_feed_upload)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </>
  );
}

