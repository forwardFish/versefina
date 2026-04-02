"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";

import type {
  GenericRecord,
  GraphStagePayload,
  ParticipantActionRecord,
  ParticipantRecord,
  RoundSnapshotRecord,
  TradePulsePayload,
  WorkbenchEdge,
  WorkbenchNode,
} from "./types";
import {
  asRecord,
  cardStyle,
  cloneAlias,
  dayLabel,
  edgeTypeColor,
  familyLabel,
  familyVisualMeta,
  formatCurrency,
  formatShares,
  mutedStyle,
  orderSideLabel,
  primaryButtonStyle,
  softButtonStyle,
  strengthWidth,
  stringValue,
  subtleCardStyle,
  toNumber,
} from "./workbenchShared";

type GraphCanvasProps = {
  graphStage: GraphStagePayload;
  activeRound: RoundSnapshotRecord | null;
  tradePulse: TradePulsePayload | null;
  selectedNodeId: string | null;
  selectedEdgeId: string | null;
  onSelectNode: (nodeId: string) => void;
  onSelectEdge: (edgeId: string) => void;
  participantsById: Record<string, ParticipantRecord>;
  roundStatesById: Record<string, GenericRecord>;
  roundActionsById: Record<string, ParticipantActionRecord>;
};

type PositionedNode = WorkbenchNode & {
  x: number;
  y: number;
  width: number;
  height: number;
};

const CANVAS_WIDTH = 1240;
const CANVAS_HEIGHT = 720;
const MIN_ZOOM = 0.7;
const MAX_ZOOM = 1.55;

