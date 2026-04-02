import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import { EventSandboxOverviewScreen } from "./OverviewScreen";

const overviewPayload = {
  event: {
    record: {
      title: "铜库存挤压事件",
      body: "交易所库存快速下滑，现货升水扩大。",
    },
    structure: {
      event_type: "supply_shock",
      commodities: ["copper"],
      confirmation_signals: ["库存持续下滑", "升水扩大"],
      invalidation_conditions: ["库存快速回补"],
      causal_chain: ["库存紧张", "现货走强", "资金抢先布局"],
    },
    mapping: {
      symbols: ["COPPER", "CU"],
    },
  },
  lineage: {
    status: "ready",
    finahunt_run_id: "run-demo",
    source_event_id: "src-001",
    source_name: "Finahunt",
    primary_theme: "铜供给扰动",
    ranking_context: { rank_position: 1 },
  },
  participants: {
    casebook_status: "ready",
    participants: [
      {
        participant_id: "hot-money-1",
        participant_family: "游资 / 高攻击性主动资金",
        style_variant: "HotMoney_FastBreakout",
        stance: "bull",
        initial_state: "ready",
      },
      {
        participant_id: "institution-1",
        participant_family: "公募 / 机构确认型",
        style_variant: "Institution_SlowConfirmation",
        stance: "bull",
        initial_state: "watch",
      },
    ],
  },
  simulation: {
    dominant_scenario: "bull",
    latest_market_state: "PROPAGATING",
    round_count: 3,
  },
  rounds: {
    rounds: [
      {
        round_id: "round-1",
        order: 1,
        focus: "首发点火",
        objective: "确认 lead clone 是否先动",
        participant_actions: [
          {
            participant_id: "hot-money-1",
            participant_family: "游资 / 高攻击性主动资金",
            action_type: "INIT_BUY",
            previous_state: "ready",
            next_state: "engaged",
            polarity: "bull",
            reason_codes: ["breakout"],
          },
        ],
        participant_states: [
          { participant_id: "hot-money-1", state: "engaged", role: "first_move", capital_range: "300w-1000w" },
          { participant_id: "institution-1", state: "watch", role: "follow_on", capital_range: "3000w-1e" },
        ],
        influence_edges: [],
        belief_snapshot: { consensus_strength: 0.62 },
        market_state: { state: "IGNITION", active_participant_count: 2 },
        scenario_snapshot: { dominant_scenario: "bull", bull_confidence: 0.71, base_confidence: 0.22, bear_confidence: 0.07 },
      },
      {
        round_id: "round-2",
        order: 2,
        focus: "跟随扩散",
        objective: "确认 follow clone 是否跟随",
        participant_actions: [
          {
            participant_id: "institution-1",
            participant_family: "公募 / 机构确认型",
            action_type: "ADD_BUY",
            previous_state: "watch",
            next_state: "confirmed",
            polarity: "bull",
            reason_codes: ["confirmation"],
          },
        ],
        participant_states: [
          { participant_id: "hot-money-1", state: "accelerating", role: "first_move", capital_range: "300w-1000w" },
          { participant_id: "institution-1", state: "confirmed", role: "follow_on", capital_range: "3000w-1e" },
        ],
        influence_edges: [],
        belief_snapshot: { consensus_strength: 0.81 },
        market_state: { state: "PROPAGATING", active_participant_count: 2, follow_on_count: 1, exit_count: 0 },
        scenario_snapshot: { dominant_scenario: "bull", bull_confidence: 0.83, base_confidence: 0.14, bear_confidence: 0.03 },
      },
    ],
    status: "ready",
  },
  influence: {
    event_id: "evt-demo",
    status: "ready",
    latest_round_id: "round-2",
    rounds: [
      {
        event_id: "evt-demo",
        round_id: "round-2",
        order: 2,
        market_state: "PROPAGATING",
        edges: [
          {
            source_participant_id: "hot-money-1",
            source_participant_family: "游资 / 高攻击性主动资金",
            target_participant_id: "institution-1",
            target_participant_family: "公募 / 机构确认型",
            round_id: "round-2",
            order: 1,
            influence_type: "CONFIRMS",
            polarity: "bull",
            strength: 0.76,
            reason: "龙头延续并带来机构确认",
          },
        ],
      },
    ],
  },
  belief: {
    latest: {
      consensus_strength: 0.81,
      divergence_index: 0.22,
    },
  },
  scenarios: {
    latest: {
      dominant_scenario: "bull",
      bull_confidence: 0.83,
      base_confidence: 0.14,
      bear_confidence: 0.03,
      watchpoints: ["库存持续下降"],
      support_chain: ["现货走强", "机构跟进"],
      opposition_chain: ["政策打压"],
    },
  },
  report: {
    report_card: {
      summary: "库存与现货信号共振，形成供给冲击主线。",
    },
    review_report: {
      summary: "游资点火后，机构确认推动市场进入扩散阶段。",
      support_chain: ["游资 lead", "机构确认"],
      opposition_chain: ["政策扰动"],
    },
  },
};

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: React.ReactNode }) => <a href={href}>{children}</a>,
}));

vi.mock("./api", () => ({
  getApiBaseUrl: () => "http://127.0.0.1:8001",
  getBelief: vi.fn(),
  getEvent: vi.fn(),
  getInfluenceGraph: vi.fn(),
  getLineage: vi.fn(),
  getParticipants: vi.fn(),
  getReport: vi.fn(),
  getRounds: vi.fn(),
  getScenarios: vi.fn(),
  getSimulation: vi.fn(),
}));

vi.mock("./shared", async () => {
  const actual = await vi.importActual<typeof import("./shared")>("./shared");
  return {
    ...actual,
    useAsyncPayload: () => ({
      status: "ready",
      data: overviewPayload,
      error: "",
    }),
  };
});

describe("EventSandboxOverviewScreen", () => {
  it("renders the roadmap 1.8 four-zone evolution wall", () => {
    const markup = renderToStaticMarkup(<EventSandboxOverviewScreen eventId="evt-demo" />);

    expect(markup).toContain("事件图谱与来源链");
    expect(markup).toContain("Population / Interaction / Influence");
    expect(markup).toContain("Belief / Scenario / Market State");
    expect(markup).toContain("Replay Timeline + 窗口切换");
    expect(markup).toContain("龙头延续并带来机构确认");
  });
});
