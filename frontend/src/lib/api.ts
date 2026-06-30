import type {
  ApiCheck,
  Checklist,
  DashboardSummary,
  PartnerDetail,
  PartnerSummary,
  ProductFeedbackReport,
  ReadinessScore,
  TroubleshootingSummary,
  ValidationIssue
} from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? (import.meta.env.DEV ? "http://127.0.0.1:8000" : "");

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  dashboard: () => request<DashboardSummary>("/api/dashboard/summary"),
  partners: () => request<PartnerSummary[]>("/api/partners"),
  partner: (partnerId: number) => request<PartnerDetail>(`/api/partners/${partnerId}`),
  readiness: (partnerId: number) => request<ReadinessScore>(`/api/partners/${partnerId}/readiness`),
  checklist: (partnerId: number) => request<Checklist>(`/api/partners/${partnerId}/integration-checklist`),
  summary: (partnerId: number) =>
    request<TroubleshootingSummary>(`/api/partners/${partnerId}/troubleshooting-summary`),
  triage: (params: Record<string, string>) => {
    const search = new URLSearchParams(params);
    return request<ValidationIssue[]>(`/api/issues/triage?${search.toString()}`);
  },
  updateIssue: (issueId: number, payload: { status?: string; assigned_owner?: string; resolution_notes?: string }) =>
    request<ValidationIssue>(`/api/issues/${issueId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    }),
  uploadFeed: (formData: FormData) =>
    request<{ feed_id: number; file_name: string; file_type: string; parse_status: string }>("/api/feeds/upload", {
      method: "POST",
      body: formData
    }),
  parseFeed: (feedId: number) =>
    request<{ feed_id: number; parse_status: string; content_records: number; parser_error?: string | null }>(
      `/api/feeds/${feedId}/parse`,
      { method: "POST" }
    ),
  validateFeed: (feedId: number) =>
    request<{
      feed_id: number;
      issue_count: number;
      severity_counts: Record<string, number>;
      readiness: Record<string, number>;
    }>(`/api/feeds/${feedId}/validate`, { method: "POST" }),
  feedErrors: (feedId: number) => request<ValidationIssue[]>(`/api/feeds/${feedId}/errors`),
  runApiChecks: (partnerId: number) =>
    request<ApiCheck[]>(`/api/api-checks/run/${partnerId}`, { method: "POST" }),
  apiChecks: (partnerId: number) => request<ApiCheck[]>(`/api/api-checks/${partnerId}`),
  productFeedback: () => request<ProductFeedbackReport>("/api/reports/product-feedback")
};

export function toChartRows(record: Record<string, number> | undefined): Array<{ name: string; value: number }> {
  return Object.entries(record ?? {}).map(([name, value]) => ({ name, value: Number(value) }));
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(
    new Date(value)
  );
}

export function compactRule(rule: string): string {
  return rule.replaceAll("_", " ");
}
