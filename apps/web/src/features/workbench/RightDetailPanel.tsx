"use client";

import React, { useMemo } from "react";

import type {
  DecisionTracePayload,
  GenericRecord,
  GraphStagePayload,
  MarketStateTransitionPayload,
  RoundSnapshotRecord,
  TradePulsePayload,
  ValidationPayload,
  WorkbenchEdge,
  WorkbenchNode,
  WorkbenchReportPayload,
} from "./types";
import {
  actionLabel,
  asArray,
  asRecord,
  cardStyle,
  cloneAlias,
  dayLabel,
  familyLabel,
  formatCurrency,
  formatList,
  formatPercent,
  formatPositionBook,
  formatShares,
  mutedStyle,
  orderSideLabel,
  polarityColor,
  stringValue,
  subtleCardStyle,
} from "./workbenchShared";

export function RightDetailPanel({
  graphStage,
  tradePulse,
  decisionTrace,
  transition,
  selectedNode,
  selectedEdge,
  report,
  validation,
  activeRound,
}: {
  graphStage: GraphStagePayload;
  tradePulse: TradePulsePayload | null;
  decisionTrace: DecisionTracePayload | null;
  transition: MarketStateTransitionPayload | null;
  selectedNode: WorkbenchNode | null;
  selectedEdge: WorkbenchEdge | null;
  report: WorkbenchReportPayload | null;
  validation: ValidationPayload | null;
  activeRound: RoundSnapshotRecord | null;
}) {
  const cloneProfile = asRecord(decisionTrace?.clone_profile);
  const currentState = asRecord(decisionTrace?.current_state);
  const executedAction = useMemo(() => resolveExecutedAction(selectedEdge, decisionTrace?.executed_action), [decisionTrace?.executed_action, selectedEdge]);
  const incomingInfluence = asArray<GenericRecord>(decisionTrace?.influenced_by);
  const outgoingInfluence = asArray<GenericRecord>(decisionTrace?.influences);
  const thresholdSummary = asArray<GenericRecord>(decisionTrace?.threshold_summary);
  const whyReport = asRecord(validation?.why);
  const reviewReport = asRecord(asRecord(report?.report).review_report);
  const selectionLabel = selectedEdge
    ? `${selectedEdge.edge_type} / ${stringValue(selectedEdge.label, selectedEdge.edge_type)}`
    : selectedNode
      ? `${selectedNode.node_type} / ${selectedNode.label}`
      : "事件焦点";

  return (
    <aside style={{ ...cardStyle, padding: 18, display: "grid", gap: 16, alignSelf: "start" }}>
      <Panel title="当天上下文">
        <DetailRow label="当前交易日" value={`${dayLabel(activeRound?.day_index)} / ${stringValue(activeRound?.trade_date)}`} />
        <DetailRow label="当前选中" value={selectionLabel} />
        <DetailRow label="市场状态" value={stringValue(activeRound?.market_state?.state ?? graphStage.shell.market_state)} />
        <DetailRow label="主导情景" value={stringValue(activeRound?.scenario_snapshot?.dominant_scenario ?? graphStage.shell.dominant_scenario)} />
        <DetailRow label="增量推演" value={activeRound?.is_incremental_generated ? "是" : "否"} />
      </Panel>

      {selectedNode?.node_type === "event" ? <EventSeedPanel eventGraph={graphStage.event_graph} /> : null}
      {selectedEdge?.edge_type === "trade" ? <TradeEdgePanel edge={selectedEdge} /> : null}
      {selectedEdge?.edge_type === "influence" ? <InfluenceEdgePanel edge={selectedEdge} /> : null}

      {selectedNode?.node_type === "clone" || decisionTrace ? (
        <>
          <CloneDailyStoryPanel cloneProfile={cloneProfile} currentState={currentState} executedAction={executedAction} />
          <InfluenceFlowPanel title="它受谁影响" items={incomingInfluence} emptyText="当天没有抓到指向它的影响链。" />
          <InfluenceFlowPanel title="它又影响了谁" items={outgoingInfluence} emptyText="当天没有抓到它向外扩散的影响链。" />
          <ThresholdPanel thresholdSummary={thresholdSummary} seenSignals={decisionTrace?.seen_signals ?? []} />
        </>
      ) : selectedNode ? (
        <NodeMetadataPanel node={selectedNode} />
      ) : null}

      <MarketStoryPanel activeRound={activeRound} transition={transition} />
      <SecondaryNarrativePanel whyReport={whyReport} reviewReport={reviewReport} validation={validation} />
    </aside>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section style={{ ...subtleCardStyle, padding: 16, display: "grid", gap: 12 }}>
      <div style={{ fontSize: 16, fontWeight: 800, color: "#0f172a" }}>{title}</div>
      {children}
    </section>
  );
}