export function GraphCanvas({
  graphStage,
  activeRound,
  tradePulse,
  selectedNodeId,
  selectedEdgeId,
  onSelectNode,
  onSelectEdge,
  participantsById,
  roundStatesById,
  roundActionsById,
}: GraphCanvasProps) {
  const [edgeFilter, setEdgeFilter] = useState<"all" | "trade" | "influence">("all");
  const [showEdgeLabels, setShowEdgeLabels] = useState(true);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [draggingCanvas, setDraggingCanvas] = useState<null | { startX: number; startY: number; originX: number; originY: number }>(null);
  const [draggingNode, setDraggingNode] = useState<null | { nodeId: string; startX: number; startY: number; originX: number; originY: number }>(null);
  const canvasRef = useRef<HTMLDivElement | null>(null);

  const activeCloneIds = useMemo(() => {
    const ids = new Set<string>();
    (activeRound?.participant_actions ?? []).forEach((action) => {
      ids.add(String(action.participant_id ?? ""));
    });
    (activeRound?.influence_edges ?? []).forEach((edge) => {
      ids.add(String(edge.source_participant_id ?? ""));
      ids.add(String(edge.target_participant_id ?? ""));
    });
    return ids;
  }, [activeRound?.influence_edges, activeRound?.participant_actions]);

  const storyEdges = useMemo(
    () =>
      graphStage.edges.filter((edge) => {
        if (edge.edge_type === "event") {
          return false;
        }
        if (edgeFilter === "all") {
          return true;
        }
        return edge.edge_type === edgeFilter;
      }),
    [edgeFilter, graphStage.edges],
  );
  const backgroundEdges = useMemo(() => graphStage.edges.filter((edge) => edge.edge_type === "event"), [graphStage.edges]);
  const focusBundle = useMemo(() => buildFocusBundle(storyEdges, selectedNodeId, selectedEdgeId), [selectedEdgeId, selectedNodeId, storyEdges]);
  const visibleNodeIds = useMemo(() => buildVisibleNodeIds(graphStage.nodes, backgroundEdges, storyEdges, selectedNodeId, selectedEdgeId), [
    backgroundEdges,
    graphStage.nodes,
    selectedEdgeId,
    selectedNodeId,
    storyEdges,
  ]);

  const initialNodes = useMemo(() => positionNodes(graphStage.nodes, activeRound, visibleNodeIds), [activeRound, graphStage.nodes, visibleNodeIds]);
  const [nodePositions, setNodePositions] = useState<Record<string, PositionedNode>>({});

  useEffect(() => {
    setNodePositions(Object.fromEntries(initialNodes.map((node) => [node.node_id, node])));
    setPan({ x: 0, y: 0 });
    setZoom(1);
  }, [graphStage.current_highlights?.active_round_id, initialNodes]);

  useEffect(() => {
    if (!draggingCanvas && !draggingNode) {
      return;
    }
    function handlePointerMove(event: MouseEvent) {
      if (draggingCanvas) {
        setPan({
          x: draggingCanvas.originX + (event.clientX - draggingCanvas.startX),
          y: draggingCanvas.originY + (event.clientY - draggingCanvas.startY),
        });
      }
      if (draggingNode) {
        const deltaX = (event.clientX - draggingNode.startX) / zoom;
        const deltaY = (event.clientY - draggingNode.startY) / zoom;
        setNodePositions((current) => {
          const target = current[draggingNode.nodeId];
          if (!target) {
            return current;
          }
          return {
            ...current,
            [draggingNode.nodeId]: {
              ...target,
              x: clamp(draggingNode.originX + deltaX, 12, CANVAS_WIDTH - target.width - 12),
              y: clamp(draggingNode.originY + deltaY, 12, CANVAS_HEIGHT - target.height - 12),
            },
          };
        });
      }
    }
    function handlePointerUp() {
      setDraggingCanvas(null);
      setDraggingNode(null);
    }
    window.addEventListener("mousemove", handlePointerMove);
    window.addEventListener("mouseup", handlePointerUp);
    return () => {
      window.removeEventListener("mousemove", handlePointerMove);
      window.removeEventListener("mouseup", handlePointerUp);
    };
  }, [draggingCanvas, draggingNode, zoom]);

  const visibleNodes = useMemo(
    () => Object.values(nodePositions).filter((node) => visibleNodeIds.has(node.node_id)),
    [nodePositions, visibleNodeIds],
  );
  const nodeLookup = useMemo(() => Object.fromEntries(visibleNodes.map((node) => [node.node_id, node])), [visibleNodes]);
  const renderedBackgroundEdges = useMemo(
    () => backgroundEdges.filter((edge) => nodeLookup[edge.source] && nodeLookup[edge.target] && shouldRenderBackgroundEdge(edge, nodeLookup)),
    [backgroundEdges, nodeLookup],
  );
  const renderedStoryEdges = useMemo(
    () => storyEdges.filter((edge) => nodeLookup[edge.source] && nodeLookup[edge.target]),
    [nodeLookup, storyEdges],
  );

  return (
    <article style={{ ...cardStyle, padding: 18, minHeight: 760, display: "grid", gap: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 14, alignItems: "flex-start", flexWrap: "wrap" }}>
        <div style={{ maxWidth: 860 }}>
          <div style={{ fontSize: 12, letterSpacing: "0.12em", textTransform: "uppercase", color: "#64748b", fontWeight: 700 }}>
            当天 Agent 舞台
          </div>
          <div style={{ marginTop: 8, fontSize: 28, fontWeight: 800, color: "#0f172a" }}>谁买、谁卖、谁影响了谁</div>
          <div style={{ ...mutedStyle, marginTop: 10 }}>
            {activeRound
              ? `${dayLabel(activeRound.day_index)} / ${stringValue(activeRound.trade_date)}：聚焦当天真实交易边、影响边和新增参与者，事件骨架仅保留为背景。`
              : "当前还没有可视化的日内结果。"}
          </div>
        </div>
        <div style={{ ...subtleCardStyle, padding: 14, minWidth: 320, display: "grid", gap: 8 }}>
          <div style={{ fontSize: 12, letterSpacing: "0.08em", textTransform: "uppercase", color: "#64748b", fontWeight: 700 }}>
            当天焦点
          </div>
          <div style={{ fontSize: 16, fontWeight: 700, color: "#0f172a" }}>
            {tradePulse?.market_pulse_summary ?? "尚未返回当天交易脉冲。"}
          </div>
          <div style={{ ...mutedStyle, fontSize: 12 }}>
            活跃 Agent {activeCloneIds.size} / 交易动作 {stringValue(activeRound?.actions_count, "0")} / 影响边 {activeRound?.influence_edges.length ?? 0}
          </div>
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          {(["all", "trade", "influence"] as const).map((item) => (
            <button key={item} type="button" onClick={() => setEdgeFilter(item)} style={edgeFilter === item ? primaryButtonStyle : softButtonStyle}>
              {item === "all" ? "全部关系" : item === "trade" ? "只看交易边" : "只看影响边"}
            </button>
          ))}
          <button type="button" onClick={() => setShowEdgeLabels((current) => !current)} style={showEdgeLabels ? primaryButtonStyle : softButtonStyle}>
            {showEdgeLabels ? "隐藏边标签" : "显示边标签"}
          </button>
        </div>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <button type="button" onClick={() => setZoom((current) => clampZoom(current - 0.12))} style={softButtonStyle}>
            缩小
          </button>
          <button type="button" onClick={() => setZoom((current) => clampZoom(current + 0.12))} style={softButtonStyle}>
            放大
          </button>
          <button
            type="button"
            onClick={() => {
              setZoom(1);
              setPan({ x: 0, y: 0 });
              setNodePositions(Object.fromEntries(initialNodes.map((node) => [node.node_id, node])));
            }}
            style={primaryButtonStyle}
          >
            重置视图
          </button>
        </div>
      </div>

      <div
        ref={canvasRef}
        onWheel={(event) => {
          if (!event.ctrlKey && !event.metaKey) {
            return;
          }
          event.preventDefault();
          setZoom((current) => clampZoom(current + (event.deltaY < 0 ? 0.06 : -0.06)));
        }}
        onMouseDown={(event) => {
          if (event.target !== event.currentTarget) {
            return;
          }
          setDraggingCanvas({ startX: event.clientX, startY: event.clientY, originX: pan.x, originY: pan.y });
        }}
        style={{
          position: "relative",
          minHeight: 660,
          borderRadius: 24,
          overflow: "hidden",
          border: "1px solid rgba(148, 163, 184, 0.16)",
          background:
            "radial-gradient(circle at 12% 18%, rgba(37,99,235,0.12), transparent 18%), radial-gradient(circle at 82% 12%, rgba(249,115,22,0.10), transparent 18%), linear-gradient(180deg, rgba(255,255,255,0.99), rgba(248,250,252,0.98))",
          cursor: draggingCanvas ? "grabbing" : "grab",
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: "0 0",
          }}
        >
          <svg viewBox={`0 0 ${CANVAS_WIDTH} ${CANVAS_HEIGHT}`} style={{ position: "absolute", inset: 0, width: CANVAS_WIDTH, height: CANVAS_HEIGHT }}>
            <defs>
              <marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(37,99,235,0.86)" />
              </marker>
              <marker id="arrow-orange" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(249,115,22,0.86)" />
              </marker>
              <marker id="arrow-green" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(22,163,74,0.82)" />
              </marker>
              <marker id="arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(220,38,38,0.82)" />
              </marker>
              <marker id="arrow-gray" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(100,116,139,0.42)" />
              </marker>
            </defs>

            {renderedBackgroundEdges.map((edge) => {
              const source = nodeLookup[edge.source];
              const target = nodeLookup[edge.target];
              if (!source || !target) {
                return null;
              }
              const path = edgePath(edge, source, target);
              return (
                <g key={edge.edge_id}>
                  <path d={path.d} fill="none" stroke="rgba(148,163,184,0.2)" strokeWidth={1.4} opacity={0.4} markerEnd="url(#arrow-gray)" />
                  {showEdgeLabels ? (
                    <text x={path.labelX} y={path.labelY} fontSize="11" fill="rgba(100,116,139,0.7)" textAnchor="middle">
                      {stringValue(edge.label)}
                    </text>
                  ) : null}
                </g>
              );
            })}

            {renderedStoryEdges.map((edge) => {
              const source = nodeLookup[edge.source];
              const target = nodeLookup[edge.target];
              if (!source || !target) {
                return null;
              }
              const selected = edge.edge_id === selectedEdgeId;
              const related = isRelatedEdge(edge, focusBundle);
              const path = edgePath(edge, source, target);
              const color = edgeTypeColor(edge.edge_type, edge.polarity, asRecord(edge.metadata).order_side);
              return (
                <g key={edge.edge_id}>
                  <path
                    d={path.d}
                    fill="none"
                    stroke={color}
                    strokeWidth={selected ? strengthWidth(edge.strength) + 1.2 : strengthWidth(edge.strength)}
                    strokeDasharray={edge.edge_type === "trade" ? "10 8" : undefined}
                    opacity={selected ? 1 : related ? 0.92 : focusBundle.active ? 0.18 : 0.78}
                    markerEnd={`url(#${markerId(edge)})`}
                    onClick={() => onSelectEdge(edge.edge_id)}
                    style={{ cursor: "pointer" }}
                  />
                  {showEdgeLabels ? (
                    <text
                      x={path.labelX}
                      y={path.labelY}
                      fontSize="12"
                      fill={selected ? "#0f172a" : color}
                      textAnchor="middle"
                      style={{ pointerEvents: "none", fontWeight: 700 }}
                    >
                      {stringValue(edge.label)}
                    </text>
                  ) : null}
                </g>
              );
            })}
          </svg>

          {visibleNodes.map((node) => {
            const cloneId = node.node_type === "clone" ? node.node_id.replace("clone:", "") : "";
            const participant = cloneId ? participantsById[cloneId] : undefined;
            const roundState = cloneId ? asRecord(roundStatesById[cloneId]) : {};
            const roundAction = cloneId ? asRecord(roundActionsById[cloneId]) : {};
            const selected = node.node_id === selectedNodeId;
            const related = isRelatedNode(node.node_id, focusBundle, node.node_type);
            const cloneCollapsed = node.node_type === "clone" && hoveredNodeId !== node.node_id;
            return (
              <button
                key={node.node_id}
                type="button"
                onClick={() => onSelectNode(node.node_id)}
                onMouseEnter={() => setHoveredNodeId(node.node_id)}
                onMouseLeave={() => setHoveredNodeId((current) => (current === node.node_id ? null : current))}
                onMouseDown={(event) => {
                  event.stopPropagation();
                  setDraggingNode({ nodeId: node.node_id, startX: event.clientX, startY: event.clientY, originX: node.x, originY: node.y });
                }}
                style={nodeStyle(node, participant, roundState, roundAction, selected, related, cloneCollapsed)}
              >
                {node.node_type === "clone" ? (
                  <CloneNodeBody node={node} participant={participant} roundState={roundState} roundAction={roundAction} collapsed={cloneCollapsed} />
                ) : (
                  <StaticNodeBody node={node} />
                )}
              </button>
            );
          })}
        </div>
      </div>

      <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))" }}>
        <LegendItem label="事件背景层" color="rgba(148,163,184,0.48)" description="事件骨架、信号和标的仅作低透明度背景参考" />
        <LegendItem label="买入交易边" color="rgba(37,99,235,0.86)" description="当天真实买入或加仓动作" dashed />
        <LegendItem label="卖出交易边" color="rgba(249,115,22,0.86)" description="当天减仓或退出动作" dashed />
        <LegendItem label="看多 / 看空影响边" color="rgba(22,163,74,0.82)" description="绿色看多、红色看空，展示当天影响扩散" curved />
      </div>
    </article>
  );
}

