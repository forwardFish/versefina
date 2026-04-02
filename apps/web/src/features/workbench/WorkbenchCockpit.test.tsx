import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { ReplayTimeline } from "./ReplayTimeline";
import { RightDetailPanel } from "./RightDetailPanel";
import { TradePulsePanel } from "./TradePulsePanel";
import { WorkbenchCatalystCard } from "./WorkbenchCatalystCard";
import type {
  DecisionTracePayload,
  GraphStagePayload,
  MarketStateTransitionPayload,
  ReplayPayload,
  TradePulsePayload,
  ValidationPayload,
  WorkbenchReportPayload,
} from "./types";

describe("workbench cockpit components", () => {
  it("renders the catalyst card with a detail link", () => {
    const markup = renderToStaticMarkup(
      <WorkbenchCatalystCard
        title="Lithium price shock"
        summary="锂价上行带动市场关注上游资源链。"
        eventType="supply_chain_price_shock"
        symbols={["002460.SZ"]}
        dayIndex={2}
        tradeDate="2026-04-02"
        detailHref="/workbench/evt-1/detail?round=day-2"
      />,
    );

    expect(markup).toContain("事件催化");
    expect(markup).toContain("查看详细页面");
    expect(markup).toContain("/workbench/evt-1/detail?round=day-2");
    expect(markup).toContain("当前轮次");
  });

  it("renders the daily agent story, influence flow, and threshold evidence", () => {
    const markup = renderToStaticMarkup(
      <RightDetailPanel
        graphStage={buildGraphStage()}
        tradePulse={buildTradePulse()}
        decisionTrace={buildDecisionTrace()}
        transition={buildTransition()}
        selectedNode={{
          node_id: "clone:alpha",
          node_type: "clone",
          label: "alpha",
          group: "institution_confirmation",
        }}
        selectedEdge={{
          edge_id: "trade:day-2:alpha:0",
          edge_type: "trade",
          source: "clone:alpha",
          target: "symbol:000001.SZ",
          label: "A（机构）买入 100000 股 / 12.00M / 000001.SZ",
          polarity: "bullish",
          strength: 0.72,
          metadata: buildDecisionTrace().executed_action,
        }}
        report={buildReport()}
        validation={buildValidation()}
        activeRound={buildReplay().rounds[1]}
      />,
    );

    expect(markup).toContain("当天 Agent 视角");
    expect(markup).toContain("股数 / 金额");
    expect(markup).toContain("它受谁影响");
    expect(markup).toContain("当天决策证据");
    expect(markup).toContain("现金前后");
  });

  it("renders compact sticky day pills and controls", () => {
    const markup = renderToStaticMarkup(
      <ReplayTimeline
        replay={buildReplay()}
        selectedRoundId="day-2"
        onSelectRound={() => {}}
        onContinueDay={() => {}}
        onJumpToFirstDay={() => {}}
        onTogglePlayback={() => {}}
        isPlaying={false}
        isContinuing={false}
        sticky
        variant="compact"
      />,
    );

    expect(markup).toContain("按天切换当前图谱");
    expect(markup).toContain("回到第1天");
    expect(markup).toContain("继续推演下一交易日");
    expect(markup).toContain("第1天");
    expect(markup).toContain("position:sticky");
  });

  it("renders the daily trade stories with quantity, amount, and cash/position changes", () => {
    const markup = renderToStaticMarkup(
      <TradePulsePanel
        tradePulse={buildTradePulse()}
        marketMetrics={{
          net_flow: 18_500_000,
          buy_clone_count: 2,
          sell_clone_count: 1,
          crowding_score: 0.61,
          fragility_score: 0.24,
        }}
        participantsById={{
          alpha: {
            participant_id: "alpha",
            participant_family: "institution_confirmation",
            capital_bucket: "mega_fund",
            capital_base: 120_000_000,
            cash_available: 88_000_000,
            current_positions: { "000001.SZ": 32_000_000 },
          },
        }}
        onSelectTrade={() => {}}
      />,
    );

    expect(markup).toContain("股数 / 金额");
    expect(markup).toContain("现金前后");
    expect(markup).toContain("12.00M");
    expect(markup).toContain("100,000");
  });
});

