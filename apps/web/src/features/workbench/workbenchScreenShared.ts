"use client";

import {
  getEvent,
  getGraphStage,
  getLineage,
  getParticipants,
  getReplay,
  getSimulation,
  getValidation,
} from "./api";
import type {
  GenericRecord,
  GraphStagePayload,
  ParticipantActionRecord,
  ParticipantListPayload,
  ReplayPayload,
  RoundSnapshotRecord,
  SimulationSummaryPayload,
  TradeCard,
  ValidationPayload,
  WorkbenchNode,
} from "./types";
import {
  actionLabel,
  cloneAlias,
  familyLabel,
  formatCurrency,
  formatShares,
  orderSideLabel,
  stringValue,
  useAsyncPayload,
} from "./workbenchShared";

export type WorkbenchPayload = {
  event: Record<string, unknown>;
  lineage: Record<string, unknown>;
  participants: ParticipantListPayload;
  simulation: SimulationSummaryPayload;
  replay: ReplayPayload;
  validation: ValidationPayload;
  graphStage: GraphStagePayload;
};

export function useWorkbenchPayload(eventId: string, refreshNonce: number) {
  return useAsyncPayload<WorkbenchPayload>(
    async () => {
      const [event, lineage, participants, simulation, replay, validation, graphStage] = await Promise.all([
        getEvent(eventId),
        getLineage(eventId),
        getParticipants(eventId),
        getSimulation(eventId),
        getReplay(eventId),
        getValidation(eventId),
        getGraphStage(eventId),
      ]);
      return { event, lineage, participants, simulation, replay, validation, graphStage };
    },
    [eventId, refreshNonce],
  );
}

export function buildRoundGraphStage(baseGraphStage: GraphStagePayload, activeRound: RoundSnapshotRecord | null): GraphStagePayload {
  const staticEdges = baseGraphStage.edges.filter((edge) => edge.edge_type !== "influence" && edge.edge_type !== "trade");
  if (!activeRound) {
    return {
      ...baseGraphStage,
      edges: staticEdges,
    };
  }

  const activeCloneIds = new Set(
    [
      ...activeRound.participant_actions.map((action) => String(action.participant_id ?? "")),
      ...activeRound.influence_edges.flatMap((edge) => [
        String(edge.source_participant_id ?? ""),
        String(edge.target_participant_id ?? ""),
      ]),
    ].filter((item) => item.trim().length > 0),
  );
  const activeSymbols = new Set(
    activeRound.participant_actions.map((action) => String(action.target_symbol ?? "")).filter((item) => item.trim().length > 0),
  );
  const familyCounts = new Map<string, number>();
  activeRound.participant_actions.forEach((action) => {
    const family = String(action.participant_family ?? "unknown");
    familyCounts.set(family, (familyCounts.get(family) ?? 0) + 1);
  });

  const nodes = [...baseGraphStage.nodes];
  for (const symbol of activeSymbols) {
    if (!nodes.some((node) => node.node_id === `symbol:${symbol}`)) {
      nodes.push({
        node_id: `symbol:${symbol}`,
        node_type: "symbol",
        label: symbol,
        group: "market_object",
        highlighted: true,
      });
    }
  }

  const nextNodes = nodes.map((node, index) => {
    if (node.node_type === "clone") {
      const cloneId = node.node_id.replace("clone:", "");
      return {
        ...node,
        highlighted: activeCloneIds.has(cloneId),
        metadata: {
          ...node.metadata,
          alias: cloneAlias(cloneId, index + 1),
          family_label: familyLabel(node.metadata?.participant_family ?? node.group),
        },
      };
    }
    if (node.node_type === "symbol") {
      return { ...node, highlighted: activeSymbols.has(node.label) };
    }
    return { ...node, highlighted: node.node_type === "event" ? true : node.highlighted };
  });

  const dynamicInfluenceEdges = activeRound.influence_edges.map((edge, index) => ({
    edge_id: `influence:${activeRound.round_id}:${index}`,
    edge_type: "influence",
    source: `clone:${edge.source_participant_id}`,
    target: `clone:${edge.target_participant_id}`,
    label: summarizeInfluenceLabel(edge),
    polarity: stringValue(edge.polarity, "neutral"),
    strength: toNumberSafe(edge.strength),
    metadata: edge as GenericRecord,
  }));

  const dynamicTradeEdges = activeRound.participant_actions.map((action, index) => {
    const targetNodeId = resolveTradeTargetNodeId(action, nextNodes);
    return {
      edge_id: `trade:${activeRound.round_id}:${action.participant_id}:${index}`,
      edge_type: "trade",
      source: `clone:${action.participant_id}`,
      target: targetNodeId,
      label: summarizeTradeLabel(action),
      polarity: stringValue(action.polarity, "neutral"),
      strength: toNumberSafe((action as GenericRecord).confidence) || 0.55,
      metadata: action as GenericRecord,
    };
  });

  const dominantFamilies = Array.from(familyCounts.entries())
    .sort((left, right) => right[1] - left[1])
    .slice(0, 4)
    .map(([family]) => family);

  return {
    ...baseGraphStage,
    shell: {
      ...baseGraphStage.shell,
      market_state: activeRound.market_state?.state ?? baseGraphStage.shell.market_state,
      round_id: activeRound.round_id,
      day_index: activeRound.day_index ?? baseGraphStage.shell.day_index,
      trade_date: activeRound.trade_date ?? baseGraphStage.shell.trade_date,
      is_incremental_generated: activeRound.is_incremental_generated ?? false,
      dominant_scenario: activeRound.scenario_snapshot?.dominant_scenario ?? baseGraphStage.shell.dominant_scenario,
      actions_count: activeRound.actions_count ?? activeRound.participant_actions.length,
      buy_clone_count: activeRound.buy_clone_count ?? 0,
      sell_clone_count: activeRound.sell_clone_count ?? 0,
      new_entry_clone_count: activeRound.new_entry_clone_count ?? 0,
      exit_clone_count: activeRound.exit_clone_count ?? 0,
    },
    nodes: nextNodes,
    edges: [...staticEdges, ...dynamicInfluenceEdges, ...dynamicTradeEdges],
    current_highlights: {
      ...baseGraphStage.current_highlights,
      active_round_id: activeRound.round_id,
      active_day_index: activeRound.day_index,
      active_trade_date: activeRound.trade_date,
      is_incremental_generated: activeRound.is_incremental_generated ?? false,
      actions_count: activeRound.actions_count ?? activeRound.participant_actions.length,
      buy_clone_count: activeRound.buy_clone_count ?? 0,
      sell_clone_count: activeRound.sell_clone_count ?? 0,
      new_entry_clone_count: activeRound.new_entry_clone_count ?? 0,
      exit_clone_count: activeRound.exit_clone_count ?? 0,
      active_clone_ids: Array.from(activeCloneIds),
      active_symbols: Array.from(activeSymbols),
      dominant_family_ids: dominantFamilies,
      turning_point: Boolean(activeRound.turning_point),
    },
  };
}

