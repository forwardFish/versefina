"use client";

import React, { useMemo } from "react";

import type {
  DecisionTracePayload,
  GraphStagePayload,
  MarketStateTransitionPayload,
  RoundSnapshotRecord,
  WorkbenchEdge,
  WorkbenchNode,
} from "./types";
import {
  asArray,
  asRecord,
  cardStyle,
  edgeTypeColor,
  formatCurrency,
  formatList,
  mutedStyle,
  polarityColor,
  readStringList,
  stringValue,
  strengthWidth,
  subtleCardStyle,
  toNumber,
  windowLabel,
} from "./workbenchShared";

type InfluenceSidebarProps = {
  graphStage: GraphStagePayload;
  activeRound: RoundSnapshotRecord | null;
  selectedNode: WorkbenchNode | null;
  selectedEdge: WorkbenchEdge | null;
  decisionTrace: DecisionTracePayload | null;
  transition: MarketStateTransitionPayload | null;
  onSelectNode: (nodeId: string) => void;
  onSelectEdge: (edgeId: string) => void;
};

type InfluenceEntry = {
  edgeId: string;
  sourceId: string;
  targetId: string;
  label: string;
  polarity: string;
  strength: number;
  reason: string;
  effectOn: string;
  lagWindows: string;
  activationCondition: string;
  expirationCondition: string;
};

