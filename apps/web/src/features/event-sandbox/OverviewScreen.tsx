"use client";

import Link from "next/link";

import { getApiBaseUrl, getBelief, getEvent, getInfluenceGraph, getParticipants, getReport, getRounds, getScenarios, getSimulation } from "./api";
import type { GenericRecord, InfluenceEdgeRecord, InfluenceGraphPayload, ParticipantRecord, RoundSnapshotRecord, SimulationSummaryPayload } from "./types";
import {
  ActionLink,
  JsonCard,
  KeyRow,
  MetricPanel,
  MiniCard,
  Notice,
  PageShell,
  Pill,
  SectionHeader,
  asRecord,
  cardStyle,
  gridThreeStyle,
  gridTwoStyle,
  mutedStyle,
  numberString,
  panelStyle,
  stringValue,
  useAsyncPayload,
  joinList,
  linkStyle,
} from "./shared";

type OverviewPayload = {
  event: GenericRecord;
  participants: { participants: ParticipantRecord[]; casebook_status?: string };
  simulation: SimulationSummaryPayload;
  rounds: { rounds: RoundSnapshotRecord[]; status: string };
  influence: InfluenceGraphPayload;
  belief: GenericRecord;
  scenarios: GenericRecord;
  report: GenericRecord;
};

export function EventSandboxOverviewScreen({ eventId }: { eventId: string }) {
  const state = useAsyncPayload<OverviewPayload>(
    async () => {
      const [event, participants, simulation, rounds, influence, belief, scenarios, report] = await Promise.all([
        getEvent(eventId),
        getParticipants(eventId),
        getSimulation(eventId),
        getRounds(eventId),
        getInfluenceGraph(eventId),
        getBelief(eventId),
        getScenarios(eventId),
        getReport(eventId),
      ]);
      return { event, participants, simulation, rounds, influence, belief, scenarios, report };
    },
    [eventId],
  );

  const latestRound = state.data?.rounds.rounds?.[state.data.rounds.rounds.length - 1] ?? null;
  const latestScenario = asRecord(state.data?.scenarios.latest);
  const latestBelief = asRecord(state.data?.belief.latest);
  const latestInfluenceRound = state.data?.influence.rounds?.[state.data.influence.rounds.length - 1];
  const eventRecord = asRecord(state.data?.event.record ?? state.data?.event);
  const structure = asRecord(state.data?.event.structure);
  const mapping = asRecord(state.data?.event.mapping);

  return (
    <PageShell
      eyebrow="Roadmap 1.7 Output"
      title={`Event Sandbox Overview: ${eventId}`}
      description="This page shows the live event lane: structure, activated participants, round timeline, influence network, belief shifts, market state, and scenario result."
      actions={
        <>
          <ActionLink href="/event-sandbox" label="New event" />
          <ActionLink href={`/event-sandbox/${eventId}/replay`} label="Replay" />
          <ActionLink href={`/event-sandbox/${eventId}/validation`} label="Validation" />
          <ActionLink href={`${getApiBaseUrl()}/docs`} label="Swagger" external />
        </>
      }
    >
      {state.status === "loading" ? <Notice>Loading live event sandbox...</Notice> : null}
      {state.status === "error" ? <Notice tone="error">{state.error}</Notice> : null}
      {state.data ? (
        <>
          <section style={panelStyle}>
            <SectionHeader
              eyebrow="Event"
              title={stringValue(eventRecord.title, eventId)}
              description={stringValue(eventRecord.body, "No event body available.")}
            />
            <div style={gridThreeStyle}>
              <MiniCard title="Event type" value={stringValue(structure.event_type)} />
              <MiniCard title="Target symbols" value={joinList(mapping.symbols)} />
              <MiniCard title="Dominant scenario" value={stringValue(state.data.simulation.dominant_scenario)} />
              <MiniCard title="Latest market state" value={stringValue(state.data.simulation.latest_market_state)} />
              <MiniCard title="Round count" value={String(state.data.simulation.round_count ?? 0)} />
              <MiniCard title="Casebook status" value={stringValue(state.data.participants.casebook_status)} />
            </div>
          </section>

          <section style={{ ...panelStyle, marginTop: 20 }}>
            <SectionHeader
              eyebrow="Participants"
              title="Activated participant roster"
              description="These are the participants the system activated from the structured event and casebook."
            />
            <div style={gridTwoStyle}>
              {state.data.participants.participants.map((participant) => (
                <ParticipantCard key={participant.participant_id} eventId={eventId} participant={participant} />
              ))}
            </div>
          </section>

          <section style={{ ...panelStyle, marginTop: 20 }}>
            <SectionHeader
              eyebrow="Timeline"
              title="Round-by-round path"
              description="The timeline below is based on the live run output. Turning points and scenario changes come from the persisted simulation."
            />
            <div style={gridThreeStyle}>
              {(state.data.rounds.rounds || []).map((round) => (
                <RoundCard key={round.round_id} round={round} />
              ))}
            </div>
          </section>

          <section style={{ ...panelStyle, marginTop: 20 }}>
            <SectionHeader
              eyebrow="Current state"
              title="Belief, market state, and scenario"
              description="This is the current convergence point after the latest round."
            />
            <div style={gridThreeStyle}>
              <MetricPanel
                title="Belief"
                items={[
                  ["Consensus", numberString(latestBelief.consensus_strength)],
                  ["Opposition", numberString(latestBelief.opposition_strength)],
                  ["Divergence", numberString(latestBelief.divergence_index)],
                  ["Summary", stringValue(latestBelief.summary)],
                ]}
              />
              <MetricPanel
                title="Market state"
                items={[
                  ["State", stringValue(asRecord(latestRound?.market_state).state)],
                  ["Active", numberString(asRecord(latestRound?.market_state).active_participant_count)],
                  ["Follow-on", numberString(asRecord(latestRound?.market_state).follow_on_count)],
                  ["Exit count", numberString(asRecord(latestRound?.market_state).exit_count)],
                ]}
              />
              <MetricPanel
                title="Scenario"
                items={[
                  ["Dominant", stringValue(latestScenario.dominant_scenario)],
                  ["Bull", numberString(latestScenario.bull_confidence)],
                  ["Base", numberString(latestScenario.base_confidence)],
                  ["Bear", numberString(latestScenario.bear_confidence)],
                ]}
              />
            </div>
          </section>

          <section style={{ ...panelStyle, marginTop: 20 }}>
            <SectionHeader
              eyebrow="Influence"
              title="Latest round influence network"
              description="This is the visible propagation layer: who influenced whom, the edge type, and the strength of the link."
            />
            {latestInfluenceRound?.edges?.length ? (
              <div style={{ display: "grid", gap: 14 }}>
                {latestInfluenceRound.edges.map((edge, index) => (
                  <InfluenceCard key={`${edge.source_participant_id}-${edge.target_participant_id}-${index}`} edge={edge} />
                ))}
              </div>
            ) : (
              <Notice>No influence edges were generated for the latest round.</Notice>
            )}
          </section>

          <section style={{ ...panelStyle, marginTop: 20 }}>
            <SectionHeader
              eyebrow="Report"
              title="Current review summary"
              description="The event sandbox also keeps the report layer visible so you can see how the current run will be explained."
            />
            <div style={gridTwoStyle}>
              <JsonCard title="Report card" data={asRecord(state.data.report.report_card)} />
              <JsonCard title="Review report" data={asRecord(state.data.report.review_report)} />
            </div>
          </section>
        </>
      ) : null}
    </PageShell>
  );
}

