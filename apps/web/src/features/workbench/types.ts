import type {
  CreateEventPayload,
  EventLineagePayload,
  EventRecordPayload,
  GenericRecord,
  ImportFinahuntEventPayload,
  ImportFinahuntEventResponse,
  InfluenceEdgeRecord,
  ParticipantActionRecord,
  ParticipantListPayload,
  ParticipantRecord,
  ReplayPayload,
  RoundSnapshotRecord,
  SimulationSummaryPayload,
  ValidationPayload,
} from "@/features/event-sandbox/types";

export type {
  CreateEventPayload,
  EventLineagePayload,
  EventRecordPayload,
  GenericRecord,
  ImportFinahuntEventPayload,
  ImportFinahuntEventResponse,
  InfluenceEdgeRecord,
  ParticipantActionRecord,
  ParticipantListPayload,
  ParticipantRecord,
  ReplayPayload,
  RoundSnapshotRecord,
  SimulationSummaryPayload,
  ValidationPayload,
};

export type WorkbenchNode = {
  node_id: string;
  node_type: string;
  label: string;
  group?: string;
  highlighted?: boolean;
  metadata?: GenericRecord;
};

export type WorkbenchEdge = {
  edge_id: string;
  edge_type: string;
  source: string;
  target: string;
  label?: string;
  polarity?: string;
  strength?: number;
  metadata?: GenericRecord;
};

export type GraphStagePayload = {
  event_id: string;
  status: string;
  shell: GenericRecord;
  event_graph: GenericRecord;
  nodes: WorkbenchNode[];
  edges: WorkbenchEdge[];
  current_highlights: GenericRecord;
};

export type TradeCard = {
  card_id: string;
  participant_id: string;
  participant_family: string;
  action_type: string;
  next_state: string;
  polarity: string;
  symbols: string[];
  window: string;
  day_index?: number;
  trade_date?: string;
  expected_impact: string;
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
};

export type TradePulsePayload = {
  event_id: string;
  status: string;
  round_id?: string;
  window?: string;
  day_index?: number;
  trade_date?: string;
  is_incremental_generated?: boolean;
  market_state?: string;
  dominant_scenario?: string;
  actions_count?: number;
  buy_clone_count?: number;
  sell_clone_count?: number;
  new_entry_clone_count?: number;
  exit_clone_count?: number;
  highlighted_clone_ids: string[];
  highlighted_symbols: string[];
  trade_cards: TradeCard[];
  market_pulse_summary?: string;
};

export type DecisionTracePayload = {
  event_id: string;
  status: string;
  clone_id: string;
  round_id?: string;
  day_index?: number;
  trade_date?: string;
  is_incremental_generated?: boolean;
  clone_profile: GenericRecord;
  current_state: GenericRecord;
  seen_signals: string[];
  influenced_by: GenericRecord[];
  influences: GenericRecord[];
  decision_chain: GenericRecord[];
  executed_action: GenericRecord;
  expected_impact?: string;
  threshold_summary?: GenericRecord[];
};

export type MarketStateTransitionPayload = {
  event_id: string;
  status: string;
  transition_id: string;
  from_state?: string;
  to_state?: string;
  previous_round_id?: string;
  current_round_id?: string;
  day_index?: number;
  trade_date?: string;
  triggering_clones: string[];
  triggering_edges: GenericRecord[];
  triggering_signals: string[];
  market_metrics?: GenericRecord;
  summary?: string;
};

export type WorkbenchReportPayload = {
  event_id: string;
  status: string;
  replay_summary: GenericRecord;
  report: GenericRecord;
  validation: ValidationPayload | GenericRecord;
  scoreboards: GenericRecord;
  failure_taxonomy: GenericRecord[];
  provenance: GenericRecord;
};

export type WorkbenchAskPayload = {
  question: string;
  ask_type?: string;
  clone_id?: string;
  round_id?: string;
  transition_id?: string;
};

export type WorkbenchAskResponse = {
  event_id: string;
  status: string;
  ask_type: string;
  answer: string;
  evidence_refs: GenericRecord[];
};
