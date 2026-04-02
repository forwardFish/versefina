"use client";

import React, { startTransition, useDeferredValue, useEffect, useMemo, useState } from "react";

import {
  continueSimulationDay,
  getDecisionTrace,
  getMarketStateTransition,
  getTradePulse,
  getWorkbenchReport,
} from "./api";
import { GraphCanvas } from "./GraphCanvas";
import { InfluenceSidebar } from "./InfluenceSidebar";
import { ReplayTimeline } from "./ReplayTimeline";
import { RightDetailPanel } from "./RightDetailPanel";
import { TradePulsePanel } from "./TradePulsePanel";
import type {
  DecisionTracePayload,
  GenericRecord,
  MarketStateTransitionPayload,
  ParticipantActionRecord,
  ParticipantRecord,
  RoundSnapshotRecord,
  TradeCard,
  TradePulsePayload,
  WorkbenchEdge,
  WorkbenchNode,
  WorkbenchReportPayload,
} from "./types";
import {
  ActionLink,
  Notice,
  StatPill,
  WorkbenchShell,
  asRecord,
  cardStyle,
  dayLabel,
  formatList,
  mutedStyle,
  primaryButtonStyle,
  softButtonStyle,
  stringValue,
  summarizeDayNarrative,
  useAsyncPayload,
  usePlaybackTimeline,
} from "./workbenchShared";
import { buildRoundGraphStage, tradeCardToEdgeId, summarizeText, useWorkbenchPayload } from "./workbenchScreenShared";

type WorkbenchMode = "workbench" | "graph" | "dual";

