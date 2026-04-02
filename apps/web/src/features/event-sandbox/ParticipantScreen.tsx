"use client";

import { getInfluenceGraph, getParticipants, getReplay } from "./api";
import type {
  InfluenceEdgeRecord,
  InfluenceGraphPayload,
  ParticipantActionRecord,
  ParticipantRecord,
  ReplayPayload,
} from "./types";
import {
  ActionLink,
  JsonCard,
  MiniCard,
  Notice,
  PageShell,
  Pill,
  SectionHeader,
  cardStyle,
  gridThreeStyle,
  gridTwoStyle,
  joinList,
  mutedStyle,
  numberString,
  panelStyle,
  stringValue,
  useAsyncPayload,
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
      eyebrow="参与者钻取"
      title={participantId}
      description="查看某个参与者在各轮中的动作变化、它响应了哪些信号，以及它影响了哪些其他参与者。"
      actions={
        <>
          <ActionLink href={`/event-sandbox/${eventId}`} label="返回总览" />
          <ActionLink href={`/event-sandbox/${eventId}/replay`} label="查看回放" />
          <ActionLink href={`/event-sandbox/${eventId}/validation`} label="查看验证" />
        </>
      }
    >
      {state.status === "loading" ? <Notice>正在加载参与者详情...</Notice> : null}
      {state.status === "error" ? <Notice tone="error">{state.error}</Notice> : null}
      {participant ? (
        <>
          <section style={panelStyle}>
            <SectionHeader
              eyebrow="参与者画像"
              title={participant.participant_family}
              description={participant.expected_impact ?? "暂无参与者摘要。"}
            />
            <div style={gridThreeStyle}>
              <MiniCard title="立场" value={stringValue(participant.stance)} />
              <MiniCard title="权重" value={numberString(participant.authority_weight)} />
              <MiniCard title="信心" value={numberString(participant.confidence)} />
              <MiniCard title="时间维度" value={stringValue(participant.time_horizon)} />
              <MiniCard title="风险预算" value={stringValue(participant.risk_budget_profile)} />
              <MiniCard title="首发标的" value={joinList(participant.first_movers)} />
            </div>
          </section>

          <section style={{ ...panelStyle, marginTop: 20 }}>
            <SectionHeader
              eyebrow="动作轨迹"
              title="逐轮动作"
              description="这里展示的是从回放载荷中提取出的参与者动作历史。"
            />
            <div style={{ display: "grid", gap: 14 }}>
              {actionTrail.length ? (
                actionTrail.map((action, index) => <ActionCard key={`${action.round_id}-${index}`} action={action} />)
              ) : (
                <Notice>回放数据里没有找到这个参与者的动作记录。</Notice>
              )}
            </div>
          </section>

          <section style={{ ...panelStyle, marginTop: 20 }}>
            <SectionHeader
              eyebrow="影响关系"
              title="输入影响与输出影响"
              description="这些边展示了该参与者如何响应网络，又如何反过来改变网络。"
            />
            <div style={gridTwoStyle}>
              <JsonCard title="输入影响边" data={incomingEdges} />
              <JsonCard title="输出影响边" data={outgoingEdges} />
            </div>
          </section>
        </>
      ) : state.status === "ready" ? (
        <Notice tone="error">在当前已经准备好的参与者阵列中没有找到这个参与者。</Notice>
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
