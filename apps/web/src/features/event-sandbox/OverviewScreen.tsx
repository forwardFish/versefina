"use client";

import React from "react";
import Link from "next/link";
import { useState, type CSSProperties } from "react";

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
  pillButtonStyle,
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

const wallGridStyle: CSSProperties = {
  display: "grid",
  gap: 20,
  gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
  alignItems: "start",
};

const stageGridStyle: CSSProperties = {
  display: "grid",
  gap: 16,
  gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
};

const buttonRowStyle: CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: 10,
};

const accentButtonStyle: CSSProperties = {
  ...pillButtonStyle,
  background: "rgba(14, 165, 233, 0.16)",
};

const mutedButtonStyle: CSSProperties = {
  ...pillButtonStyle,
  background: "rgba(15, 23, 42, 0.82)",
};

const timelineCardStyle: CSSProperties = {
  ...cardStyle,
  display: "grid",
  gap: 14,
};

const executionWindows = [
  "pre_open",
  "open_5m",
  "morning_30m",
  "midday_reprice",
  "afternoon_follow",
  "close_positioning",
];

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

  const [selectedRoundId, setSelectedRoundId] = useState<string | null>(null);
  const [selectedParticipantId, setSelectedParticipantId] = useState<string | null>(null);
  const [selectedEdgeKey, setSelectedEdgeKey] = useState<string | null>(null);
  const [selectedScenarioKey, setSelectedScenarioKey] = useState<string | null>(null);

  const rounds = state.data?.rounds.rounds ?? [];
  const latestRound = rounds[rounds.length - 1] ?? null;
  const activeRound =
    rounds.find((round) => round.round_id === selectedRoundId) ??
    latestRound;
  const latestScenario = asRecord(state.data?.scenarios.latest);
  const latestBelief = asRecord(state.data?.belief.latest);
  const activeBelief = asRecord(activeRound?.belief_snapshot ?? latestBelief);
  const activeScenario = asRecord(activeRound?.scenario_snapshot ?? latestScenario);
  const activeMarket = asRecord(activeRound?.market_state);
  const eventRecord = asRecord(state.data?.event.record ?? state.data?.event);
  const structure = asRecord(state.data?.event.structure);
  const mapping = asRecord(state.data?.event.mapping);
  const reportCard = asRecord(asRecord(state.data?.report).report_card);
  const reviewReport = asRecord(asRecord(state.data?.report).review_report);
  const lineage = state.data?.lineage;
  const orchestrationRows = buildOrchestrationRows(
    state.data?.participants.participants ?? [],
    rounds,
    state.data?.influence.rounds ?? [],
  );
  const activeParticipant =
    orchestrationRows.find((row) => row.participant_id === selectedParticipantId) ??
    orchestrationRows[0] ??
    null;
  const activeInfluenceRound = resolveInfluenceRound(state.data?.influence.rounds ?? [], activeRound?.round_id);
  const activeEdges = activeInfluenceRound?.edges ?? [];
  const activeEdge =
    activeEdges.find((edge, index) => buildEdgeKey(edge, index) === selectedEdgeKey) ??
    activeEdges[0] ??
    null;
  const roleCounts = summarizeRoles(orchestrationRows);
  const selectedScenarioName = selectedScenarioKey ?? stringValue(activeScenario.dominant_scenario, "base");

  return (
    <PageShell
      eyebrow="Roadmap 1.8 图谱墙"
      title={`单事件演化墙：${stringValue(eventRecord.title, eventId)}`}
      description="这不是普通信息页。这里把事件图谱、参与者编排、影响传播、信念剧本和市场状态放进同一张演化墙，让你一眼看见市场是怎么动起来的。"
      actions={
        <>
          <ActionLink href="/event-sandbox" label="导入新事件" />
          <ActionLink href={`/event-sandbox/${eventId}/replay`} label="打开回放" />
          <ActionLink href={`/event-sandbox/${eventId}/validation`} label="打开验证" />
          <ActionLink href={`${getApiBaseUrl()}/docs`} label="Swagger" external />
        </>
      }
    >
      {state.status === "loading" ? <Notice>正在加载单事件演化墙...</Notice> : null}
      {state.status === "error" ? <Notice tone="error">{state.error}</Notice> : null}
      {state.data ? (
        <>
          <section style={wallGridStyle}>
            <article style={panelStyle}>
              <SectionHeader
                eyebrow="左侧"
                title="事件图谱与来源链"
                description="先看事件本身：消息是什么、冲击链怎么走、确认与失效条件是什么、它来自哪个真实来源。"
              />
              <div style={gridThreeStyle}>
                <MiniCard title="事件类型" value={stringValue(structure.event_type)} />
                <MiniCard title="核心商品" value={joinList(structure.commodities)} />
                <MiniCard title="板块与标的" value={joinList(mapping.symbols)} />
                <MiniCard title="来源主题" value={stringValue(lineage?.primary_theme)} />
                <MiniCard title="案例基座" value={stringValue(state.data.participants.casebook_status)} />
                <MiniCard title="当前主导剧本" value={stringValue(state.data.simulation.dominant_scenario)} />
              </div>
              <div style={{ ...gridTwoStyle, marginTop: 18 }}>
                <MetricPanel
                  title="事件图谱"
                  items={[
                    ["事件标题", stringValue(eventRecord.title, eventId)],
                    ["传导链", joinList(structure.causal_chain ?? mapping.causal_chain)],
                    ["确认信号", joinList(structure.confirmation_signals)],
                    ["失效条件", joinList(structure.invalidation_conditions)],
                  ]}
                />
                <MetricPanel
                  title="来源链与排序上下文"
                  items={[
                    ["Finahunt Run", stringValue(lineage?.finahunt_run_id)],
                    ["来源消息 ID", stringValue(lineage?.source_event_id)],
                    ["来源介质", stringValue(lineage?.source_name)],
                    ["排序位次", stringValue(asRecord(lineage?.ranking_context).rank_position)],
                  ]}
                />
              </div>
              <div style={{ ...gridTwoStyle, marginTop: 18 }}>
                <NarrativeCard
                  title="这条真实事件是什么"
                  body={stringValue(eventRecord.body, "暂无事件正文。")}
                />
                <NarrativeCard
                  title="为什么值得看"
                  body={stringValue(reportCard.summary ?? reviewReport.summary, "系统会根据真实来源、事件结构和演化轨迹，判断这条消息如何可能沿着产业链与参与者网络扩散。")}
                />
              </div>
            </article>

            <article style={panelStyle}>
              <SectionHeader
                eyebrow="中央"
                title="Population / Interaction / Influence"
                description="这块是主画布：当前窗口里谁被触发、谁 lead、谁 follow、谁 reduce、谁 exit，以及谁正在影响谁。"
              />
              <div style={gridThreeStyle}>
                <MiniCard title="激活 Agent 数" value={String(orchestrationRows.length)} />
                <MiniCard title="首发带动者" value={String(roleCounts.first_move)} />
                <MiniCard title="跟随确认者" value={String(roleCounts.follow_on)} />
                <MiniCard title="风险观察者" value={String(roleCounts.risk_watch)} />
                <MiniCard title="当前执行窗口" value={windowLabelForRound(activeRound)} />
                <MiniCard title="当前轮次" value={stringValue(activeRound?.round_id)} />
              </div>
              <div style={{ ...gridTwoStyle, marginTop: 18 }}>
                <MetricPanel
                  title="当前主导参与者"
                  items={[
                    ["Dominant Family", activeParticipant?.participant_family ?? "-"],
                    ["当前角色", activeParticipant?.role ?? "-"],
                    ["最终状态", activeParticipant?.final_state ?? "-"],
                    ["输出影响数", String(activeParticipant?.outgoing_count ?? 0)],
                  ]}
                />
                <MetricPanel
                  title="当前传播链"
                  items={[
                    ["最新边数量", String(activeEdges.length)],
                    ["影响类型", stringValue(activeEdge?.influence_type)],
                    ["影响强度", numberString(activeEdge?.strength)],
                    ["影响原因", stringValue(activeEdge?.reason)],
                  ]}
                />
              </div>
              <div style={{ ...stageGridStyle, marginTop: 18 }}>
                {orchestrationRows.map((row) => (
                  <button
                    key={row.participant_id}
                    type="button"
                    onClick={() => setSelectedParticipantId(row.participant_id)}
                    style={row.participant_id === activeParticipant?.participant_id ? accentButtonStyle : mutedButtonStyle}
                  >
                    {row.participant_family} / {row.role} / {row.final_state}
                  </button>
                ))}
              </div>
              <div style={{ ...buttonRowStyle, marginTop: 18 }}>
                {activeEdges.map((edge, index) => {
                  const edgeKey = buildEdgeKey(edge, index);
                  const selected = edgeKey === selectedEdgeKey || (!selectedEdgeKey && index === 0);
                  return (
                    <button
                      key={edgeKey}
                      type="button"
                      onClick={() => setSelectedEdgeKey(edgeKey)}
                      style={selected ? accentButtonStyle : mutedButtonStyle}
                    >
                      {edge.source_participant_family} {" -> "} {edge.target_participant_family}
                    </button>
                  );
                })}
              </div>
              <div style={{ ...gridTwoStyle, marginTop: 18 }}>
                <AgentDrilldownCard eventId={eventId} row={activeParticipant} />
                <EdgeDrilldownCard edge={activeEdge} />
              </div>
            </article>

            <article style={panelStyle}>
              <SectionHeader
                eyebrow="右侧"
                title="Belief / Scenario / Market State"
                description="这里展示信念、剧本和市场状态是如何一起变化的，以及为什么当前 dominant scenario 站在前面。"
              />
              <div style={gridThreeStyle}>
                <MiniCard title="市场状态" value={stringValue(activeMarket.state)} />
                <MiniCard title="共识强度" value={numberString(activeBelief.consensus_strength)} />
                <MiniCard title="分歧宽度" value={numberString(activeBelief.divergence_index ?? activeBelief.dissent_width)} />
                <MiniCard title="拥挤度" value={numberString(activeMarket.crowding_score)} />
                <MiniCard title="脆弱度" value={numberString(activeMarket.falsification_fragility)} />
                <MiniCard title="Dominant Scenario" value={selectedScenarioName} />
              </div>
              <div style={{ ...buttonRowStyle, marginTop: 18 }}>
                {["bull", "base", "bear"].map((scenarioKey) => (
                  <button
                    key={scenarioKey}
                    type="button"
                    onClick={() => setSelectedScenarioKey(scenarioKey)}
                    style={scenarioKey === selectedScenarioName ? accentButtonStyle : mutedButtonStyle}
                  >
                    {scenarioKey.toUpperCase()}
                  </button>
                ))}
              </div>
              <div style={{ ...gridTwoStyle, marginTop: 18 }}>
                <MetricPanel
                  title="剧本状态"
                  items={[
                    ["Bull", numberString(activeScenario.bull_confidence)],
                    ["Base", numberString(activeScenario.base_confidence)],
                    ["Bear", numberString(activeScenario.bear_confidence)],
                    ["Watchpoints", joinList(activeScenario.watchpoints)],
                  ]}
                />
                <MetricPanel
                  title="状态迁移原因"
                  items={[
                    ["当前状态", stringValue(activeMarket.state)],
                    ["活跃参与者", numberString(activeMarket.active_participant_count)],
                    ["跟随数量", numberString(activeMarket.follow_on_count)],
                    ["退出数量", numberString(activeMarket.exit_count)],
                  ]}
                />
              </div>
              <div style={{ ...gridTwoStyle, marginTop: 18 }}>
                <NarrativeCard
                  title="支持链"
                  body={joinNarrative(activeScenario.support_chain, reviewReport.support_chain, reviewReport.key_support_chain)}
                />
                <NarrativeCard
                  title="反对链与脆弱点"
                  body={joinNarrative(activeScenario.opposition_chain, reviewReport.opposition_chain, reviewReport.key_opposition_chain, activeScenario.invalidation_conditions)}
                />
              </div>
            </article>
          </section>

          <section style={panelStyle}>
            <SectionHeader
              eyebrow="底部"
              title="Replay Timeline + 窗口切换"
              description="底部时间轴是单事件演化墙的总控台。切换任何窗口，你都能看到当时谁动了、怎么动、影响了谁、市场状态变成了什么。"
            />
            <div style={buttonRowStyle}>
              {rounds.map((round) => (
                <button
                  key={round.round_id}
                  type="button"
                  onClick={() => setSelectedRoundId(round.round_id)}
                  style={round.round_id === activeRound?.round_id ? accentButtonStyle : mutedButtonStyle}
                >
                  {windowLabelForRound(round)} / {round.round_id}
                </button>
              ))}
            </div>
            <div style={{ ...gridThreeStyle, marginTop: 18 }}>
              {rounds.map((round) => (
                <RoundSummaryCard
                  key={round.round_id}
                  round={round}
                  selected={round.round_id === activeRound?.round_id}
                  onSelect={() => setSelectedRoundId(round.round_id)}
                />
              ))}
            </div>
            {activeRound ? (
              <div style={{ ...gridTwoStyle, marginTop: 18 }}>
                <MetricPanel
                  title="当前窗口细节"
                  items={[
                    ["执行窗口", windowLabelForRound(activeRound)],
                    ["焦点", stringValue(activeRound.focus)],
                    ["目标", stringValue(activeRound.objective)],
                    ["动作数", String(activeRound.participant_actions.length)],
                  ]}
                />
                <MetricPanel
                  title="本轮市场变化"
                  items={[
                    ["Market State", stringValue(asRecord(activeRound.market_state).state)],
                    ["Dominant Scenario", stringValue(asRecord(activeRound.scenario_snapshot).dominant_scenario)],
                    ["共识强度", numberString(asRecord(activeRound.belief_snapshot).consensus_strength)],
                    ["转折点", activeRound.turning_point ? "是" : "否"],
                  ]}
                />
              </div>
            ) : (
              <Notice>当前没有可用的轮次数据。</Notice>
            )}
          </section>
        </>
      ) : null}
    </PageShell>
  );
}