export function WorkbenchDetailScreen({
  eventId,
  initialRoundId = null,
}: {
  eventId: string;
  initialRoundId?: string | null;
}) {
  const [refreshNonce, setRefreshNonce] = useState(0);
  const [mode, setMode] = useState<WorkbenchMode>("workbench");
  const [selectedRoundId, setSelectedRoundId] = useState<string | null>(initialRoundId);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);
  const [tradePulse, setTradePulse] = useState<TradePulsePayload | null>(null);
  const [decisionTrace, setDecisionTrace] = useState<DecisionTracePayload | null>(null);
  const [transition, setTransition] = useState<MarketStateTransitionPayload | null>(null);
  const [runtimeError, setRuntimeError] = useState("");
  const [isContinuing, setIsContinuing] = useState(false);

  const payload = useWorkbenchPayload(eventId, refreshNonce);
  const reportPayload = useAsyncPayload<WorkbenchReportPayload>(async () => getWorkbenchReport(eventId), [eventId, refreshNonce]);

  const replayRounds = useMemo(() => payload.data?.replay.rounds ?? [], [payload.data?.replay.rounds]);
  const eventRecord = useMemo(
    () => asRecord(asRecord(payload.data?.event).record ?? payload.data?.event),
    [payload.data?.event],
  );
  const eventBodySummary = useMemo(() => summarizeText(eventRecord.body, 260), [eventRecord.body]);
  const participantsById = useMemo(
    () =>
      Object.fromEntries(
        ((payload.data?.participants.participants ?? []) as ParticipantRecord[]).map((participant) => [participant.participant_id, participant]),
      ),
    [payload.data?.participants.participants],
  );
  const selectedRoundIdDeferred = useDeferredValue(selectedRoundId);

  useEffect(() => {
    if (!selectedRoundId && replayRounds.length) {
      setSelectedRoundId(replayRounds[0]?.round_id ?? null);
    }
  }, [replayRounds, selectedRoundId]);

  const activeRound = useMemo<RoundSnapshotRecord | null>(() => {
    if (!replayRounds.length) {
      return null;
    }
    return replayRounds.find((round) => round.round_id === selectedRoundId) ?? replayRounds[0] ?? null;
  }, [replayRounds, selectedRoundId]);

  const playback = usePlaybackTimeline(replayRounds, selectedRoundId, setSelectedRoundId);

  const roundGraphStage = useMemo(() => {
    if (!payload.data?.graphStage) {
      return null;
    }
    return buildRoundGraphStage(payload.data.graphStage, activeRound);
  }, [activeRound, payload.data?.graphStage]);

  const roundStatesById = useMemo(
    () => Object.fromEntries((activeRound?.participant_states ?? []).map((state) => [String(asRecord(state).participant_id ?? ""), asRecord(state)])),
    [activeRound?.participant_states],
  );
  const roundActionsById = useMemo(
    () => Object.fromEntries((activeRound?.participant_actions ?? []).map((action) => [String(action.participant_id ?? ""), action])),
    [activeRound?.participant_actions],
  );

  useEffect(() => {
    if (!roundGraphStage) {
      return;
    }
    const nodeIds = new Set(roundGraphStage.nodes.map((node) => node.node_id));
    if (!selectedNodeId || !nodeIds.has(selectedNodeId)) {
      const eventNode = roundGraphStage.nodes.find((node) => node.node_type === "event");
      setSelectedNodeId(eventNode?.node_id ?? null);
    }
  }, [roundGraphStage, selectedNodeId]);

  useEffect(() => {
    if (!roundGraphStage) {
      return;
    }
    const edgeIds = new Set(roundGraphStage.edges.map((edge) => edge.edge_id));
    if (!selectedEdgeId || !edgeIds.has(selectedEdgeId)) {
      const firstTrade = roundGraphStage.edges.find((edge) => edge.edge_type === "trade");
      const firstInfluence = roundGraphStage.edges.find((edge) => edge.edge_type === "influence");
      setSelectedEdgeId(firstTrade?.edge_id ?? firstInfluence?.edge_id ?? null);
    }
  }, [roundGraphStage, selectedEdgeId]);

  const selectedNode = useMemo<WorkbenchNode | null>(
    () => roundGraphStage?.nodes.find((node) => node.node_id === selectedNodeId) ?? null,
    [roundGraphStage, selectedNodeId],
  );
  const selectedEdge = useMemo<WorkbenchEdge | null>(
    () => roundGraphStage?.edges.find((edge) => edge.edge_id === selectedEdgeId) ?? null,
    [roundGraphStage, selectedEdgeId],
  );
  const selectedCloneId = useMemo(() => {
    if (selectedNode?.node_type === "clone") {
      return selectedNode.node_id.replace("clone:", "");
    }
    if (selectedEdge?.source.startsWith("clone:")) {
      return selectedEdge.source.replace("clone:", "");
    }
    if (selectedEdge?.target.startsWith("clone:")) {
      return selectedEdge.target.replace("clone:", "");
    }
    return null;
  }, [selectedEdge, selectedNode]);

  useEffect(() => {
    let cancelled = false;
    async function loadTradePulse() {
      if (!selectedRoundIdDeferred) {
        return;
      }
      try {
        const response = await getTradePulse(eventId, selectedRoundIdDeferred);
        if (!cancelled) {
          setTradePulse(response);
        }
      } catch (error) {
        if (!cancelled) {
          setRuntimeError(error instanceof Error ? error.message : "加载当天流水失败。");
        }
      }
    }
    void loadTradePulse();
    return () => {
      cancelled = true;
    };
  }, [eventId, selectedRoundIdDeferred]);

  useEffect(() => {
    let cancelled = false;
    async function loadDecisionTrace() {
      if (!selectedCloneId) {
        setDecisionTrace(null);
        return;
      }
      try {
        const response = await getDecisionTrace(eventId, selectedCloneId, selectedRoundIdDeferred ?? undefined);
        if (!cancelled) {
          setDecisionTrace(response);
        }
      } catch (error) {
        if (!cancelled) {
          setRuntimeError(error instanceof Error ? error.message : "加载 Agent 决策失败。");
        }
      }
    }
    void loadDecisionTrace();
    return () => {
      cancelled = true;
    };
  }, [eventId, selectedCloneId, selectedRoundIdDeferred]);

  useEffect(() => {
    let cancelled = false;
    async function loadTransition() {
      if (!selectedRoundIdDeferred) {
        return;
      }
      try {
        const response = await getMarketStateTransition(eventId, selectedRoundIdDeferred);
        if (!cancelled) {
          setTransition(response.status === "ready" ? response : null);
        }
      } catch {
        if (!cancelled) {
          setTransition(null);
        }
      }
    }
    void loadTransition();
    return () => {
      cancelled = true;
    };
  }, [eventId, selectedRoundIdDeferred]);

  const shell = roundGraphStage?.shell ?? {};
  const selectionLabel = selectedEdge
    ? `${selectedEdge.edge_type}: ${stringValue(selectedEdge.label, selectedEdge.edge_type)}`
    : selectedNode
      ? `${selectedNode.node_type}: ${selectedNode.label}`
      : "事件";
  const homeHref = `/workbench/${eventId}${selectedRoundId ? `?round=${encodeURIComponent(selectedRoundId)}` : ""}`;

  function handleSelectRound(roundId: string) {
    playback.stop();
    startTransition(() => {
      setSelectedRoundId(roundId);
      setSelectedEdgeId(null);
    });
  }

  function handleSelectNode(nodeId: string) {
    startTransition(() => {
      setSelectedNodeId(nodeId);
    });
  }

  function handleSelectEdge(edgeId: string) {
    startTransition(() => {
      setSelectedEdgeId(edgeId);
      const edge = roundGraphStage?.edges.find((item) => item.edge_id === edgeId);
      if (!edge) {
        return;
      }
      const preferredNodeId = edge.source.startsWith("clone:")
        ? edge.source
        : edge.target.startsWith("clone:")
          ? edge.target
          : edge.source;
      setSelectedNodeId(preferredNodeId);
    });
  }

  function handleSelectTrade(card: TradeCard) {
    const edgeId = tradeCardToEdgeId(card, roundGraphStage);
    startTransition(() => {
      setSelectedNodeId(`clone:${card.participant_id}`);
      if (edgeId) {
        setSelectedEdgeId(edgeId);
      }
    });
  }

  async function handleContinueDay() {
    if (isContinuing) {
      return;
    }
    setRuntimeError("");
    setIsContinuing(true);
    playback.stop();
    try {
      const result = await continueSimulationDay(eventId);
      const latestRoundId =
        result.latest_round_result?.round_id ??
        result.new_round_results?.[result.new_round_results.length - 1]?.round_id ??
        result.round_results?.[result.round_results.length - 1]?.round_id ??
        null;
      setRefreshNonce((current) => current + 1);
      setSelectedEdgeId(null);
      if (latestRoundId) {
        setSelectedRoundId(latestRoundId);
      } else {
        setSelectedRoundId(null);
      }
    } catch (error) {
      setRuntimeError(error instanceof Error ? error.message : "继续推演下一交易日失败。");
    } finally {
      setIsContinuing(false);
    }
  }

  const mainGridTemplate =
    mode === "graph"
      ? "minmax(0, 1.6fr) minmax(360px, 0.9fr)"
      : mode === "dual"
        ? "minmax(360px, 0.96fr) minmax(0, 1.5fr)"
        : "minmax(320px, 0.84fr) minmax(0, 1.48fr) minmax(360px, 0.92fr)";

  return (
    <WorkbenchShell
      title={`${stringValue(eventRecord.title ?? asRecord(roundGraphStage?.shell).title, eventId)} 详细页面`}
      description="这里承接完整的 Agent 详情、交易边、影响边、当天故事和报告解释。"
      actions={
        <>
          <ActionLink href={homeHref} label="返回图谱首页" />
          <ActionLink href="/workbench" label="工作台首页" />
          <ActionLink href={`/event-sandbox/${eventId}/replay`} label="旧版回放" />
          <ActionLink href={`/event-sandbox/${eventId}/validation`} label="旧版验证" />
          <ActionLink href="http://127.0.0.1:8010/versefina/runtime" label="运行审计" external />
        </>
      }
    >
      {payload.status === "loading" ? <Notice>正在加载详细工作台...</Notice> : null}
      {payload.status === "error" ? <Notice tone="error">{payload.error}</Notice> : null}
      {reportPayload.status === "error" ? <Notice tone="error">Workbench 报告暂时不可用，但主推演视图仍可继续使用。</Notice> : null}
      {runtimeError ? <Notice tone="error">{runtimeError}</Notice> : null}

      {payload.data && roundGraphStage ? (
        <>
          <section style={{ ...cardStyle, padding: 18, display: "grid", gap: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap", alignItems: "flex-start" }}>
              <div style={{ display: "grid", gap: 10, maxWidth: 920 }}>
                <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                  {(["workbench", "graph", "dual"] as WorkbenchMode[]).map((viewMode) => (
                    <button key={viewMode} type="button" onClick={() => setMode(viewMode)} style={viewMode === mode ? primaryButtonStyle : softButtonStyle}>
                      {viewMode === "workbench" ? "完整工作台" : viewMode === "graph" ? "主画布+详情" : "双栏联动"}
                    </button>
                  ))}
                </div>
                <div style={{ fontSize: 24, fontWeight: 800, color: "#0f172a" }}>{stringValue(shell.title)}</div>
                <div style={mutedStyle}>{eventBodySummary}</div>
                <div style={{ ...mutedStyle, fontSize: 15 }}>{summarizeDayNarrative(activeRound)}</div>
              </div>
              <div style={{ display: "flex", gap: 10, flexWrap: "wrap", justifyContent: "flex-end" }}>
                <StatPill label="当前交易日" value={dayLabel(activeRound?.day_index ?? shell.day_index)} />
                <StatPill label="交易日期" value={stringValue(activeRound?.trade_date ?? shell.trade_date)} />
                <StatPill label="市场状态" value={stringValue(shell.market_state)} />
                <StatPill label="主导情景" value={stringValue(shell.dominant_scenario)} />
                <StatPill label="当前选中" value={selectionLabel} />
              </div>
            </div>

            <div style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
              <SummaryBlock
                label="来源"
                value={`信源 ${stringValue(eventRecord.source)} / 线索 ${stringValue(asRecord(payload.data.lineage).finahunt_run_id, "未关联")}`}
              />
              <SummaryBlock
                label="结构"
                value={`事件类型 ${stringValue(asRecord(roundGraphStage.event_graph.structure).event_type)} / 标的 ${formatList(asRecord(roundGraphStage.event_graph.mapping).symbols)}`}
              />
              <SummaryBlock
                label="当天焦点"
                value={`${dayLabel(activeRound?.day_index)} / ${stringValue(activeRound?.trade_date)} / ${stringValue(activeRound?.focus, "当天推演")}`}
              />
              <SummaryBlock
                label="当日统计"
                value={`动作 ${stringValue(activeRound?.actions_count, "0")} / 买入 ${stringValue(activeRound?.buy_clone_count, "0")} / 卖出 ${stringValue(activeRound?.sell_clone_count, "0")} / 新进 ${stringValue(activeRound?.new_entry_clone_count, "0")} / 退出 ${stringValue(activeRound?.exit_clone_count, "0")}`}
              />
            </div>
          </section>

          <ReplayTimeline
            replay={payload.data.replay}
            selectedRoundId={selectedRoundId}
            onSelectRound={handleSelectRound}
            onContinueDay={handleContinueDay}
            onJumpToFirstDay={playback.jumpToFirst}
            onTogglePlayback={playback.toggle}
            isPlaying={playback.isPlaying}
            isContinuing={isContinuing}
            sticky
          />

          <section style={{ display: "grid", gap: 18, gridTemplateColumns: mainGridTemplate, alignItems: "start" }}>
            {mode !== "graph" ? (
              <InfluenceSidebar
                graphStage={roundGraphStage}
                activeRound={activeRound}
                selectedNode={selectedNode}
                selectedEdge={selectedEdge}
                decisionTrace={decisionTrace}
                transition={transition}
                onSelectNode={handleSelectNode}
                onSelectEdge={handleSelectEdge}
              />
            ) : null}

            <GraphCanvas
              graphStage={roundGraphStage}
              activeRound={activeRound}
              tradePulse={tradePulse}
              selectedNodeId={selectedNodeId}
              selectedEdgeId={selectedEdgeId}
              onSelectNode={handleSelectNode}
              onSelectEdge={handleSelectEdge}
              participantsById={participantsById}
              roundStatesById={roundStatesById}
              roundActionsById={roundActionsById}
            />

            {mode !== "dual" ? (
              <RightDetailPanel
                graphStage={roundGraphStage}
                tradePulse={tradePulse}
                decisionTrace={decisionTrace}
                transition={transition}
                selectedNode={selectedNode}
                selectedEdge={selectedEdge}
                report={reportPayload.data}
                validation={payload.data.validation as never}
                activeRound={activeRound}
              />
            ) : null}
          </section>

          <TradePulsePanel
            tradePulse={tradePulse}
            marketMetrics={asRecord(transition?.market_metrics ?? activeRound?.market_state)}
            participantsById={participantsById}
            onSelectTrade={handleSelectTrade}
          />
        </>
      ) : null}
    </WorkbenchShell>
  );
}

function SummaryBlock({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ ...cardStyle, padding: 14 }}>
      <div style={{ fontSize: 12, letterSpacing: "0.08em", textTransform: "uppercase", color: "#64748b", fontWeight: 700 }}>{label}</div>
      <div style={{ ...mutedStyle, marginTop: 8 }}>{value}</div>
    </div>
  );
}