function CloneNodeBody({
  node,
  participant,
  roundState,
  roundAction,
  collapsed,
}: {
  node: PositionedNode;
  participant?: ParticipantRecord;
  roundState: GenericRecord;
  roundAction: GenericRecord;
  collapsed: boolean;
}) {
  const participantId = node.node_id.replace("clone:", "");
  const family = participant?.participant_family ?? node.metadata?.participant_family ?? node.group;
  const visual = familyVisualMeta(family);
  const alias = cloneAlias(participantId);
  if (collapsed) {
    return (
      <div style={{ display: "grid", justifyItems: "start", gap: 6 }}>
        <div
          style={{
            width: 44,
            height: 44,
            borderRadius: 999,
            display: "grid",
            placeItems: "center",
            fontSize: 20,
            fontWeight: 900,
            color: visual.accent,
            background: "rgba(255,255,255,0.96)",
            border: `2px solid ${visual.border}`,
            boxShadow: "0 10px 20px rgba(15,23,42,0.08)",
          }}
        >
          {alias}
        </div>
        <div style={{ fontSize: 11, fontWeight: 700, color: visual.accent }}>散户</div>
      </div>
    );
  }
  return (
    <div style={{ display: "grid", gap: 8 }}>
      <div
        style={{
          width: 44,
          height: 44,
          borderRadius: 999,
          display: "grid",
          placeItems: "center",
          fontSize: 20,
          fontWeight: 900,
          color: visual.accent,
          background: "rgba(255,255,255,0.92)",
          border: `2px solid ${visual.border}`,
        }}
      >
        {alias}
      </div>
      <div style={{ fontSize: 18, fontWeight: 800, color: "#0f172a" }}>{familyLabel(family)}</div>
      <div style={{ ...mutedStyle, fontSize: 12 }}>{participantId}</div>
      <div style={{ display: "grid", gap: 4, color: "#0f172a", fontSize: 12, fontWeight: 700 }}>
        <div>{stringValue(roundAction.action_name ?? roundAction.action_type, "今日观望")}</div>
        <div>{orderSideLabel(roundAction.order_side, "无交易")} / {formatShares(roundAction.trade_quantity)}</div>
        <div>现金 {formatCurrency(roundState.cash_available ?? participant?.cash_available)}</div>
      </div>
    </div>
  );
}

