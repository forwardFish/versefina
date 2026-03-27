"use client";

import Link from "next/link";

import {
  getApiBaseUrl,
  getBelief,
  getEvent,
  getInfluenceGraph,
  getLineage,
  getParticipants,
  getReport,
  getRounds,
  getScenarios,
  getSimulation,
} from "./api";
import type {
  EventLineagePayload,
  GenericRecord,
  InfluenceEdgeRecord,
  InfluenceGraphPayload,
  ParticipantRecord,
  RoundSnapshotRecord,
  SimulationSummaryPayload,
} from "./types";
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
  joinList,
  linkStyle,
  mutedStyle,
  numberString,
  panelStyle,
  stringValue,
  useAsyncPayload,
} from "./shared";

type OverviewPayload = {
  event: GenericRecord;
  lineage: EventLineagePayload;
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
      const [event, lineage, participants, simulation, rounds, influence, belief, scenarios, report] = await Promise.all([
        getEvent(eventId),
        getLineage(eventId),
        getParticipants(eventId),
        getSimulation(eventId),
        getRounds(eventId),
        getInfluenceGraph(eventId),
        getBelief(eventId),
        getScenarios(eventId),
        getReport(eventId),
      ]);
      return { event, lineage, participants, simulation, rounds, influence, belief, scenarios, report };
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
  const lineage = state.data?.lineage;
  const orchestrationRows = buildOrchestrationRows(
    state.data?.participants.participants ?? [],
    state.data?.rounds.rounds ?? [],
    state.data?.influence.rounds ?? [],
  );
  const roleCounts = summarizeRoles(orchestrationRows);

  return (
    <PageShell
      eyebrow="Roadmap 1.7 结果"
      title={`事件沙盘总览：${eventId}`}
      description="这里展示真实事件链路：事件结构、参与者激活、轮次时间线、影响网络、信念变化、市场状态和剧本结论。"
      actions={
        <>
          <ActionLink href="/event-sandbox" label="新建事件" />
          <ActionLink href={`/event-sandbox/${eventId}/replay`} label="查看回放" />
          <ActionLink href={`/event-sandbox/${eventId}/validation`} label="查看验证" />
          <ActionLink href={`${getApiBaseUrl()}/docs`} label="打开 Swagger" external />
        </>
      }
    >
      {state.status === "loading" ? <Notice>正在加载真实事件沙盘...</Notice> : null}
      {state.status === "error" ? <Notice tone="error">{state.error}</Notice> : null}
      {state.data ? (
        <>
          <section style={panelStyle}>
            <SectionHeader
              eyebrow="事件"
              title={stringValue(eventRecord.title, eventId)}
              description={stringValue(eventRecord.body, "暂无事件正文。")}
            />
            <div style={gridThreeStyle}>
              <MiniCard title="事件类型" value={stringValue(structure.event_type)} />
              <MiniCard title="目标标的" value={joinList(mapping.symbols)} />
              <MiniCard title="当前主导剧本" value={stringValue(state.data.simulation.dominant_scenario)} />
              <MiniCard title="最新市场状态" value={stringValue(state.data.simulation.latest_market_state)} />
              <MiniCard title="轮次数量" value={String(state.data.simulation.round_count ?? 0)} />
              <MiniCard title="案例基座状态" value={stringValue(state.data.participants.casebook_status)} />
            </div>
            {lineage?.status === "ready" ? (
              <>
                <div style={{ ...gridThreeStyle, marginTop: 18 }}>
                  <MiniCard title="真实来源 Run" value={stringValue(lineage.finahunt_run_id)} />
                  <MiniCard title="来源主题" value={stringValue(lineage.primary_theme)} />
                  <MiniCard title="来源消息 ID" value={stringValue(lineage.source_event_id)} />
                  <MiniCard title="来源介质" value={stringValue(lineage.source_name)} />
                  <MiniCard title="来源优先级" value={stringValue(lineage.source_priority)} />
                  <MiniCard title="来源工件" value={stringValue(lineage.source_artifact)} />
                </div>
                <div style={{ ...gridTwoStyle, marginTop: 18 }}>
                  <MetricPanel
                    title="来源链路"
                    items={[
                      ["Finahunt Run", stringValue(lineage.finahunt_run_id)],
                      ["Trace", stringValue(lineage.finahunt_trace_id)],
                      ["标题", stringValue(lineage.source_title)],
                      ["消息 ID", stringValue(lineage.source_event_id)],
                    ]}
                  />
                  <MetricPanel
                    title="排序上下文"
                    items={[
                      ["排序位次", stringValue(asRecord(lineage.ranking_context).rank_position)],
                      ["相关性得分", numberString(asRecord(lineage.ranking_context).relevance_score)],
                      ["主题", stringValue(asRecord(lineage.ranking_context).theme_name)],
                      ["发酵阶段", stringValue(asRecord(lineage.ranking_context).fermentation_phase)],
                    ]}
                  />
                </div>
              </>
            ) : null}
          </section>

          <section style={{ ...panelStyle, marginTop: 20 }}>
            <SectionHeader
              eyebrow="参与者"
              title="已激活的参与者阵列"
              description="这些是系统根据事件结构化结果和案例基座激活出来的参与者。"
            />
            <div style={gridTwoStyle}>
              {state.data.participants.participants.map((participant) => (
                <ParticipantCard key={participant.participant_id} eventId={eventId} participant={participant} />
              ))}
            </div>
          </section>

          <section style={{ ...panelStyle, marginTop: 20 }}>
            <SectionHeader
              eyebrow="Agent 编排"
              title={`这次事件一共激活了 ${orchestrationRows.length} 个金融 Agent`}
              description="这里直接展示每个金融 Agent 在这次事件里扮演的角色、逐轮动作、最终状态，以及它如何推动事件发酵。"
            />
            <div style={gridThreeStyle}>
              <MiniCard title="首发带动者" value={String(roleCounts.first_move)} />
              <MiniCard title="跟随确认者" value={String(roleCounts.follow_on)} />
              <MiniCard title="风险观察者" value={String(roleCounts.risk_watch)} />
              <MiniCard title="最终市场状态" value={stringValue(state.data.simulation.latest_market_state)} />
              <MiniCard title="关键转折轮次" value={joinList(state.data.simulation.timeline?.turning_points)} />
              <MiniCard title="当前主导剧本" value={stringValue(latestScenario.dominant_scenario ?? state.data.simulation.dominant_scenario)} />
            </div>
            <div style={{ display: "grid", gap: 14, marginTop: 18 }}>
              {orchestrationRows.map((row) => (
                <AgentOrchestrationCard key={row.participant_id} eventId={eventId} row={row} />
              ))}
            </div>
          </section>

          <section style={{ ...panelStyle, marginTop: 20 }}>
            <SectionHeader
              eyebrow="时间线"
              title="逐轮演化路径"
              description="下面的时间线来自真实推演输出。转折点和剧本变化都来自持久化的 simulation 结果。"
            />
            <div style={gridThreeStyle}>
              {(state.data.rounds.rounds || []).map((round) => (
                <RoundCard key={round.round_id} round={round} />
              ))}
            </div>
          </section>

          <section style={{ ...panelStyle, marginTop: 20 }}>
            <SectionHeader
              eyebrow="当前状态"
              title="信念、市场状态与剧本"
              description="这是最近一轮之后的当前收敛点。"
            />
            <div style={gridThreeStyle}>
              <MetricPanel
                title="信念"
                items={[
                  ["共识强度", numberString(latestBelief.consensus_strength)],
                  ["对立强度", numberString(latestBelief.opposition_strength)],
                  ["分歧指数", numberString(latestBelief.divergence_index)],
                  ["摘要", stringValue(latestBelief.summary)],
                ]}
              />
              <MetricPanel
                title="市场状态"
                items={[
                  ["状态", stringValue(asRecord(latestRound?.market_state).state)],
                  ["活跃参与者", numberString(asRecord(latestRound?.market_state).active_participant_count)],
                  ["跟随数量", numberString(asRecord(latestRound?.market_state).follow_on_count)],
                  ["退出数量", numberString(asRecord(latestRound?.market_state).exit_count)],
                ]}
              />
              <MetricPanel
                title="剧本"
                items={[
                  ["主导剧本", stringValue(latestScenario.dominant_scenario)],
                  ["Bull", numberString(latestScenario.bull_confidence)],
                  ["Base", numberString(latestScenario.base_confidence)],
                  ["Bear", numberString(latestScenario.bear_confidence)],
                ]}
              />
            </div>
          </section>

          <section style={{ ...panelStyle, marginTop: 20 }}>
            <SectionHeader
              eyebrow="影响传播"
              title="最新一轮影响网络"
              description="这是可视化传播层：谁影响了谁、边的类型是什么、影响强度有多大。"
            />
            {latestInfluenceRound?.edges?.length ? (
              <div style={{ display: "grid", gap: 14 }}>
                {latestInfluenceRound.edges.map((edge, index) => (
                  <InfluenceCard key={`${edge.source_participant_id}-${edge.target_participant_id}-${index}`} edge={edge} />
                ))}
              </div>
            ) : (
              <Notice>最新一轮没有生成影响传播边。</Notice>
            )}
          </section>

          <section style={{ ...panelStyle, marginTop: 20 }}>
            <SectionHeader
              eyebrow="报告"
              title="当前复盘摘要"
              description="事件沙盘会把报告层一起展示出来，让你看到这次推演会如何被解释。"
            />
            <div style={gridTwoStyle}>
              <JsonCard title="报告卡片" data={asRecord(state.data.report.report_card)} />
              <JsonCard title="复盘报告" data={asRecord(state.data.report.review_report)} />
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
          查看详情
        </Link>
      </div>
      <div style={{ display: "grid", gap: 10, marginTop: 16 }}>
        <KeyRow label="参与者" value={participant.participant_id} />
        <KeyRow label="立场" value={stringValue(participant.stance)} />
        <KeyRow label="权重" value={numberString(participant.authority_weight)} />
        <KeyRow label="信心" value={numberString(participant.confidence)} />
        <KeyRow label="触发条件" value={joinList(participant.trigger_conditions)} />
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
        {round.turning_point ? <Pill label="转折点" tone="warning" /> : <Pill label={`第 ${round.order} 轮`} />}
      </div>
      <div style={{ ...mutedStyle, marginTop: 10 }}>{round.objective}</div>
      <div style={{ display: "grid", gap: 10, marginTop: 16 }}>
        <KeyRow label="市场状态" value={stringValue(market.state)} />
        <KeyRow label="主导剧本" value={stringValue(scenario.dominant_scenario)} />
        <KeyRow label="共识强度" value={numberString(belief.consensus_strength)} />
        <KeyRow label="动作数量" value={String(round.participant_actions.length)} />
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
        <KeyRow label="轮次" value={edge.round_id} />
        <KeyRow label="强度" value={numberString(edge.strength)} />
        <KeyRow label="来源" value={edge.source_participant_id} />
        <KeyRow label="目标" value={edge.target_participant_id} />
      </div>
    </article>
  );
}

type AgentOrchestrationRow = {
  participant_id: string;
  participant_family: string;
  stance: string;
  role: string;
  initial_state: string;
  final_state: string;
  round_actions: Array<{ round_id: string; action_type: string; next_state: string }>;
  incoming_count: number;
  outgoing_count: number;
  allowed_actions: string[];
};

function AgentOrchestrationCard({
  eventId,
  row,
}: {
  eventId: string;
  row: AgentOrchestrationRow;
}) {
  return (
    <article style={cardStyle}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start" }}>
        <div>
          <div style={{ color: "#f8fafc", fontSize: 18, fontWeight: 700 }}>{row.participant_family}</div>
          <div style={{ ...mutedStyle, marginTop: 8 }}>
            角色：{row.role} / 立场：{row.stance}
          </div>
        </div>
        <Link href={`/event-sandbox/${eventId}/participants/${encodeURIComponent(row.participant_id)}`} style={linkStyle}>
          查看详情
        </Link>
      </div>
      <div style={{ display: "grid", gap: 10, marginTop: 16 }}>
        <KeyRow label="Agent ID" value={row.participant_id} />
        <KeyRow label="初始状态" value={row.initial_state} />
        <KeyRow label="最终状态" value={row.final_state} />
        <KeyRow label="输入影响数" value={String(row.incoming_count)} />
        <KeyRow label="输出影响数" value={String(row.outgoing_count)} />
        <KeyRow label="允许动作" value={joinList(row.allowed_actions)} />
      </div>
      <div style={{ display: "grid", gap: 8, marginTop: 16 }}>
        {row.round_actions.map((action) => (
          <div
            key={`${row.participant_id}-${action.round_id}`}
            style={{
              borderTop: "1px solid rgba(148, 163, 184, 0.12)",
              paddingTop: 10,
              display: "flex",
              justifyContent: "space-between",
              gap: 12,
            }}
          >
            <div style={{ color: "#94a3b8", fontSize: 13 }}>{action.round_id}</div>
            <div style={{ color: "#f8fafc", textAlign: "right" }}>
              {action.action_type} {" -> "} {action.next_state}
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}

function buildOrchestrationRows(
  participants: ParticipantRecord[],
  rounds: RoundSnapshotRecord[],
  influenceRounds: InfluenceGraphPayload["rounds"],
): AgentOrchestrationRow[] {
  const firstRound = rounds[0];
  const latestRound = rounds[rounds.length - 1];
  const rows = participants.map((participant) => {
    const initialStateRecord =
      firstRound?.participant_states
        ?.map((item) => asRecord(item))
        .find((item) => stringValue(item.participant_id) === participant.participant_id) ?? {};
    const finalStateRecord =
      latestRound?.participant_states
        ?.map((item) => asRecord(item))
        .find((item) => stringValue(item.participant_id) === participant.participant_id) ?? {};
    const roundActions = rounds
      .map((round) => {
        const action = round.participant_actions.find((item) => item.participant_id === participant.participant_id);
        if (!action) {
          return null;
        }
        return {
          round_id: round.round_id,
          action_type: action.action_type,
          next_state: action.next_state,
        };
      })
      .filter(Boolean) as Array<{ round_id: string; action_type: string; next_state: string }>;
    const incomingCount = influenceRounds.reduce(
      (count, round) => count + round.edges.filter((edge) => edge.target_participant_id === participant.participant_id).length,
      0,
    );
    const outgoingCount = influenceRounds.reduce(
      (count, round) => count + round.edges.filter((edge) => edge.source_participant_id === participant.participant_id).length,
      0,
    );
    return {
      participant_id: participant.participant_id,
      participant_family: participant.participant_family,
      stance: stringValue(participant.stance),
      role: stringValue(finalStateRecord.role ?? initialStateRecord.role, "watch"),
      initial_state: stringValue(participant.initial_state ?? initialStateRecord.state, "ready"),
      final_state: stringValue(finalStateRecord.state, "unknown"),
      round_actions: roundActions,
      incoming_count: incomingCount,
      outgoing_count: outgoingCount,
      allowed_actions: participant.allowed_actions ?? [],
    };
  });
  return rows.sort((left, right) => right.outgoing_count - left.outgoing_count || right.incoming_count - left.incoming_count);
}

function summarizeRoles(rows: AgentOrchestrationRow[]) {
  return rows.reduce(
    (summary, row) => {
      if (row.role === "first_move") {
        summary.first_move += 1;
      } else if (row.role === "follow_on") {
        summary.follow_on += 1;
      } else {
        summary.risk_watch += 1;
      }
      return summary;
    },
    { first_move: 0, follow_on: 0, risk_watch: 0 },
  );
}