function RoundSummaryCard({
  round,
  selected,
  onSelect,
}: {
  round: RoundSnapshotRecord;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button type="button" onClick={onSelect} style={{ ...timelineCardStyle, ...(selected ? accentButtonStyle : {}) }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start" }}>
        <div>
          <div style={{ color: "#f8fafc", fontSize: 18, fontWeight: 700 }}>{windowLabelForRound(round)}</div>
          <div style={{ ...mutedStyle, marginTop: 8 }}>{round.round_id}</div>
        </div>
        {round.turning_point ? <Pill label="转折点" tone="warning" /> : <Pill label={`第 ${round.order} 轮`} />}
      </div>
      <div style={{ ...mutedStyle, textAlign: "left" }}>{stringValue(round.focus)}</div>
      <div style={{ display: "grid", gap: 10 }}>
        <KeyRow label="动作数" value={String(round.participant_actions.length)} />
        <KeyRow label="状态" value={stringValue(asRecord(round.market_state).state)} />
        <KeyRow label="剧本" value={stringValue(asRecord(round.scenario_snapshot).dominant_scenario)} />
      </div>
    </button>
  );
}

function AgentDrilldownCard({
  eventId,
  row,
}: {
  eventId: string;
  row: AgentOrchestrationRow | null;
}) {
  if (!row) {
    return <Notice>当前没有可用的参与者钻取对象。</Notice>;
  }
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
          查看参与者详情
        </Link>
      </div>
      <div style={{ display: "grid", gap: 10, marginTop: 16 }}>
        <KeyRow label="Agent ID" value={row.participant_id} />
        <KeyRow label="风格变体" value={row.style_variant} />
        <KeyRow label="资金范围" value={row.capital_range} />
        <KeyRow label="状态变化" value={`${row.initial_state} -> ${row.final_state}`} />
        <KeyRow label="影响别人" value={String(row.outgoing_count)} />
        <KeyRow label="被影响次数" value={String(row.incoming_count)} />
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
              {action.action_type} / {action.next_state}
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}

function EdgeDrilldownCard({ edge }: { edge: InfluenceEdgeRecord | null }) {
  if (!edge) {
    return <Notice>当前窗口还没有影响边，或者边数据尚未生成。</Notice>;
  }
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
        <KeyRow label="来源 Agent" value={edge.source_participant_id} />
        <KeyRow label="目标 Agent" value={edge.target_participant_id} />
        <KeyRow label="影响强度" value={numberString(edge.strength)} />
        <KeyRow label="轮次" value={edge.round_id} />
      </div>
    </article>
  );
}