export function InfluenceSidebar({
  graphStage,
  activeRound,
  selectedNode,
  selectedEdge,
  decisionTrace,
  transition,
  onSelectNode,
  onSelectEdge,
}: InfluenceSidebarProps) {
  const nodeLookup = useMemo(
    () => Object.fromEntries(graphStage.nodes.map((node) => [node.node_id, node])),
    [graphStage.nodes],
  );
  const influenceEdges = useMemo(
    () => graphStage.edges.filter((edge) => edge.edge_type === "influence"),
    [graphStage.edges],
  );
  const incomingInfluence = useMemo(
    () =>
      selectedNode?.node_type === "clone"
        ? influenceEdges
            .filter((edge) => edge.target === selectedNode.node_id)
            .sort((left, right) => toNumber(right.strength) - toNumber(left.strength))
        : influenceEdges.slice(0, 6),
    [influenceEdges, selectedNode],
  );
  const outgoingInfluence = useMemo(
    () =>
      selectedNode?.node_type === "clone"
        ? influenceEdges
            .filter((edge) => edge.source === selectedNode.node_id)
            .sort((left, right) => toNumber(right.strength) - toNumber(left.strength))
        : [],
    [influenceEdges, selectedNode],
  );
  const dominantSupportChain = useMemo(
    () =>
      readStringList(
        transition?.market_metrics?.dominant_support_chain ??
          activeRound?.market_state?.dominant_support_chain ??
          graphStage.current_highlights?.dominant_family_ids,
      ),
    [activeRound?.market_state, graphStage.current_highlights, transition?.market_metrics],
  );
  const selectedEdgeDetail = useMemo(() => toInfluenceEntry(selectedEdge), [selectedEdge]);
  const topIncoming = useMemo(() => {
    if (decisionTrace?.influenced_by?.length) {
      return decisionTrace.influenced_by.map((item, index) => toInfluenceEntryFromRecord(item, index));
    }
    return incomingInfluence.map((edge) => toInfluenceEntry(edge)).filter(Boolean) as InfluenceEntry[];
  }, [decisionTrace?.influenced_by, incomingInfluence]);

  return (
    <aside style={{ ...cardStyle, padding: 18, display: "grid", gap: 16, alignSelf: "start" }}>
      <section style={{ ...subtleCardStyle, padding: 16, display: "grid", gap: 12 }}>
        <div style={{ fontSize: 12, letterSpacing: "0.12em", textTransform: "uppercase", color: "#64748b", fontWeight: 700 }}>
          影响链
        </div>
        <div style={{ fontSize: 22, fontWeight: 800, color: "#0f172a" }}>谁影响了谁</div>
        <div style={mutedStyle}>
          第 {stringValue(activeRound?.order)} 轮，{windowLabel(activeRound?.execution_window)}。
          这里会追踪主导支撑链、边级压力，以及当前选中 clone 的扩散影响。
        </div>
      </section>

      <Panel title="主导支撑链">
        {dominantSupportChain.length === 0 ? (
          <div style={mutedStyle}>这一轮还没有浮现出主导链路。</div>
        ) : (
          <div style={{ display: "grid", gap: 10 }}>
            {dominantSupportChain.map((item, index) => (
              <div
                key={`${item}-${index}`}
                style={{
                  borderRadius: 16,
                  padding: "10px 12px",
                  border: "1px solid rgba(22,163,74,0.18)",
                  background: "rgba(240,253,244,0.92)",
                }}
              >
                <div style={{ fontSize: 12, letterSpacing: "0.08em", textTransform: "uppercase", color: "#15803d", fontWeight: 700 }}>
                  链路 {index + 1}
                </div>
                <div style={{ marginTop: 6, fontWeight: 700, color: "#0f172a" }}>{item}</div>
              </div>
            ))}
          </div>
        )}
      </Panel>

      <Panel title={selectedNode?.node_type === "clone" ? `${selectedNode.label} 的流入影响` : "主要流入影响"}>
        {topIncoming.length === 0 ? (
          <div style={mutedStyle}>当前焦点还没有捕获到流入影响。</div>
        ) : (
          <div style={{ display: "grid", gap: 10 }}>
            {topIncoming.slice(0, 4).map((edge) => (
              <InfluenceItem
                key={edge.edgeId}
                edge={edge}
                sourceLabel={nodeLookup[edge.sourceId]?.label ?? stripClonePrefix(edge.sourceId)}
                targetLabel={nodeLookup[edge.targetId]?.label ?? stripClonePrefix(edge.targetId)}
                onSelectNode={onSelectNode}
                onSelectEdge={onSelectEdge}
              />
            ))}
          </div>
        )}
      </Panel>

      <Panel title={selectedNode?.node_type === "clone" ? `${selectedNode.label} 的流出影响` : "当前影响边"}>
        {selectedEdgeDetail ? (
          <div style={{ display: "grid", gap: 10 }}>
            <EdgeHeadline edge={selectedEdgeDetail} />
            <MetaRow label="作用于" value={stringValue(selectedEdgeDetail.effectOn)} />
            <MetaRow label="触发条件" value={stringValue(selectedEdgeDetail.activationCondition)} />
            <MetaRow label="失效条件" value={stringValue(selectedEdgeDetail.expirationCondition)} />
            <MetaRow label="滞后窗口" value={stringValue(selectedEdgeDetail.lagWindows)} />
          </div>
        ) : outgoingInfluence.length ? (
          <div style={{ display: "grid", gap: 10 }}>
            {outgoingInfluence.slice(0, 4).map((edge) => {
              const entry = toInfluenceEntry(edge);
              return entry ? (
                <InfluenceItem
                  key={entry.edgeId}
                  edge={entry}
                  sourceLabel={nodeLookup[entry.sourceId]?.label ?? stripClonePrefix(entry.sourceId)}
                  targetLabel={nodeLookup[entry.targetId]?.label ?? stripClonePrefix(entry.targetId)}
                  onSelectNode={onSelectNode}
                  onSelectEdge={onSelectEdge}
                />
              ) : null;
            })}
          </div>
        ) : (
          <div style={mutedStyle}>请选择一条影响边或一个 clone，查看它的下游影响。</div>
        )}
      </Panel>

      <Panel title="本轮压力">
        <MetaRow label="触发 clone" value={formatList(transition?.triggering_clones)} />
        <MetaRow label="信号" value={formatList(transition?.triggering_signals)} />
        <MetaRow
          label="净流量"
          value={formatCurrency(transition?.market_metrics?.net_flow ?? activeRound?.market_state?.net_flow)}
        />
        <MetaRow label="拥挤度" value={stringValue(transition?.market_metrics?.crowding_score ?? activeRound?.market_state?.crowding_score)} />
        <MetaRow label="脆弱度" value={stringValue(transition?.market_metrics?.fragility_score ?? activeRound?.market_state?.fragility_score)} />
      </Panel>
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

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: "grid", gap: 6 }}>
      <div style={{ fontSize: 11, letterSpacing: "0.08em", textTransform: "uppercase", color: "#64748b", fontWeight: 700 }}>{label}</div>
      <div style={{ color: "#0f172a", fontWeight: 600, lineHeight: 1.5 }}>{value}</div>
    </div>
  );
}

