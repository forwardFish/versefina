export type StatusKind = "ready" | "missing" | "loading" | "error";

export type EventDemo = {
  status: StatusKind | string;
  event_id?: string;
  headline?: string;
  summary?: Record<string, unknown>;
  structure?: Record<string, unknown>;
  mapping?: Record<string, unknown>;
  simulation?: Record<string, unknown>;
  outcome?: Record<string, unknown>;
  why?: Record<string, unknown>;
  source_paths?: Record<string, string>;
};

export type StatementDemo = {
  status: StatusKind | string;
  statement_id?: string;
  headline?: string;
  summary?: Record<string, unknown>;
  parse_report?: Record<string, unknown>;
  trade_sample?: Record<string, unknown>;
  style_features?: Record<string, unknown>;
  mirror_agent?: Record<string, unknown>;
  mirror_validation?: Record<string, unknown>;
  distribution_calibration?: Record<string, unknown>;
  source_paths?: Record<string, string>;
};

export type AcceptanceDemo = {
  status: StatusKind | string;
  roadmap_id?: string;
  headline?: string;
  summary?: Record<string, unknown>;
  p0_boundaries?: Array<Record<string, unknown>>;
  p1_boundaries?: Array<Record<string, unknown>>;
  current_handoff?: Record<string, unknown>;
  delivery_artifacts?: Array<Record<string, unknown>>;
  source_paths?: Record<string, string>;
};

export type RuntimeShowcasePayload = {
  generated_at: string;
  event_demo: EventDemo;
  statement_demo: StatementDemo;
  acceptance_demo: AcceptanceDemo;
  source_paths: Record<string, unknown>;
};
