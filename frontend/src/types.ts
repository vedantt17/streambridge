export type StatusName = "Draft" | "Testing" | "Blocked" | "Ready" | "Live" | string;
export type SeverityName = "Critical" | "High" | "Medium" | "Low" | string;

export interface PartnerSummary {
  partner_id: number;
  partner_name: string;
  contact_email: string;
  integration_status: StatusName;
  launch_target_date: string | null;
  region_scope: string;
  readiness_score: number;
  open_blocker_count: number;
  critical_count: number;
  high_count: number;
  sla_age_days: number;
  last_feed_upload: string | null;
  last_feed_status: string;
  region_coverage: string[];
  entitlement_package_status: string;
}

export interface DashboardSummary {
  partner_count: number;
  open_blockers: number;
  average_readiness_score: number;
  api_health_pct: number;
  status_counts: Record<string, number>;
  severity_counts: Record<string, number>;
  category_counts: Record<string, number>;
  issue_trend: Array<{ date: string; issues: number }>;
  top_recurring_failures: Array<[string, number]>;
  partner_cards: PartnerSummary[];
}

export interface FeedUpload {
  feed_id: number;
  file_name: string;
  file_type: string;
  uploaded_at: string;
  parse_status: string;
  parser_error?: string | null;
}

export interface ValidationIssue {
  error_id: number;
  partner_id?: number;
  partner_name?: string;
  feed_id: number | null;
  content_id: number | null;
  content_title?: string | null;
  severity: SeverityName;
  category: string;
  rule_name: string;
  error_message: string;
  recommended_fix: string;
  assigned_owner: string;
  status: string;
  resolution_notes?: string | null;
  sla_age_days?: number;
  created_at: string;
  resolved_at?: string | null;
}

export interface ApiCheck {
  check_id: number;
  partner_id: number;
  endpoint: string;
  http_status: number;
  latency_ms: number;
  check_status: string;
  checked_at: string;
  error_message: string | null;
}

export interface ReadinessScore {
  score_id: number;
  partner_id: number;
  feed_id: number | null;
  readiness_score: number;
  critical_count: number;
  high_count: number;
  valid_content_pct: number;
  artwork_completion_pct: number;
  entitlement_completion_pct: number;
  api_health_score: number;
  generated_at: string;
}

export interface PartnerDetail extends PartnerSummary {
  feeds: FeedUpload[];
  open_issues: ValidationIssue[];
  api_checks: ApiCheck[];
  onboarding_tasks: Array<{
    task_id: number;
    task_name: string;
    owner: string;
    status: string;
    due_date: string | null;
    completed_at: string | null;
  }>;
}

export interface Checklist {
  partner: string;
  launch_status: string;
  readiness_score: number;
  required_before_go_live: string[];
  current_blockers: {
    critical: number;
    high: number;
    top_rules: Array<[string, number]>;
  };
  metrics: Record<string, number>;
}

export interface TroubleshootingSummary {
  partner: string;
  summary: string;
  critical_count: number;
  high_count: number;
  top_categories: Array<[string, number]>;
  next_actions: string[];
}

export interface ProductFeedbackReport {
  top_validation_failures: Array<[string, number]>;
  top_api_failures: Array<[string, number]>;
  partners_with_repeated_blockers: Array<{ partner: string; blockers: number }>;
  suggested_self_service_features: string[];
  recommended_product_improvements: string[];
}

