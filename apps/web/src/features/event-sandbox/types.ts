export type GenericRecord = Record<string, unknown>;

export type ParticipantRecord = {
  participant_id: string;
  participant_family: string;
  style_variant?: string;
  stance?: string;
  confidence?: number;
  authority_weight?: number;
  time_horizon?: string;
  expected_impact?: string;
  first_movers?: string[];
  secondary_movers?: string[];
  trigger_conditions?: string[];
  invalidation_conditions?: string[];
  evidence?: string[];
  risk_budget_profile?: string;
};

export type ParticipantActionRecord = {
  participant_id: string;
  participant_family: string;
  action_type: string;
  previous_state: string;
  next_state: string;
  polarity: string;
  reason_codes: string[];
};

export type InfluenceEdgeRecord = {
  source_participant_id: string;
  source_participant_family: string;
  target_participant_id: string;
  target_participant_family: string;
  round_id: string;
  order: number;
  influence_type: string;
  polarity: string;
  strength: number;
  reason: string;
};

export type RoundSnapshotRecord = {
  event_id: string;
  run_id: string;
  round_id: string;
  order: number;
  focus: string;
  objective: string;
  participant_actions: ParticipantActionRecord[];
  participant_states: GenericRecord[];
  influence_edges: InfluenceEdgeRecord[];
  belief_snapshot?: GenericRecord;
  market_state?: GenericRecord;
  scenario_snapshot?: GenericRecord;
  turning_point?: boolean;
};

export type EventRecordPayload = {
  event_id: string;
  title?: string;
  body?: string;
  source?: string;
  event_time?: string;
  status?: string;
  record?: GenericRecord;
  structure?: GenericRecord;
  mapping?: GenericRecord;
};

export type ParticipantListPayload = {
  event_id: string;
  status: string;
  participants: ParticipantRecord[];
  blocked_reasons?: string[];
  activation_basis?: string[];
  casebook_status?: string;
};

export type SimulationSummaryPayload = {
  event_id: string;
  status: string;
  run_id?: string;
  dominant_scenario?: string;
  round_count?: number;
  latest_market_state?: string;
  timeline?: GenericRecord;
  top_participants?: GenericRecord[];
  rounds?: GenericRecord[];
};

export type InfluenceGraphPayload = {
  event_id: string;
  status: string;
  latest_round_id?: string;
  rounds: Array<{
    event_id: string;
    round_id: string;
    order: number;
    market_state?: string;
    edges: InfluenceEdgeRecord[];
  }>;
};

export type RoundCollectionPayload = {
  event_id: string;
  status: string;
  run_id?: string;
  rounds: RoundSnapshotRecord[];
};

export type ReplayPayload = {
  event_id: string;
  status: string;
  run_id?: string;
  dominant_scenario?: string;
  timeline?: GenericRecord;
  rounds: RoundSnapshotRecord[];
};

export type ValidationPayload = {
  event_id: string;
  status: string;
  report: GenericRecord;
  why: GenericRecord;
  outcomes: GenericRecord;
  reliability: GenericRecord;
};

export type CreateEventPayload = {
  title: string;
  body: string;
  source: string;
  event_time?: string;
};
