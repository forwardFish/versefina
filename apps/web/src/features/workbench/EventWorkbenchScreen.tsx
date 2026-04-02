"use client";

import React, { startTransition, useEffect, useMemo, useState } from "react";

import { continueSimulationDay, getTradePulse } from "./api";
import { GraphCanvas } from "./GraphCanvas";
import { ReplayTimeline } from "./ReplayTimeline";
import { WorkbenchCatalystCard } from "./WorkbenchCatalystCard";
import type {
  GenericRecord,
  ParticipantActionRecord,
  ParticipantRecord,
  RoundSnapshotRecord,
  TradePulsePayload,
} from "./types";
import {
  Notice,
  asRecord,
  containerStyle,
  shellStyle,
  usePlaybackTimeline,
} from "./workbenchShared";
import { buildRoundGraphStage, summarizeText, useWorkbenchPayload } from "./workbenchScreenShared";

export function EventWorkbenchScreen({
  eventId,
  initialRoundId = null,
}: {
  eventId: string;
  initialRoundId?: string | null;
}) {
  const [refreshNonce, setRefreshNonce] = useState(0);
  const [selectedRoundId, setSelectedRoundId] = useState<string | null>(initialRoundId);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);
  const [tradePulse, setTradePulse] = useState<TradePulsePayload | null>(null);
  const [runtimeError, setRuntimeError] = useState("");
  const [isContinuing, setIsContinuing] = useState(false);

  const payload = useWorkbenchPayload(eventId, refreshNonce);
  const replayRounds = useMemo(() => payload.data?.replay.rounds ?? [], [payload.data?.replay.rounds]);
  const eventRecord = useMemo(
    () => asRecord(asRecord(payload.data?.event).record ?? payload.data?.event),
    [payload.data?.event],
  );

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

  const participantsById = useMemo(
    () =>
      Object.fromEntries(
        ((payload.data?.participants.participants ?? []) as ParticipantRecord[]).map((participant) => [participant.participant_id, participant]),
      ),
    [payload.data?.participants.participants],
  );
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

  useEffect(() => {
    let cancelled = false;
    async function loadTradePulse() {
      if (!selectedRoundId) {
        return;
      }
      try {
        const response = await getTradePulse(eventId, selectedRoundId);
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
  }, [eventId, selectedRoundId]);

  function handleSelectRound(roundId: string) {
    playback.stop();
    startTransition(() => {
      setSelectedRoundId(roundId);
      setSelectedEdgeId(null);
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
      setSelectedRoundId(latestRoundId);
    } catch (error) {
      setRuntimeError(error instanceof Error ? error.message : "继续推演下一交易日失败。");
    } finally {
      setIsContinuing(false);
    }
  }

  const eventType = String(asRecord(roundGraphStage?.event_graph.structure).event_type ?? "");
  const symbols = asRecord(roundGraphStage?.event_graph.mapping).symbols;
  const detailHref = `/workbench/${eventId}/detail${selectedRoundId ? `?round=${encodeURIComponent(selectedRoundId)}` : ""}`;
  const catalystSummary = summarizeText(
    activeRound?.focus || tradePulse?.market_pulse_summary || eventRecord.body,
    160,
  );

  return (
    <main style={shellStyle}>
      <div style={containerStyle}>
        {payload.status === "loading" ? <Notice>正在加载图谱首页...</Notice> : null}
        {payload.status === "error" ? <Notice tone="error">{payload.error}</Notice> : null}
        {runtimeError ? <Notice tone="error">{runtimeError}</Notice> : null}

        {payload.data && roundGraphStage ? (
          <div style={{ display: "grid", gap: 18 }}>
            <WorkbenchCatalystCard
              title={String(eventRecord.title ?? eventId)}
              summary={catalystSummary}
              eventType={eventType || "未标注"}
              symbols={symbols}
              dayIndex={activeRound?.day_index ?? roundGraphStage.shell.day_index}
              tradeDate={String(activeRound?.trade_date ?? roundGraphStage.shell.trade_date ?? "")}
              detailHref={detailHref}
            />

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
              variant="compact"
            />

            <GraphCanvas
              graphStage={roundGraphStage}
              activeRound={activeRound}
              tradePulse={tradePulse}
              selectedNodeId={selectedNodeId}
              selectedEdgeId={selectedEdgeId}
              onSelectNode={setSelectedNodeId}
              onSelectEdge={setSelectedEdgeId}
              participantsById={participantsById}
              roundStatesById={roundStatesById}
              roundActionsById={roundActionsById as Record<string, ParticipantActionRecord>}
            />
          </div>
        ) : null}
      </div>
    </main>
  );
}
