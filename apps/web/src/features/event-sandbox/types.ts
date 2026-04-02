export type GenericRecord = Record<string, unknown>;

export type ParticipantRecord = {
  participant_id: string;
  participant_family: string;
  style_variant?: string;
  stance?: string;
  initial_state?: string;
  allowed_actions?: string[];
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
  clone_index?: number;
  influence_weight?: number;
  capital_bucket?: string;
  capital_base?: number;
  cash_available?: number;
  current_positions?: Record<string, number>;
  max_event_exposure?: number;
  reaction_latency?: number;
  entry_threshold?: number;
  add_threshold?: number;
  reduce_threshold?: number;
  exit_threshold?: number;
  preferred_execution_windows?: string[];
  avoid_execution_windows?: string[];
};

export type ParticipantActionRecord = {
  participant_id: string;
  participant_family: string;
  action_type: string;
  action_name?: string;
  previous_state: string;
  next_state: string;
  polarity: string;
  reason_codes: string[];
  execution_window?: string;
  day_index?: number;
  trade_date?: string;
  target_symbol?: string;
  order_side?: string;
  order_value?: number;
  order_value_range_min?: number;
  order_value_range_max?: number;
  reference_price?: number;
  reference_price_source?: string;
  lot_size?: number;
  trade_quantity?: number;
  trade_unit_label?: string;
  position_before?: number;
  position_after?: number;
  position_qty_before?: number;
  position_qty_after?: number;
  holding_qty_after?: number;
  cash_before?: number;
  cash_after?: number;
  influenced_by?: GenericRecord[];
  evidence_trace?: GenericRecord[];
  effect_summary?: string;
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
  lag_windows?: number;
  activation_condition?: string;
  expiration_condition?: string;
  effect_on?: string;
};

export type RoundSnapshotRecord = {
  event_id: string;
  run_id: string;
  round_id: string;
  order: number;
  focus: string;
  objective: string;
  execution_window?: string;
  day_index?: number;
  trade_date?: string;
  is_trading_day?: boolean;
  is_incremental_generated?: boolean;
  actions_count?: number;
  buy_clone_count?: number;
  sell_clone_count?: number;
  new_entry_clone_count?: number;
  exit_clone_count?: number;
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

export type EventLineagePayload = {
  event_id: string;
  status: string;
  finahunt_run_id?: string;
  finahunt_trace_id?: string;
  source_artifact?: string;
  source_event_id?: string;
  source_title?: string;
  source_name?: string;
  source_url?: string;
  source_priority?: string;
  primary_theme?: string;
  ranking_context?: GenericRecord;
  message_snapshot?: GenericRecord;
  imported_at?: string;
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
  default_day_count?: number;
  generated_day_count?: number;
  latest_trade_date?: string;
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
  default_day_count?: number;
  generated_day_count?: number;
  can_continue?: boolean;
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

export type ImportFinahuntEventPayload = {
  run_id?: string;
  rank_position?: number;
  message_id?: string;
  auto_structure_prepare_simulate?: boolean;
};

export type ImportFinahuntEventResponse = {
  event_id: string;
  status: string;
  run_id: string;
  source_event_id: string;
  lineage: EventLineagePayload;
  structure_status: string;
  participant_status: string;
  simulation_status: string;
};
