"use client";

import { getInfluenceGraph, getParticipants, getReplay } from "./api";
import type { InfluenceEdgeRecord, InfluenceGraphPayload, ParticipantActionRecord, ParticipantRecord, ReplayPayload } from "./types";
import {
  ActionLink,
  JsonCard,
  MiniCard,
  Notice,
  PageShell,
  SectionHeader,
  cardStyle,
  gridThreeStyle,
  gridTwoStyle,
  mutedStyle,
  numberString,
  panelStyle,
  stringValue,
  useAsyncPayload,
  joinList,
  Pill,
} from "./shared";

export function EventSandboxParticipantScreen({
  eventId,
  participantId,
}: {
  eventId: string;
  participantId: string;
}) {
  const state = useAsyncPayload(
    async () => {
      const [participants, replay, influence] = await Promise.all([
        getParticipants(eventId),
        getReplay(eventId),
        getInfluenceGraph(eventId),
      ]);
      return { participants, replay, influence };
    },
    [eventId, participantId],
  );

  const participant =
    state.data?.participants.participants.find((item: ParticipantRecord) => item.participant_id === participantId) ?? null;
  const actionTrail = collectParticipantActions(state.data?.replay, participantId);
  const incomingEdges = collectInfluenceEdges(state.data?.influence, participantId, "incoming");
  const outgoingEdges = collectInfluenceEdges(state.data?.influence, participantId, "outgoing");

  return (
    <PageShell
      eyebrow="Participant Drilldown"
      title={participantId}
      description="Inspect how one participant moved across rounds, what signals it reacted to, and which other participants it influenced."
      actions={
        <>
          <ActionLink href={`/event-sandbox/${eventId}`} label="Overview" />
          <ActionLink href={`/event-sandbox/${eventId}/replay`} label="Replay" />
          <ActionLink href={`/event-sandbox/${eventId}/validation`} label="Validation" />
        </>
      }
    >
      {state.status === "loading" ? <Notice>Loading participant drilldown...</Notice> : null}
      {state.status === "error" ? <Notice tone="error">{state.error}</Notice> : null}
      {participant ? (
        <>
          <section style={panelStyle}>
            <SectionHeader
              eyebrow="Participant"
              title={participant.participant_family}
              description={participant.expected_impact ?? "No participant summary available."}
            />
            <div style={gridThreeStyle}>
              <MiniCard title="Stance" value={stringValue(participant.stance)} />
              <MiniCard title="Authority" value={numberString(participant.authority_weight)} />
              <MiniCard title="Confidence" value={numberString(participant.confidence)} />
              <MiniCard title="Time horizon" value={stringValue(participant.time_horizon)} />
              <MiniCard title="Risk budget" value={stringValue(participant.risk_budget_profile)} />
              <MiniCard title="First movers" value={joinList(participant.first_movers)} />
            </div>
          </section>
          <section style={{ ...panelStyle, marginTop: 20 }}>
            <SectionHeader
              eyebrow="Action trail"
              title="Round-by-round actions"
              description="This is the action history pulled from the replay payload."
            />
            <div style={{ display: "grid", gap: 14 }}>
              {actionTrail.length ? actionTrail.map((action, index) => <ActionCard key={`${action.round_id}-${index}`} action={action} />) : <Notice>No participant actions found in the replay payload.</Notice>}
            </div>
          </section>
          <section style={{ ...panelStyle, marginTop: 20 }}>
            <SectionHeader
              eyebrow="Influence"
              title="Incoming and outgoing influence"
              description="These edges show how the participant both reacted to the network and changed the network."
            />
            <div style={gridTwoStyle}>
              <JsonCard title="Incoming edges" data={incomingEdges} />
              <JsonCard title="Outgoing edges" data={outgoingEdges} />
            </div>
          </section>
        </>
      ) : state.status === "ready" ? (
        <Notice tone="error">Participant not found in the prepared roster.</Notice>
      ) : null}
    </PageShell>
  );
}

function ActionCard({ action }: { action: ParticipantActionRecord & { round_id: string } }) {
  return (
    <article style={cardStyle}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start" }}>
        <div>
          <div style={{ color: "#f8fafc", fontSize: 18, fontWeight: 700 }}>{action.round_id}</div>
          <div style={{ ...mutedStyle, marginTop: 8 }}>
            {action.previous_state} {" -> "} {action.next_state}
          </div>
        </div>
        <Pill label={`${action.action_type} / ${action.polarity}`} tone="info" />
      </div>
      <div style={{ ...mutedStyle, marginTop: 12 }}>{joinList(action.reason_codes)}</div>
    </article>
  );
}

function collectParticipantActions(replay: ReplayPayload | undefined, participantId: string) {
  const actions: Array<ParticipantActionRecord & { round_id: string }> = [];
  for (const round of replay?.rounds || []) {
    for (const action of round.participant_actions || []) {
      if (action.participant_id === participantId) {
        actions.push({ ...action, round_id: round.round_id });
      }
    }
  }
  return actions;
}

function collectInfluenceEdges(
  influence: InfluenceGraphPayload | undefined,
  participantId: string,
  direction: "incoming" | "outgoing",
) {
  const edges: InfluenceEdgeRecord[] = [];
  for (const round of influence?.rounds || []) {
    for (const edge of round.edges || []) {
      if (direction === "incoming" && edge.target_participant_id === participantId) {
        edges.push(edge);
      }
      if (direction === "outgoing" && edge.source_participant_id === participantId) {
        edges.push(edge);
      }
    }
  }
  return edges;
}