function buildGraphStage(): GraphStagePayload {
  return {
    event_id: "evt-1",
    status: "ready",
    shell: {
      title: "demo event",
      market_state: "PROPAGATING",
      round_id: "day-2",
      dominant_scenario: "bull",
    },
    event_graph: {
      record: { title: "demo event", body: "A bought, B followed." },
      structure: { event_type: "equity_event", confirmation_signals: ["volume"], invalidation_conditions: ["policy"] },
      mapping: { symbols: ["000001.SZ"] },
    },
    nodes: [
      { node_id: "event:evt-1", node_type: "event", label: "demo event" },
      { node_id: "clone:alpha", node_type: "clone", label: "alpha", metadata: { participant_family: "institution_confirmation" } },
      { node_id: "symbol:000001.SZ", node_type: "symbol", label: "000001.SZ" },
    ],
    edges: [],
    current_highlights: {
      dominant_family_ids: ["institution_confirmation"],
      active_clone_ids: ["alpha"],
    },
  };
}

function buildTradePulse(): TradePulsePayload {
  return {
    event_id: "evt-1",
    status: "ready",
    round_id: "day-2",
    day_index: 2,
    trade_date: "2026-04-02",
    market_state: "PROPAGATING",
    dominant_scenario: "bull",
    buy_clone_count: 2,
    sell_clone_count: 1,
    new_entry_clone_count: 1,
    exit_clone_count: 0,
    highlighted_clone_ids: ["alpha"],
    highlighted_symbols: ["000001.SZ"],
    market_pulse_summary: "alpha 继续买入，beta 首次跟进。",
    trade_cards: [
      {
        card_id: "trade-card:day-2:alpha:0",
        participant_id: "alpha",
        participant_family: "institution_confirmation",
        action_type: "ADD_BUY",
        next_state: "accelerating",
        polarity: "bullish",
        symbols: ["000001.SZ"],
        window: "trading_day",
        day_index: 2,
        trade_date: "2026-04-02",
        expected_impact: "confirmation",
        order_side: "buy",
        order_value: 12_000_000,
        order_value_range_min: 10_000_000,
        order_value_range_max: 14_000_000,
        reference_price: 12,
        reference_price_source: "demo_close",
        lot_size: 100,
        trade_quantity: 100_000,
        position_before: 20_000_000,
        position_after: 32_000_000,
        position_qty_before: 160_000,
        position_qty_after: 260_000,
        holding_qty_after: 260_000,
        cash_before: 100_000_000,
        cash_after: 88_000_000,
      },
    ],
  };
}

function buildDecisionTrace(): DecisionTracePayload {
  return {
    event_id: "evt-1",
    status: "ready",
    clone_id: "alpha",
    round_id: "day-2",
    day_index: 2,
    trade_date: "2026-04-02",
    clone_profile: {
      clone_id: "alpha",
      participant_family: "institution_confirmation",
      stance: "bullish",
      authority_weight: 0.86,
      influence_weight: 0.72,
      capital_bucket: "mega_fund",
      capital_base: 120_000_000,
      cash_available: 88_000_000,
      current_positions: { "000001.SZ": 32_000_000 },
      max_event_exposure: 64_000_000,
    },
    current_state: {
      cash_available: 88_000_000,
      current_positions: { "000001.SZ": 32_000_000 },
      stance: "bullish",
      authority_weight: 0.86,
      influence_weight: 0.72,
    },
    seen_signals: ["volume", "policy"],
    influenced_by: [
      {
        source_participant_id: "beta",
        target_participant_id: "alpha",
        polarity: "bullish",
        strength: 0.63,
        reason: "beta validated the move",
        effect_on: "entry_threshold",
      },
    ],
    influences: [
      {
        source_participant_id: "alpha",
        target_participant_id: "gamma",
        polarity: "bullish",
        strength: 0.55,
        reason: "alpha brought gamma into the move",
        effect_on: "add_bias",
      },
    ],
    decision_chain: [],
    executed_action: {
      action_name: "ADD_BUY",
      execution_window: "trading_day",
      target_symbol: "000001.SZ",
      order_side: "buy",
      order_value: 12_000_000,
      order_value_range_min: 10_000_000,
      order_value_range_max: 14_000_000,
      trade_quantity: 100_000,
      position_before: 20_000_000,
      position_after: 32_000_000,
      position_qty_before: 160_000,
      position_qty_after: 260_000,
      cash_before: 100_000_000,
      cash_after: 88_000_000,
      effect_summary: "alpha sized up after confirmation.",
    },
    expected_impact: "institutional confirmation",
    threshold_summary: [
      { kind: "metric", metric: "validation_score", value: 0.66, threshold: 0.55 },
      { kind: "market", metric: "crowding_score", value: 0.61 },
    ],
  };
}