function ParticipantCard({ eventId, participant }: { eventId: string; participant: ParticipantRecord }) {
  return (
    <article style={cardStyle}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start" }}>
        <div>
          <div style={{ color: "#f8fafc", fontSize: 18, fontWeight: 700 }}>{participant.participant_family}</div>
          <div style={{ ...mutedStyle, marginTop: 8 }}>{participant.expected_impact ?? "-"}</div>
        </div>
        <Link href={`/event-sandbox/${eventId}/participants/${encodeURIComponent(participant.participant_id)}`} style={linkStyle}>
          Drill down
        </Link>
      </div>
      <div style={{ display: "grid", gap: 10, marginTop: 16 }}>
        <KeyRow label="Participant" value={participant.participant_id} />
        <KeyRow label="Stance" value={stringValue(participant.stance)} />
        <KeyRow label="Authority" value={numberString(participant.authority_weight)} />
        <KeyRow label="Confidence" value={numberString(participant.confidence)} />
        <KeyRow label="Triggers" value={joinList(participant.trigger_conditions)} />
      </div>
    </article>
  );
}

function RoundCard({ round }: { round: RoundSnapshotRecord }) {
  const belief = asRecord(round.belief_snapshot);
  const market = asRecord(round.market_state);
  const scenario = asRecord(round.scenario_snapshot);
  return (
    <article style={cardStyle}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start" }}>
        <div>
          <div style={{ color: "#f8fafc", fontSize: 18, fontWeight: 700 }}>{round.round_id}</div>
          <div style={{ ...mutedStyle, marginTop: 8 }}>{round.focus}</div>
        </div>
        {round.turning_point ? <Pill label="Turning point" tone="warning" /> : <Pill label={`Round ${round.order}`} />}
      </div>
      <div style={{ ...mutedStyle, marginTop: 10 }}>{round.objective}</div>
      <div style={{ display: "grid", gap: 10, marginTop: 16 }}>
        <KeyRow label="Market state" value={stringValue(market.state)} />
        <KeyRow label="Dominant scenario" value={stringValue(scenario.dominant_scenario)} />
        <KeyRow label="Consensus" value={numberString(belief.consensus_strength)} />
        <KeyRow label="Action count" value={String(round.participant_actions.length)} />
      </div>
    </article>
  );
}

function InfluenceCard({ edge }: { edge: InfluenceEdgeRecord }) {
  return (
    <article style={cardStyle}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
        <div>
          <div style={{ color: "#f8fafc", fontSize: 18, fontWeight: 700 }}>
            {edge.source_participant_family} {" -> "} {edge.target_participant_family}
          </div>
          <div style={{ ...mutedStyle, marginTop: 8 }}>{edge.reason}</div>
        </div>
        <Pill label={`${edge.influence_type} / ${edge.polarity}`} tone="info" />
      </div>
      <div style={{ display: "grid", gap: 10, marginTop: 16 }}>
        <KeyRow label="Round" value={edge.round_id} />
        <KeyRow label="Strength" value={numberString(edge.strength)} />
        <KeyRow label="Source" value={edge.source_participant_id} />
        <KeyRow label="Target" value={edge.target_participant_id} />
      </div>
    </article>
  );
}
