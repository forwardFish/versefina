"use client";

import { useEffect, useState } from "react";

import { getApiBaseUrl, getReplay } from "./api";
import {
  ActionLink,
  JsonCard,
  Notice,
  PageShell,
  SectionHeader,
  mutedStyle,
  panelStyle,
  pillButtonStyle,
  useAsyncPayload,
} from "./shared";
import type { ReplayPayload } from "./types";

export function EventSandboxReplayScreen({ eventId }: { eventId: string }) {
  const state = useAsyncPayload<ReplayPayload>(() => getReplay(eventId), [eventId]);
  const [selectedRound, setSelectedRound] = useState("");

  useEffect(() => {
    if (state.data?.rounds?.length && !selectedRound) {
      setSelectedRound(state.data.rounds[0].round_id);
    }
  }, [selectedRound, state.data]);

  const activeRound =
    state.data?.rounds?.find((round) => round.round_id === selectedRound) ?? state.data?.rounds?.[0] ?? null;

  return (
    <PageShell
      eyebrow="Roadmap 1.7 Replay"
      title={`Replay: ${eventId}`}
      description="Use this page to replay the event path round by round and inspect the action ledger behind the final result."
      actions={
        <>
          <ActionLink href={`/event-sandbox/${eventId}`} label="Overview" />
          <ActionLink href={`/event-sandbox/${eventId}/validation`} label="Validation" />
          <ActionLink href={`${getApiBaseUrl()}/docs`} label="Swagger" external />
        </>
      }
    >
      {state.status === "loading" ? <Notice>Loading replay...</Notice> : null}
      {state.status === "error" ? <Notice tone="error">{state.error}</Notice> : null}
      {state.data ? (
        <>
          <section style={panelStyle}>
            <SectionHeader
              eyebrow="Replay"
              title={`Dominant scenario: ${state.data.dominant_scenario ?? "-"}`}
              description="Switch rounds to see how participant actions, states, and influence changed over time."
            />
            <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
              {(state.data.rounds || []).map((round) => (
                <button
                  key={round.round_id}
                  type="button"
                  onClick={() => setSelectedRound(round.round_id)}
                  style={{
                    ...pillButtonStyle,
                    background:
                      selectedRound === round.round_id ? "rgba(14, 165, 233, 0.18)" : "rgba(15, 23, 42, 0.88)",
                  }}
                >
                  {round.round_id}
                </button>
              ))}
            </div>
            <div style={{ ...mutedStyle, marginTop: 16 }}>
              turning points: {Array.isArray(state.data.timeline?.turning_points) ? state.data.timeline?.turning_points?.join(", ") : "-"}
            </div>
          </section>
          {activeRound ? (
            <section style={{ ...panelStyle, marginTop: 20 }}>
              <SectionHeader
                eyebrow="Active round"
                title={`${activeRound.round_id} - ${activeRound.focus}`}
                description={activeRound.objective}
              />
              <div style={{ display: "grid", gap: 18, gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))" }}>
                <JsonCard title="Participant actions" data={activeRound.participant_actions} />
                <JsonCard title="Participant states" data={activeRound.participant_states} />
                <JsonCard title="Belief snapshot" data={activeRound.belief_snapshot} />
                <JsonCard title="Scenario snapshot" data={activeRound.scenario_snapshot} />
              </div>
            </section>
          ) : null}
        </>
      ) : null}
    </PageShell>
  );
}
