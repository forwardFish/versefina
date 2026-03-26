import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { DemoShowcaseView } from "./DemoShowcaseView";
import type { RuntimeShowcasePayload } from "./types";

const samplePayload: RuntimeShowcasePayload = {
  generated_at: "2026-03-25T10:00:00+00:00",
  event_demo: {
    status: "ready",
    event_id: "evt-demo-001",
    headline: "Copper squeeze",
    summary: {
      title: "Copper squeeze",
      dominant_scenario: "base",
      actual_outcome: "bull",
      score_label: "partial_hit",
      event_type: "supply_chain_price_shock",
    },
    mapping: { target_symbols: ["000001.SZ"] },
    simulation: {
      top_participants: [{ participant_id: "institution_confirmation:trend_confirmation" }],
      timeline: { turning_points: ["round-3"], first_move: [{ participant_id: "institution_confirmation:trend_confirmation" }] },
    },
    why: { answer: "系统判断为 base，最终 bull。" },
    source_paths: {},
  },
  statement_demo: {
    status: "ready",
    statement_id: "stmt-001",
    summary: { file_name: "demo.xls", market: "CN_A", upload_status: "parsed" },
    parse_report: { parser_key: "statement_excel_parser", trade_count: 60 },
    style_features: { feature_vector: { avg_holding_days: 2.42 } },
    mirror_agent: { archetype_name: "generic_balanced", participant_family: "quant_risk_budget" },
    mirror_validation: { grading: "B", risk_posture: "guarded" },
    distribution_calibration: { segments: [{ label: "swing" }] },
    source_paths: {},
  },
  acceptance_demo: {
    status: "ready",
    roadmap_id: "roadmap_1_6",
    headline: "Acceptance pack ready",
    summary: { status: "ready", p0_count: 1, p1_count: 1, delivery_artifact_count: 1 },
    p0_boundaries: [{ priority: "P0", label: "Main lane" }],
    p1_boundaries: [{ priority: "P1", label: "Extension lane" }],
    current_handoff: { status: "completed", story: "none" },
    delivery_artifacts: [{ sprint: "Sprint 1", story_id: "E1-003", summary: "event ingestion" }],
    source_paths: {},
  },
  source_paths: {},
};

describe("DemoShowcaseView", () => {
  it("renders real business sections instead of only stats", () => {
    const markup = renderToStaticMarkup(
      <DemoShowcaseView
        apiBaseUrl="http://127.0.0.1:8001"
        dashboardBaseUrl="http://127.0.0.1:8010"
        payload={samplePayload}
        status="ready"
      />,
    );

    expect(markup).toContain("事件推演链");
    expect(markup).toContain("Copper squeeze");
    expect(markup).toContain("Statement -&gt; Style -&gt; Mirror");
    expect(markup).toContain("Acceptance pack ready");
    expect(markup).toContain("查看原始 payload");
  });
});
