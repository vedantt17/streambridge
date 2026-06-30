# Data Dictionary

| Table | Purpose | Key Fields |
| --- | --- | --- |
| `partners` | Partner integration account | `partner_id`, `partner_name`, `contact_email`, `integration_status`, `launch_target_date`, `region_scope` |
| `feed_uploads` | Raw partner feed submissions | `feed_id`, `partner_id`, `file_name`, `file_type`, `raw_file_path`, `parse_status`, `parser_error` |
| `content_items` | Normalized title/content records | `content_id`, `partner_content_id`, `title`, `asset_type`, `channel_id`, `language`, `content_rating`, `playback_url`, `drm_required`, `is_premium` |
| `artwork_assets` | Artwork linked to content | `artwork_url`, `width`, `height`, `file_type`, `validation_status` |
| `availability_windows` | Regional launch windows | `region`, `start_date`, `end_date`, `entitlement_package` |
| `captions` | Caption/subtitle assets | `language`, `region`, `caption_url`, `validation_status` |
| `entitlement_rules` | Premium package access rules | `package_id`, `package_name`, `region`, `entitlement_type` |
| `api_checks` | Simulated partner endpoint checks | `endpoint`, `http_status`, `latency_ms`, `check_status`, `error_message` |
| `validation_errors` | Feed and API issue queue | `severity`, `category`, `rule_name`, `error_message`, `recommended_fix`, `status`, `assigned_owner`, `resolution_notes` |
| `readiness_scores` | Launch-readiness snapshots | `readiness_score`, `critical_count`, `high_count`, `valid_content_pct`, `artwork_completion_pct`, `entitlement_completion_pct`, `api_health_score` |
| `onboarding_tasks` | Launch workflow tasks | `task_name`, `owner`, `status`, `due_date`, `completed_at` |