function StaticNodeBody({ node }: { node: PositionedNode }) {
  return (
    <div style={{ display: "grid", gap: 6 }}>
      <div style={{ fontSize: 11, letterSpacing: "0.08em", textTransform: "uppercase", color: "#64748b", fontWeight: 700 }}>
        {node.node_type}
      </div>
      <div style={{ fontSize: 15, fontWeight: 800, color: "#0f172a", lineHeight: 1.35 }}>{node.label}</div>
      <div style={{ ...mutedStyle, fontSize: 12 }}>{stringValue(node.metadata?.event_type ?? node.metadata?.participant_family ?? node.group)}</div>
    </div>
  );
}

function LegendItem({
  label,
  color,
  description,
  dashed = false,
  curved = false,
}: {
  label: string;
  color: string;
  description: string;
  dashed?: boolean;
  curved?: boolean;
}) {
  return (
    <div style={{ ...subtleCardStyle, padding: 12, display: "grid", gap: 8 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <svg width="36" height="14" viewBox="0 0 36 14" aria-hidden="true">
          {curved ? (
            <path d="M2 11 Q18 1 34 11" fill="none" stroke={color} strokeWidth="3" />
          ) : (
            <line x1="2" y1="7" x2="34" y2="7" stroke={color} strokeWidth="3" strokeDasharray={dashed ? "8 6" : undefined} />
          )}
        </svg>
        <div style={{ fontWeight: 800, color: "#0f172a" }}>{label}</div>
      </div>
      <div style={{ ...mutedStyle, fontSize: 12 }}>{description}</div>
    </div>
  );
}

function nodeStyle(
  node: PositionedNode,
  participant: ParticipantRecord | undefined,
  roundState: GenericRecord,
  roundAction: GenericRecord,
  selected: boolean,
  related: boolean,
  collapsed: boolean,
): React.CSSProperties {
  if (node.node_type === "clone") {
    const family = participant?.participant_family ?? node.metadata?.participant_family ?? node.group;
    const visual = familyVisualMeta(family);
      if (collapsed) {
        return {
        position: "absolute",
        left: node.x,
        top: node.y,
        width: node.width,
        minHeight: node.height,
        borderRadius: 26,
        padding: "12px",
        border: "1px solid transparent",
        background: "transparent",
        boxShadow: "none",
        textAlign: "left",
        cursor: "grab",
        opacity: related ? 0.92 : 0.3,
        overflow: "visible",
      };
    }
    return {
      position: "absolute",
      left: node.x,
      top: node.y,
      width: node.width,
      minHeight: node.height,
      borderRadius: 26,
      padding: "14px 14px 12px",
      border: selected ? `2px solid ${visual.accent}` : `1px solid ${visual.border}`,
      background: visual.background,
      boxShadow: selected ? "0 18px 34px rgba(59,130,246,0.18)" : "0 10px 18px rgba(15,23,42,0.07)",
      textAlign: "left",
      cursor: "grab",
      opacity: related ? 1 : 0.24,
      overflow: "hidden",
    };
  }
  const isCore = node.node_type === "event" || node.node_type === "symbol";
  return {
    position: "absolute",
    left: node.x,
    top: node.y,
    width: node.width,
    minHeight: node.height,
    borderRadius: 20,
    padding: "12px 12px 10px",
    border: selected ? "2px solid rgba(59,130,246,0.36)" : "1px solid rgba(148,163,184,0.2)",
    background: isCore ? "rgba(255,255,255,0.92)" : "rgba(248,250,252,0.84)",
    textAlign: "left",
    cursor: "grab",
    opacity: selected ? 0.9 : isCore ? 0.55 : 0.34,
  };
}

function positionNodes(nodes: WorkbenchNode[], activeRound: RoundSnapshotRecord | null, visibleNodeIds: Set<string>): PositionedNode[] {
  const actionMap = new Map<string, ParticipantActionRecord>(
    (activeRound?.participant_actions ?? []).map((action) => [String(action.participant_id ?? ""), action]),
  );
  const cloneNodes = nodes.filter((node) => node.node_type === "clone" && visibleNodeIds.has(node.node_id));
  const staticNodes = nodes.filter((node) => node.node_type !== "clone" && node.node_type !== "family" && visibleNodeIds.has(node.node_id));
  const positioned: PositionedNode[] = [];

  staticNodes
    .filter((node) => node.node_type === "event")
    .forEach((node, index) => positioned.push({ ...node, x: 44, y: 274 + index * 96, width: 176, height: 88 }));
  staticNodes
    .filter((node) => node.node_type === "signal" || node.node_type === "risk")
    .forEach((node, index) => {
      const column = index % 2;
      const row = Math.floor(index / 2);
      positioned.push({ ...node, x: 232 + column * 146, y: 64 + row * 110, width: 132, height: 72 });
    });
  staticNodes
    .filter((node) => ["symbol", "commodity", "sector"].includes(node.node_type))
    .forEach((node, index) => {
      const row = index % 3;
      const column = Math.floor(index / 3);
      positioned.push({ ...node, x: 292 + column * 148, y: 198 + row * 92, width: 136, height: 74 });
    });

  const buyNodes = cloneNodes.filter((node) => String(actionMap.get(node.node_id.replace("clone:", ""))?.order_side ?? "").toLowerCase() === "buy");
  const sellNodes = cloneNodes.filter((node) => String(actionMap.get(node.node_id.replace("clone:", ""))?.order_side ?? "").toLowerCase() === "sell");
  const neutralNodes = cloneNodes.filter((node) => !buyNodes.includes(node) && !sellNodes.includes(node));

  placeCloneLane(positioned, buyNodes, 486, 94);
  placeCloneLane(positioned, neutralNodes, 486, 284);
  placeCloneLane(positioned, sellNodes, 486, 490);
  return positioned;
}

function placeCloneLane(target: PositionedNode[], nodes: WorkbenchNode[], startX: number, startY: number) {
  nodes.forEach((node, index) => {
    const column = index % 3;
    const row = Math.floor(index / 3);
    target.push({ ...node, x: startX + column * 196, y: startY + row * 132, width: 170, height: 126 });
  });
}

function buildVisibleNodeIds(
  nodes: WorkbenchNode[],
  backgroundEdges: WorkbenchEdge[],
  storyEdges: WorkbenchEdge[],
  selectedNodeId: string | null,
  selectedEdgeId: string | null,
) {
  const nodeTypeById = Object.fromEntries(nodes.map((node) => [node.node_id, node.node_type]));
  const ids = new Set<string>();
  ids.add(nodes.find((node) => node.node_type === "event")?.node_id ?? "");
  storyEdges.forEach((edge) => {
    ids.add(edge.source);
    ids.add(edge.target);
  });
  if (selectedNodeId) {
    ids.add(selectedNodeId);
  }
  if (selectedEdgeId) {
    const edge = storyEdges.find((item) => item.edge_id === selectedEdgeId);
    if (edge) {
      ids.add(edge.source);
      ids.add(edge.target);
    }
  }
  backgroundEdges.forEach((edge) => {
    const sourceType = nodeTypeById[edge.source];
    const targetType = nodeTypeById[edge.target];
    if (sourceType !== "family" && targetType !== "family" && (ids.has(edge.source) || ids.has(edge.target) || edge.source.startsWith("event:"))) {
      ids.add(edge.source);
      ids.add(edge.target);
    }
  });
  ids.delete("");
  return ids;
}

function shouldRenderBackgroundEdge(edge: WorkbenchEdge, nodeLookup: Record<string, PositionedNode>) {
  const source = nodeLookup[edge.source];
  const target = nodeLookup[edge.target];
  if (!source || !target) {
    return false;
  }
  return source.node_type !== "family" && target.node_type !== "family";
}

function buildFocusBundle(edges: WorkbenchEdge[], selectedNodeId: string | null, selectedEdgeId: string | null) {
  if (!selectedNodeId && !selectedEdgeId) {
    return { active: false, nodeIds: new Set<string>(), edgeIds: new Set<string>() };
  }
  const nodeIds = new Set<string>();
  const edgeIds = new Set<string>();
  if (selectedNodeId) {
    nodeIds.add(selectedNodeId);
    edges.forEach((edge) => {
      if (edge.source === selectedNodeId || edge.target === selectedNodeId) {
        edgeIds.add(edge.edge_id);
        nodeIds.add(edge.source);
        nodeIds.add(edge.target);
      }
    });
  }
  if (selectedEdgeId) {
    const edge = edges.find((item) => item.edge_id === selectedEdgeId);
    if (edge) {
      edgeIds.add(edge.edge_id);
      nodeIds.add(edge.source);
      nodeIds.add(edge.target);
    }
  }
  return { active: true, nodeIds, edgeIds };
}

function isRelatedNode(nodeId: string, focusBundle: { active: boolean; nodeIds: Set<string> }, nodeType: string) {
  if (!focusBundle.active) {
    return true;
  }
  if (nodeType !== "clone") {
    return true;
  }
  return focusBundle.nodeIds.has(nodeId);
}

function isRelatedEdge(edge: WorkbenchEdge, focusBundle: { active: boolean; nodeIds: Set<string>; edgeIds: Set<string> }) {
  return !focusBundle.active || focusBundle.edgeIds.has(edge.edge_id) || (focusBundle.nodeIds.has(edge.source) && focusBundle.nodeIds.has(edge.target));
}

function edgePath(edge: WorkbenchEdge, source: PositionedNode, target: PositionedNode) {
  const start = { x: source.x + source.width / 2, y: source.y + source.height / 2 };
  const end = { x: target.x + target.width / 2, y: target.y + target.height / 2 };
  if (edge.edge_type === "influence") {
    const controlX = (start.x + end.x) / 2;
    const controlY = Math.min(start.y, end.y) - 56;
    return {
      d: `M ${start.x} ${start.y} Q ${controlX} ${controlY} ${end.x} ${end.y}`,
      labelX: controlX,
      labelY: controlY - 8,
    };
  }
  return {
    d: `M ${start.x} ${start.y} L ${end.x} ${end.y}`,
    labelX: (start.x + end.x) / 2,
    labelY: (start.y + end.y) / 2 - 10,
  };
}

function markerId(edge: WorkbenchEdge) {
  if (edge.edge_type === "trade") {
    return String(asRecord(edge.metadata).order_side ?? "").toLowerCase() === "sell" ? "arrow-orange" : "arrow-blue";
  }
  if (edge.edge_type === "influence") {
    return String(edge.polarity ?? "").toLowerCase().includes("bear") ? "arrow-red" : "arrow-green";
  }
  return "arrow-gray";
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function clampZoom(value: number) {
  return clamp(value, MIN_ZOOM, MAX_ZOOM);
}