function DetailRow({ label, value, compact = false }: { label: string; value: string; compact?: boolean }) {
  return (
    <div style={{ display: "grid", gap: compact ? 4 : 6 }}>
      <div style={{ fontSize: 11, letterSpacing: "0.08em", textTransform: "uppercase", color: "#64748b", fontWeight: 700 }}>{label}</div>
      <div style={{ color: "#0f172a", fontWeight: 700, lineHeight: 1.5 }}>{value}</div>
    </div>
  );
}

function EventSeedPanel({ eventGraph }: { eventGraph: GenericRecord }) {
  const record = asRecord(eventGraph.record);
  const structure = asRecord(eventGraph.structure);
  const mapping = asRecord(eventGraph.mapping);
  return (
    <Panel title="事件种子">
      <div style={{ fontSize: 20, fontWeight: 800, color: "#0f172a" }}>{stringValue(record.title)}</div>
      <div style={mutedStyle}>{stringValue(record.body)}</div>
      <DetailRow label="来源" value={stringValue(record.source)} />
      <DetailRow label="事件类型" value={stringValue(structure.event_type)} />
      <DetailRow label="目标标的" value={formatList(mapping.symbols)} />
      <DetailRow label="确认信号" value={formatList(structure.confirmation_signals)} />
      <DetailRow label="失效条件" value={formatList(structure.invalidation_conditions)} />
    </Panel>
  );
}

function NodeMetadataPanel({ node }: { node: WorkbenchNode }) {
  return (
    <Panel title="节点信息">
      {Object.entries(asRecord(node.metadata)).length === 0 ? (
        <div style={mutedStyle}>这个节点没有额外元数据。</div>
      ) : (
        Object.entries(asRecord(node.metadata)).map(([key, value]) => (
          <DetailRow key={key} label={key} value={Array.isArray(value) ? formatList(value) : stringValue(value)} compact />
        ))
      )}
    </Panel>
  );
}

function CloneDailyStoryPanel({
  cloneProfile,
  currentState,
  executedAction,
}: {
  cloneProfile: GenericRecord;
  currentState: GenericRecord;
  executedAction: GenericRecord;
}) {
  const participantId = stringValue(cloneProfile.clone_id ?? cloneProfile.participant_id, stringValue(executedAction.participant_id));
  const family = familyLabel(cloneProfile.participant_family ?? currentState.participant_family);
  const alias = cloneAlias(participantId);
  return (
    <Panel title="当天 Agent 视角">
      <div style={{ fontSize: 22, fontWeight: 800, color: "#0f172a" }}>
        {alias}（{family}）
      </div>
      <div style={mutedStyle}>
        当天动作 {actionLabel(executedAction.action_name ?? executedAction.action_type)}，方向 {orderSideLabel(executedAction.order_side)}。
      </div>
      <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))" }}>
        <DetailRow label="股数 / 金额" value={`${formatShares(executedAction.trade_quantity)} / ${formatCurrency(executedAction.order_value)}`} compact />
        <DetailRow label="现金前后" value={`${formatCurrency(executedAction.cash_before)} -> ${formatCurrency(executedAction.cash_after)}`} compact />
        <DetailRow label="仓位前后" value={`${formatCurrency(executedAction.position_before)} -> ${formatCurrency(executedAction.position_after)}`} compact />
        <DetailRow label="持仓股数前后" value={`${formatShares(executedAction.position_qty_before)} -> ${formatShares(executedAction.position_qty_after)}`} compact />
        <DetailRow label="当前现金" value={formatCurrency(currentState.cash_available ?? cloneProfile.cash_available)} compact />
        <DetailRow label="当前仓位" value={formatPositionBook(currentState.current_positions ?? cloneProfile.current_positions)} compact />
      </div>
      <div style={{ ...mutedStyle, marginTop: 4 }}>{stringValue(executedAction.effect_summary, "当天还没有返回额外动作解释。")}</div>
    </Panel>
  );
}