function NarrativeCard({ title, body }: { title: string; body: string }) {
  return (
    <article style={cardStyle}>
      <div style={{ color: "#f8fafc", fontSize: 18, fontWeight: 700 }}>{title}</div>
      <div style={{ ...mutedStyle, marginTop: 12 }}>{body}</div>
    </article>
  );
}

type AgentOrchestrationRow = {
  participant_id: string;
  participant_family: string;
  style_variant: string;
  stance: string;
  role: string;
  initial_state: string;
  final_state: string;
  capital_range: string;
  round_actions: Array<{ round_id: string; action_type: string; next_state: string }>;
  incoming_count: number;
  outgoing_count: number;
};

function buildOrchestrationRows(
  participants: ParticipantRecord[],
  rounds: RoundSnapshotRecord[],
  influenceRounds: InfluenceGraphPayload["rounds"],
): AgentOrchestrationRow[] {
  const firstRound = rounds[0];
  const latestRound = rounds[rounds.length - 1];
  return participants
    .map((participant) => {
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
        style_variant: stringValue(participant.style_variant, "默认风格"),
        stance: stringValue(participant.stance),
        role: stringValue(finalStateRecord.role ?? initialStateRecord.role, "watch"),
        initial_state: stringValue(participant.initial_state ?? initialStateRecord.state, "ready"),
        final_state: stringValue(finalStateRecord.state, "unknown"),
        capital_range: stringValue(asRecord(finalStateRecord).capital_range ?? participant.risk_budget_profile, "待接入 clone 级资金范围"),
        round_actions: roundActions,
        incoming_count: incomingCount,
        outgoing_count: outgoingCount,
      };
    })
    .sort((left, right) => right.outgoing_count - left.outgoing_count || right.incoming_count - left.incoming_count);
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

function resolveInfluenceRound(
  rounds: InfluenceGraphPayload["rounds"],
  roundId?: string,
) {
  return rounds.find((item) => item.round_id === roundId) ?? rounds[rounds.length - 1];
}

function buildEdgeKey(edge: InfluenceEdgeRecord, index: number) {
  return `${edge.source_participant_id}-${edge.target_participant_id}-${edge.round_id}-${index}`;
}

function windowLabelForRound(round: RoundSnapshotRecord | null) {
  if (!round) {
    return "-";
  }
  const explicitWindow = stringValue(asRecord(round).execution_window, "");
  if (explicitWindow !== "") {
    return explicitWindow;
  }
  return executionWindows[Math.max(0, Math.min(executionWindows.length - 1, round.order - 1))] ?? round.round_id;
}

function joinNarrative(...values: unknown[]) {
  const items = values.flatMap((value) => {
    if (Array.isArray(value)) {
      return value.map((item) => String(item));
    }
    if (value === null || value === undefined || value === "") {
      return [];
    }
    return [String(value)];
  });
  return items.length ? items.join("；") : "当前没有额外的链路说明。";
}