function InfluenceItem({
  edge,
  sourceLabel,
  targetLabel,
  onSelectNode,
  onSelectEdge,
}: {
  edge: InfluenceEntry;
  sourceLabel: string;
  targetLabel: string;
  onSelectNode: (nodeId: string) => void;
  onSelectEdge: (edgeId: string) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onSelectEdge(edge.edgeId)}
      style={{
        textAlign: "left",
        borderRadius: 18,
        border: `1px solid ${edgeTypeColor("influence", edge.polarity)}`,
        background: "rgba(255,255,255,0.96)",
        padding: "12px 12px 13px",
        cursor: "pointer",
      }}
    >
      <EdgeHeadline edge={edge} />
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 10 }}>
        <MiniLink label={sourceLabel} onClick={() => onSelectNode(edge.sourceId)} />
        <MiniLink label={targetLabel} onClick={() => onSelectNode(edge.targetId)} />
      </div>
      <div style={{ ...mutedStyle, marginTop: 10 }}>{edge.reason}</div>
    </button>
  );
}

function MiniLink({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <span
      role="button"
      tabIndex={0}
      onClick={(event) => {
        event.stopPropagation();
        onClick();
      }}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onClick();
        }
      }}
      style={{
        display: "inline-flex",
        alignItems: "center",
        borderRadius: 999,
        padding: "6px 10px",
        border: "1px solid rgba(148,163,184,0.22)",
        background: "rgba(248,250,252,0.96)",
        color: "#0f172a",
        fontWeight: 700,
      }}
    >
      {label}
    </span>
  );
}

function EdgeHeadline({ edge }: { edge: InfluenceEntry }) {
  return (
    <div style={{ display: "grid", gap: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <div style={{ fontWeight: 800, color: "#0f172a" }}>{edge.label}</div>
        <div style={{ color: polarityColor(edge.polarity), fontWeight: 800, textTransform: "uppercase", fontSize: 12 }}>{edge.polarity}</div>
      </div>
      <div style={{ display: "grid", gap: 6 }}>
        <div style={{ height: 8, borderRadius: 999, background: "rgba(226,232,240,0.88)", overflow: "hidden" }}>
          <div
            style={{
              width: `${Math.min(100, Math.max(10, toNumber(edge.strength) * 100))}%`,
              height: "100%",
              borderRadius: 999,
              background: edgeTypeColor("influence", edge.polarity),
            }}
          />
        </div>
        <div style={{ ...mutedStyle, fontSize: 12 }}>
          强度 {edge.strength.toFixed(2)} / 宽度 {strengthWidth(edge.strength).toFixed(1)}
        </div>
      </div>
    </div>
  );
}

function toInfluenceEntry(edge: WorkbenchEdge | null): InfluenceEntry | null {
  if (!edge || edge.edge_type !== "influence") {
    return null;
  }
  const metadata = asRecord(edge.metadata);
  return {
    edgeId: edge.edge_id,
    sourceId: edge.source,
    targetId: edge.target,
    label: stringValue(edge.label, "影响"),
    polarity: stringValue(edge.polarity, "中性"),
    strength: toNumber(edge.strength),
    reason: stringValue(metadata.reason ?? edge.label, "未提供原因。"),
    effectOn: stringValue(metadata.effect_on),
    lagWindows: stringValue(metadata.lag_windows),
    activationCondition: stringValue(metadata.activation_condition),
    expirationCondition: stringValue(metadata.expiration_condition),
  };
}

function toInfluenceEntryFromRecord(record: Record<string, unknown>, index: number): InfluenceEntry {
  const sourceId = `clone:${stringValue(record.source_participant_id)}`;
  const targetId = `clone:${stringValue(record.target_participant_id)}`;
  return {
    edgeId: `decision-influence:${index}:${record.source_participant_id ?? "source"}:${record.target_participant_id ?? "target"}`,
    sourceId,
    targetId,
    label: stringValue(record.reason ?? record.influence_type, "影响"),
    polarity: stringValue(record.polarity, "中性"),
    strength: toNumber(record.strength),
    reason: stringValue(record.reason),
    effectOn: stringValue(record.effect_on),
    lagWindows: stringValue(record.lag_windows),
    activationCondition: stringValue(record.activation_condition),
    expirationCondition: stringValue(record.expiration_condition),
  };
}

function stripClonePrefix(value: string) {
  return value.replace(/^clone:/, "");
}