function resolveTradeTargetNodeId(action: ParticipantActionRecord, nodes: WorkbenchNode[]) {
  const targetSymbol = String(action.target_symbol ?? "").trim();
  if (targetSymbol && nodes.some((node) => node.node_id === `symbol:${targetSymbol}`)) {
    return `symbol:${targetSymbol}`;
  }
  if (targetSymbol && nodes.some((node) => node.node_id === `commodity:${targetSymbol}`)) {
    return `commodity:${targetSymbol}`;
  }
  return targetSymbol ? `symbol:${targetSymbol}` : "event:market";
}

function summarizeTradeLabel(action: ParticipantActionRecord) {
  const alias = cloneAlias(action.participant_id);
  const family = familyLabel(action.participant_family);
  const direction = orderSideLabel(action.order_side, actionLabel(action.action_name ?? action.action_type));
  const quantity = formatShares(action.trade_quantity);
  const amount = formatCurrency(action.order_value);
  const symbol = stringValue(action.target_symbol, "事件标的");
  return `${alias}（${family}）${direction}${quantity !== "--" ? ` ${quantity}` : ""}${amount !== "--" ? ` / ${amount}` : ""} / ${symbol}`;
}

function summarizeInfluenceLabel(edge: GenericRecord) {
  const source = cloneAlias(edge.source_participant_id);
  const target = cloneAlias(edge.target_participant_id);
  const polarity = String(edge.polarity ?? "").toLowerCase().includes("bear") ? "看空影响" : "看多影响";
  return `${source} -> ${target} ${polarity}`;
}

export function tradeCardToEdgeId(card: TradeCard, graphStage: GraphStagePayload | null) {
  const direct = card.card_id.replace("trade-card:", "trade:");
  if (graphStage?.edges.some((edge) => edge.edge_id === direct)) {
    return direct;
  }
  return (
    graphStage?.edges.find(
      (edge) =>
        edge.edge_type === "trade" &&
        edge.source === `clone:${card.participant_id}` &&
        edge.target.endsWith(String(card.symbols?.[0] ?? "")),
    )?.edge_id ?? null
  );
}

function toNumberSafe(value: unknown) {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string") {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }
  return 0;
}

export function summarizeText(value: unknown, maxLength: number) {
  const resolved = stringValue(value, "");
  if (!resolved) {
    return "暂无事件正文。";
  }
  const compact = resolved.replace(/\s+/g, " ").trim();
  if (compact.length <= maxLength) {
    return compact;
  }
  return `${compact.slice(0, maxLength).trim()}...`;
}