function buildTransition(): MarketStateTransitionPayload {
  return {
    event_id: "evt-1",
    status: "ready",
    transition_id: "day-2",
    from_state: "IGNITION",
    to_state: "PROPAGATING",
    previous_round_id: "day-1",
    current_round_id: "day-2",
    day_index: 2,
    trade_date: "2026-04-02",
    triggering_clones: ["alpha"],
    triggering_edges: [],
    triggering_signals: ["volume"],
    market_metrics: {
      net_flow: 18_500_000,
      crowding_score: 0.61,
      fragility_score: 0.24,
    },
    summary: "资金继续确认，市场状态进入传播阶段。",
  };
}

function buildReplay(): ReplayPayload {
  return {
    event_id: "evt-1",
    status: "ready",
    run_id: "run-1",
    default_day_count: 5,
    generated_day_count: 5,
    can_continue: true,
    timeline: {},
    rounds: [
      {
        event_id: "evt-1",
        run_id: "run-1",
        round_id: "day-1",
        order: 1,
        day_index: 1,
        trade_date: "2026-04-01",
        focus: "Day 1 Seed Ignition",
        objective: "ignite",
        actions_count: 3,
        buy_clone_count: 1,
        sell_clone_count: 0,
        new_entry_clone_count: 1,
        exit_clone_count: 0,
        participant_actions: [],
        participant_states: [],
        influence_edges: [],
        scenario_snapshot: { dominant_scenario: "bull" },
        market_state: { state: "IGNITION", net_flow: 10_000_000 },
      },
      {
        event_id: "evt-1",
        run_id: "run-1",
        round_id: "day-2",
        order: 2,
        day_index: 2,
        trade_date: "2026-04-02",
        focus: "Day 2 Follow Through",
        objective: "propagate",
        actions_count: 4,
        buy_clone_count: 2,
        sell_clone_count: 1,
        new_entry_clone_count: 1,
        exit_clone_count: 0,
        participant_actions: [],
        participant_states: [],
        influence_edges: [],
        scenario_snapshot: { dominant_scenario: "bull" },
        market_state: { state: "PROPAGATING", net_flow: 18_500_000 },
      },
    ],
  };
}

function buildReport(): WorkbenchReportPayload {
  return {
    event_id: "evt-1",
    status: "ready",
    replay_summary: {},
    report: {
      review_report: {
        summary: "Propagation remains intact.",
        support_chain: ["alpha -> beta"],
        opposition_chain: ["risk desk"],
      },
    },
    validation: buildValidation(),
    scoreboards: {},
    failure_taxonomy: [],
    provenance: {},
  };
}

function buildValidation(): ValidationPayload {
  return {
    event_id: "evt-1",
    status: "ready",
    report: {},
    reliability: {
      participants: [{ participant_id: "alpha" }],
    },
    why: {
      summary: "The day stayed constructive.",
      turning_points: ["beta confirmation"],
    },
    outcomes: {},
  };
}
