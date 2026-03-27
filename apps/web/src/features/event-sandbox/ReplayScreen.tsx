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
      eyebrow="事件回放"
      title={`事件回放：${eventId}`}
      description="这一页按轮次回放事件演化过程，让你看到最终结论背后的动作流水。"
      actions={
        <>
          <ActionLink href={`/event-sandbox/${eventId}`} label="返回总览" />
          <ActionLink href={`/event-sandbox/${eventId}/validation`} label="查看验证" />
          <ActionLink href={`${getApiBaseUrl()}/docs`} label="打开 Swagger" external />
        </>
      }
    >
      {state.status === "loading" ? <Notice>正在加载回放...</Notice> : null}
      {state.status === "error" ? <Notice tone="error">{state.error}</Notice> : null}
      {state.data ? (
        <>
          <section style={panelStyle}>
            <SectionHeader
              eyebrow="回放"
              title={`当前主导剧本：${state.data.dominant_scenario ?? "-"}`}
              description="切换不同轮次，查看参与者动作、状态和影响网络如何随着时间变化。"
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
              关键转折：{Array.isArray(state.data.timeline?.turning_points) ? state.data.timeline?.turning_points?.join("、") : "-"}
            </div>
          </section>
          {activeRound ? (
            <section style={{ ...panelStyle, marginTop: 20 }}>
              <SectionHeader
                eyebrow="当前轮次"
                title={`${activeRound.round_id} · ${activeRound.focus}`}
                description={activeRound.objective}
              />
              <div style={{ display: "grid", gap: 18, gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))" }}>
                <JsonCard title="参与者动作" data={activeRound.participant_actions} />
                <JsonCard title="参与者状态" data={activeRound.participant_states} />
                <JsonCard title="信念快照" data={activeRound.belief_snapshot} />
                <JsonCard title="剧本快照" data={activeRound.scenario_snapshot} />
              </div>
            </section>
          ) : null}
        </>
      ) : null}
    </PageShell>
  );
}