function InfluenceFlowPanel({
  title,
  items,
  emptyText,
}: {
  title: string;
  items: GenericRecord[];
  emptyText: string;
}) {
  return (
    <Panel title={title}>
      {items.length === 0 ? (
        <div style={mutedStyle}>{emptyText}</div>
      ) : (
        <div style={{ display: "grid", gap: 10 }}>
          {items.slice(0, 4).map((item, index) => {
            const polarity = stringValue(item.polarity, "neutral");
            return (
              <div
                key={`${item.source_participant_id ?? item.target_participant_id ?? "edge"}-${index}`}
                style={{
                  borderRadius: 16,
                  padding: "12px 12px 10px",
                  border: `1px solid ${polarityColor(polarity)}`,
                  background: "rgba(255,255,255,0.96)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                  <div style={{ fontWeight: 800, color: "#0f172a" }}>
                    {cloneAlias(item.source_participant_id)} {"->"} {cloneAlias(item.target_participant_id)} / {polarity}
                  </div>
                  <div style={{ color: polarityColor(polarity), fontWeight: 800, fontSize: 12, textTransform: "uppercase" }}>
                    {formatPercent(item.strength, 0)}
                  </div>
                </div>
                <div style={{ ...mutedStyle, marginTop: 8 }}>{stringValue(item.reason, "未返回影响原因。")}</div>
                <div style={{ display: "grid", gap: 6, marginTop: 10 }}>
                  <DetailRow label="作用阈值" value={stringValue(item.effect_on, "未标注")} compact />
                  <DetailRow label="结果判断" value={inferInfluenceOutcome(item)} compact />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Panel>
  );
}

function ThresholdPanel({ thresholdSummary, seenSignals }: { thresholdSummary: GenericRecord[]; seenSignals: string[] }) {
  return (
    <Panel title="当天决策证据">
      {thresholdSummary.length === 0 ? (
        <div style={mutedStyle}>当天没有返回额外阈值证据。</div>
      ) : (
        thresholdSummary.slice(0, 6).map((item, index) => (
          <div key={`${item.metric ?? "metric"}-${index}`} style={{ ...subtleCardStyle, padding: 12, display: "grid", gap: 6 }}>
            <DetailRow label="指标" value={stringValue(item.metric)} compact />
            <DetailRow label="值" value={Array.isArray(item.value) ? formatList(item.value) : stringValue(item.value)} compact />
            <DetailRow label="阈值" value={stringValue(item.threshold, "未标注")} compact />
          </div>
        ))
      )}
      <div style={mutedStyle}>当天观察到的信号：{seenSignals.length ? seenSignals.join("，") : "暂无"}。</div>
    </Panel>
  );
}

function InfluenceEdgePanel({ edge }: { edge: WorkbenchEdge }) {
  const metadata = asRecord(edge.metadata);
  return (
    <Panel title="影响边详情">
      <DetailRow label="影响链" value={`${cloneAlias(metadata.source_participant_id, 1)} -> ${cloneAlias(metadata.target_participant_id, 2)}`} />
      <DetailRow label="原因" value={stringValue(metadata.reason, edge.label)} />
      <DetailRow label="强度" value={formatPercent(metadata.strength ?? edge.strength, 0)} />
      <DetailRow label="作用阈值" value={stringValue(metadata.effect_on, "未标注")} />
      <DetailRow label="结果判断" value={inferInfluenceOutcome(metadata)} />
      <DetailRow label="触发条件" value={stringValue(metadata.activation_condition, "未标注")} />
    </Panel>
  );
}

function TradeEdgePanel({ edge }: { edge: WorkbenchEdge }) {
  const metadata = asRecord(edge.metadata);
  return (
    <Panel title="交易边详情">
      <DetailRow label="方向" value={orderSideLabel(metadata.order_side)} />
      <DetailRow label="股数 / 金额" value={`${formatShares(metadata.trade_quantity)} / ${formatCurrency(metadata.order_value)}`} />
      <DetailRow label="交易前后仓位" value={`${formatCurrency(metadata.position_before)} -> ${formatCurrency(metadata.position_after)}`} />
      <DetailRow label="交易前后现金" value={`${formatCurrency(metadata.cash_before)} -> ${formatCurrency(metadata.cash_after)}`} />
      <DetailRow label="触发原因" value={stringValue(metadata.effect_summary, edge.label)} />
      <DetailRow label="参考价 / 手数" value={`${formatCurrency(metadata.reference_price)} / ${stringValue(metadata.lot_size, "--")}`} />
    </Panel>
  );
}

function MarketStoryPanel({
  activeRound,
  transition,
}: {
  activeRound: RoundSnapshotRecord | null;
  transition: MarketStateTransitionPayload | null;
}) {
  const marketState = asRecord(activeRound?.market_state);
  const metrics = asRecord(transition?.market_metrics ?? marketState);
  return (
    <Panel title="当天市场故事">
      <DetailRow
        label="状态变化"
        value={
          transition
            ? `${stringValue(transition.from_state, "未知")} -> ${stringValue(transition.to_state, "未知")}`
            : stringValue(marketState.state)
        }
      />
      <DetailRow label="净流量" value={formatCurrency(metrics.net_flow)} />
      <DetailRow label="拥挤度 / 脆弱度" value={`${formatPercent(metrics.crowding_score, 0)} / ${formatPercent(metrics.fragility_score, 0)}`} />
      <DetailRow label="触发 Agent" value={formatList(transition?.triggering_clones)} />
      <div style={mutedStyle}>{stringValue(transition?.summary ?? metrics.summary, "当天还没有补充市场转折解释。")}</div>
    </Panel>
  );
}

function SecondaryNarrativePanel({
  whyReport,
  reviewReport,
  validation,
}: {
  whyReport: GenericRecord;
  reviewReport: GenericRecord;
  validation: ValidationPayload | null;
}) {
  const reliability = asRecord(validation?.reliability);
  return (
    <Panel title="补充解释">
      <div style={mutedStyle}>{stringValue(whyReport.summary ?? reviewReport.summary, "当前还没有额外复盘摘要。")}</div>
      <DetailRow label="支撑链" value={formatList(reviewReport.support_chain ?? reviewReport.key_support_chain)} compact />
      <DetailRow label="对立链" value={formatList(reviewReport.opposition_chain ?? reviewReport.key_opposition_chain)} compact />
      <DetailRow label="关键转折" value={formatList(whyReport.turning_points)} compact />
      <DetailRow label="可靠性条目" value={String(asArray(reliability.participants).length)} compact />
    </Panel>
  );
}

function resolveExecutedAction(selectedEdge: WorkbenchEdge | null, fallback: unknown) {
  if (selectedEdge?.edge_type === "trade") {
    return asRecord(selectedEdge.metadata);
  }
  return asRecord(fallback);
}

function inferInfluenceOutcome(item: GenericRecord) {
  const polarity = stringValue(item.polarity).toLowerCase();
  const effectOn = stringValue(item.effect_on).toLowerCase();
  if (polarity.includes("bear") || effectOn.includes("risk")) {
    return "更可能导致当天卖出或继续观望";
  }
  if (polarity.includes("bull") || effectOn.includes("entry") || effectOn.includes("add")) {
    return "更可能导致当天买入或继续加仓";
  }
  return "更可能导致当天继续观望";
}
