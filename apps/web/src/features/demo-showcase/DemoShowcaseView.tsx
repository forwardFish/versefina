import React, { type CSSProperties, type ReactNode } from "react";

import type { AcceptanceDemo, EventDemo, RuntimeShowcasePayload, StatementDemo } from "./types";

type DemoShowcaseViewProps = {
  apiBaseUrl: string;
  dashboardBaseUrl: string;
  payload: RuntimeShowcasePayload | null;
  status: "loading" | "ready" | "error";
  errorMessage?: string;
};

const shellStyle: CSSProperties = {
  minHeight: "100vh",
  background:
    "radial-gradient(circle at top left, rgba(14,165,233,0.16), transparent 22%), radial-gradient(circle at top right, rgba(249,115,22,0.14), transparent 24%), linear-gradient(160deg, #07111d 0%, #091827 48%, #0a1020 100%)",
  color: "#e2e8f0",
  fontFamily: '"Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif',
};

const containerStyle: CSSProperties = {
  width: "min(1240px, calc(100% - 32px))",
  margin: "0 auto",
  padding: "32px 0 72px",
};

const heroStyle: CSSProperties = {
  borderRadius: 32,
  padding: "32px 28px",
  border: "1px solid rgba(148, 163, 184, 0.18)",
  background: "linear-gradient(180deg, rgba(13, 23, 40, 0.96), rgba(8, 14, 27, 0.92))",
  boxShadow: "0 24px 64px rgba(2, 6, 23, 0.42)",
};

const sectionStyle: CSSProperties = {
  marginTop: 24,
  borderRadius: 28,
  padding: 24,
  border: "1px solid rgba(148, 163, 184, 0.14)",
  background: "rgba(9, 16, 31, 0.9)",
  boxShadow: "0 18px 48px rgba(2, 6, 23, 0.3)",
};

const cardStyle: CSSProperties = {
  borderRadius: 22,
  border: "1px solid rgba(148, 163, 184, 0.14)",
  background: "rgba(15, 23, 42, 0.72)",
  padding: 18,
};

const gridTwoStyle: CSSProperties = {
  display: "grid",
  gap: 18,
  gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
};

const statGridStyle: CSSProperties = {
  display: "grid",
  gap: 14,
  gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
  marginTop: 22,
};

const timelineGridStyle: CSSProperties = {
  display: "grid",
  gap: 14,
  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
  marginTop: 16,
};

const pillBaseStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 8,
  borderRadius: 999,
  padding: "7px 12px",
  fontSize: 12,
  lineHeight: 1,
  letterSpacing: "0.08em",
  textTransform: "uppercase",
  border: "1px solid rgba(148, 163, 184, 0.18)",
};

const labelStyle: CSSProperties = {
  fontSize: 12,
  letterSpacing: "0.16em",
  textTransform: "uppercase",
  color: "#94a3b8",
  fontWeight: 700,
};

const valueTitleStyle: CSSProperties = {
  marginTop: 8,
  fontSize: 26,
  lineHeight: 1.2,
  fontWeight: 700,
  color: "#f8fafc",
};

const mutedStyle: CSSProperties = {
  fontSize: 14,
  lineHeight: 1.8,
  color: "#cbd5e1",
};

const codeStyle: CSSProperties = {
  marginTop: 12,
  borderRadius: 16,
  padding: 14,
  background: "rgba(2, 6, 23, 0.78)",
  border: "1px solid rgba(148, 163, 184, 0.12)",
  color: "#dbeafe",
  fontFamily: 'Consolas, "Courier New", monospace',
  fontSize: 12,
  lineHeight: 1.6,
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
};

export function DemoShowcaseView({ apiBaseUrl, dashboardBaseUrl, payload, status, errorMessage }: DemoShowcaseViewProps) {
  return (
    <main style={shellStyle}>
      <div style={containerStyle}>
        <section style={heroStyle}>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 16, justifyContent: "space-between", alignItems: "flex-start" }}>
            <div style={{ maxWidth: 760 }}>
              <div style={labelStyle}>Roadmap 1.6 Product Demo</div>
              <h1 style={{ ...valueTitleStyle, fontSize: 42 }}>
                这不是统计面板，而是 `roadmap_1_6` 真正跑出来的业务效果页
              </h1>
              <p style={{ ...mutedStyle, marginTop: 16 }}>
                页面直接消费最新 `.runtime` 真实产物，按事件推演链和 statement 镜像链讲清楚系统到底推演了什么、为什么这样判断、最后交付边界停在哪里。
              </p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginTop: 18 }}>
                {statusPill(status)}
                {payload?.acceptance_demo?.status ? statusPill(String(payload.acceptance_demo.status), "acceptance pack") : null}
                {payload?.event_demo?.status ? statusPill(String(payload.event_demo.status), "event lane") : null}
                {payload?.statement_demo?.status ? statusPill(String(payload.statement_demo.status), "statement lane") : null}
              </div>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
              {linkButton("Swagger", `${apiBaseUrl}/docs`, true)}
              {linkButton("验收台", `${dashboardBaseUrl}/versefina/runtime`, true)}
              {linkButton("执行报告", `${dashboardBaseUrl}/versefina/runtime/report`, true)}
            </div>
          </div>
          <div style={statGridStyle}>
            <MetricCard label="事件样例" value={payload?.event_demo?.event_id || "暂无"} />
            <MetricCard label="Dominant Scenario" value={stringValue(payload?.event_demo?.summary?.dominant_scenario)} />
            <MetricCard label="实际 Outcome" value={stringValue(payload?.event_demo?.summary?.actual_outcome)} />
            <MetricCard label="Mirror Archetype" value={stringValue(payload?.statement_demo?.mirror_agent?.archetype_name)} />
          </div>
        </section>

        <section style={sectionStyle}>
          <SectionHeader
            eyebrow="Event Lane"
            title="事件推演链"
            description="从 event 到 prepare、belief / scenario、simulation、outcome、why，把一条真实事件如何被系统处理讲清楚。"
          />
          {status === "loading" && !payload ? <EmptyState message="正在加载最新 runtime 样例..." /> : null}
          {status === "error" ? <EmptyState message={errorMessage || "加载 demo 数据失败。"} tone="error" /> : null}
          {payload ? <EventLane eventDemo={payload.event_demo} /> : null}
        </section>

        <section style={sectionStyle}>
          <SectionHeader
            eyebrow="Statement Lane"
            title="Statement -> Style -> Mirror"
            description="展示 statement 被解析为风格向量、映射到 mirror agent，再进入 validation 和 distribution calibration 的真实结果。"
          />
          {payload ? <StatementLane statementDemo={payload.statement_demo} /> : null}
        </section>

        <section style={sectionStyle}>
          <SectionHeader
            eyebrow="Acceptance"
            title="Roadmap Acceptance Pack"
            description="这里不是流程统计，而是最后对 P0/P1 边界、当前 handoff 和交付物的业务收口。"
          />
          {payload ? <AcceptanceLane acceptanceDemo={payload.acceptance_demo} /> : null}
        </section>

        <section style={sectionStyle}>
          <SectionHeader
            eyebrow="Evidence"
            title="证据入口与原始 payload"
            description="首屏只讲业务摘要，原始结构化 payload 放在折叠区，方便进一步审计但不打断阅读。"
          />
          <div style={gridTwoStyle}>
            <EvidenceCard
              title="入口链接"
              body={
                <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
                  {linkButton("Swagger", `${apiBaseUrl}/docs`, true)}
                  {linkButton("Demo API", `${apiBaseUrl}/api/v1/demo/runtime-showcase`, true)}
                  {linkButton("Dashboard", `${dashboardBaseUrl}/versefina/runtime`, true)}
                </div>
              }
            />
            <EvidenceCard
              title="数据来源"
              body={<pre style={codeStyle}>{JSON.stringify(payload?.source_paths ?? {}, null, 2)}</pre>}
            />
          </div>
          {payload ? <RawPayloads payload={payload} /> : null}
        </section>
      </div>
    </main>
  );
}

function EventLane({ eventDemo }: { eventDemo: EventDemo }) {
  if (eventDemo.status !== "ready") {
    return <EmptyState message={stringValue(eventDemo.summary?.message, "暂无真实事件样例。")} />;
  }

  const timeline = recordOfUnknown(eventDemo.simulation?.timeline);
  const topParticipants = listOfRecords(eventDemo.simulation?.top_participants);
  const turningPoints = listOfUnknown(timeline.turning_points);
  const firstMove = listOfRecords(timeline.first_move);
  const followOn = listOfRecords(timeline.follow_on);

  return (
    <div style={{ display: "grid", gap: 18 }}>
      <div style={gridTwoStyle}>
        <StoryCard
          title={stringValue(eventDemo.summary?.title, "未命名事件")}
          subtitle={stringValue(eventDemo.summary?.body, "")}
          items={[
            { label: "事件类型", value: stringValue(eventDemo.summary?.event_type) },
            { label: "映射标的", value: joinList(eventDemo.mapping?.target_symbols) },
            { label: "dominant scenario", value: stringValue(eventDemo.summary?.dominant_scenario) },
            { label: "actual outcome", value: stringValue(eventDemo.summary?.actual_outcome) },
            { label: "score label", value: stringValue(eventDemo.summary?.score_label) },
          ]}
        />
        <StoryCard
          title="为什么系统会这么判断"
          subtitle={stringValue(eventDemo.why?.answer, "暂无 why 答案。")}
          items={[
            { label: "关键支持者", value: joinList(eventDemo.why?.supporters) },
            { label: "转折点", value: joinList(eventDemo.why?.turning_points) },
          ]}
        />
      </div>

      <div style={gridTwoStyle}>
        <StoryCard
          title="Participant Roster"
          subtitle="按 authority weight 选出的关键参与者。"
          body={
            topParticipants.length ? (
              <div style={{ display: "grid", gap: 10, marginTop: 14 }}>
                {topParticipants.map((item) => (
                  <div key={stringValue(item.participant_id)} style={{ ...cardStyle, padding: 14 }}>
                    <div style={{ color: "#f8fafc", fontWeight: 600 }}>{stringValue(item.participant_id)}</div>
                    <div style={{ ...mutedStyle, marginTop: 6 }}>
                      {stringValue(item.participant_family)} / {stringValue(item.role)} / {stringValue(item.stance)}
                    </div>
                    <div style={{ ...mutedStyle, marginTop: 4 }}>authority {stringValue(item.authority_weight)} / state {stringValue(item.state)}</div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState message="暂无 participant roster。" />
            )
          }
        />
        <StoryCard
          title="Simulation Timeline"
          subtitle="首轮启动、跟随响应和最终转折点，帮助你快速看懂模拟路径。"
          body={
            <div style={timelineGridStyle}>
              <TimelineCard title="First Move" items={firstMove.map((item) => stringValue(item.participant_id))} />
              <TimelineCard title="Follow On" items={followOn.map((item) => stringValue(item.participant_id))} />
              <TimelineCard title="Turning Points" items={turningPoints.map((item) => String(item))} />
            </div>
          }
        />
      </div>
    </div>
  );
}

function StatementLane({ statementDemo }: { statementDemo: StatementDemo }) {
  if (statementDemo.status !== "ready") {
    return <EmptyState message={stringValue(statementDemo.summary?.message, "暂无真实 statement 样例。")} />;
  }

  const featureVector = recordOfUnknown(statementDemo.style_features?.feature_vector);
  const calibrationSegments = listOfRecords(statementDemo.distribution_calibration?.segments);

  return (
    <div style={{ display: "grid", gap: 18 }}>
      <div style={gridTwoStyle}>
        <StoryCard
          title={stringValue(statementDemo.summary?.file_name, "Statement")}
          subtitle={`statement_id: ${stringValue(statementDemo.statement_id)}`}
          items={[
            { label: "market", value: stringValue(statementDemo.summary?.market) },
            { label: "upload status", value: stringValue(statementDemo.summary?.upload_status) },
            { label: "parser", value: stringValue(statementDemo.parse_report?.parser_key) },
            { label: "trade count", value: stringValue(statementDemo.parse_report?.trade_count) },
          ]}
        />
        <StoryCard
          title="Mirror Agent Profile"
          subtitle="statement 被归入哪个 archetype、哪个 participant family。"
          items={[
            { label: "archetype", value: stringValue(statementDemo.mirror_agent?.archetype_name) },
            { label: "participant family", value: stringValue(statementDemo.mirror_agent?.participant_family) },
            { label: "grading", value: stringValue(statementDemo.mirror_validation?.grading) },
            { label: "risk posture", value: stringValue(statementDemo.mirror_validation?.risk_posture) },
          ]}
        />
      </div>

      <div style={gridTwoStyle}>
        <StoryCard
          title="Style Feature Vector"
          subtitle="不直接扔原始 JSON，而是先展示最关键的行为特征。"
          body={
            Object.keys(featureVector).length ? (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginTop: 14 }}>
                {Object.entries(featureVector).map(([key, value]) => (
                  <div key={key} style={{ ...pillBaseStyle, background: "rgba(14, 165, 233, 0.12)", color: "#e0f2fe" }}>
                    <strong>{key}</strong>: {String(value)}
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState message="暂无 style feature vector。" />
            )
          }
        />
        <StoryCard
          title="Distribution Calibration"
          subtitle="镜像校准后的分布分段，用来回答这类 statement 最终落在哪个参与者簇。"
          body={
            calibrationSegments.length ? (
              <div style={{ display: "grid", gap: 10, marginTop: 14 }}>
                {calibrationSegments.map((item, index) => (
                  <div key={`${stringValue(item.label)}-${index}`} style={{ ...cardStyle, padding: 14 }}>
                    <div style={{ color: "#f8fafc", fontWeight: 600 }}>{stringValue(item.label, `segment-${index + 1}`)}</div>
                    <div style={{ ...mutedStyle, marginTop: 6 }}>{JSON.stringify(item)}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ ...mutedStyle, marginTop: 14 }}>
                sample_size {stringValue(statementDemo.distribution_calibration?.sample_size)} / hit_rate{" "}
                {stringValue(statementDemo.distribution_calibration?.hit_rate)}
              </div>
            )
          }
        />
      </div>
    </div>
  );
}

function AcceptanceLane({ acceptanceDemo }: { acceptanceDemo: AcceptanceDemo }) {
  if (acceptanceDemo.status !== "ready") {
    return <EmptyState message={stringValue(acceptanceDemo.summary?.message, "暂无 acceptance pack。")} />;
  }

  const p0 = listOfRecords(acceptanceDemo.p0_boundaries);
  const p1 = listOfRecords(acceptanceDemo.p1_boundaries);
  const artifacts = listOfRecords(acceptanceDemo.delivery_artifacts);

  return (
    <div style={{ display: "grid", gap: 18 }}>
      <div style={gridTwoStyle}>
        <StoryCard
          title={stringValue(acceptanceDemo.headline, "Acceptance Pack")}
          subtitle={`roadmap_id: ${stringValue(acceptanceDemo.roadmap_id)}`}
          items={[
            { label: "status", value: stringValue(acceptanceDemo.summary?.status) },
            { label: "P0 boundaries", value: stringValue(acceptanceDemo.summary?.p0_count) },
            { label: "P1 boundaries", value: stringValue(acceptanceDemo.summary?.p1_count) },
            { label: "artifacts", value: stringValue(acceptanceDemo.summary?.delivery_artifact_count) },
          ]}
        />
        <StoryCard
          title="Current Handoff"
          subtitle="这就是 fresh chat 续跑时真正该看的边界。"
          items={[
            { label: "status", value: stringValue(acceptanceDemo.current_handoff?.status) },
            { label: "story", value: stringValue(acceptanceDemo.current_handoff?.story) },
            { label: "next action", value: stringValue(acceptanceDemo.current_handoff?.next_action) },
          ]}
        />
      </div>
      <div style={gridTwoStyle}>
        <StoryCard title="P0 Boundary" subtitle="必须稳定的主业务能力线。" body={<BoundaryList items={p0} />} />
        <StoryCard title="P1 Boundary" subtitle="在 P0 之上的增强层。" body={<BoundaryList items={p1} />} />
      </div>
      <StoryCard
        title="Delivery Artifacts"
        subtitle="这里摘取最关键的交付项，帮助快速判断 roadmap 是否真的落地。"
        body={
          artifacts.length ? (
            <div style={{ display: "grid", gap: 10, marginTop: 14 }}>
              {artifacts.map((item, index) => (
                <div key={`${stringValue(item.story_id)}-${index}`} style={{ ...cardStyle, padding: 14 }}>
                  <div style={{ color: "#f8fafc", fontWeight: 600 }}>
                    {stringValue(item.sprint)} / {stringValue(item.story_id)}
                  </div>
                  <div style={{ ...mutedStyle, marginTop: 6 }}>{stringValue(item.summary)}</div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState message="暂无 delivery artifacts。" />
          )
        }
      />
    </div>
  );
}

function RawPayloads({ payload }: { payload: RuntimeShowcasePayload }) {
  return (
    <div style={{ display: "grid", gap: 14, marginTop: 18 }}>
      <RawPayload title="Event Payload" data={payload.event_demo} />
      <RawPayload title="Statement Payload" data={payload.statement_demo} />
      <RawPayload title="Acceptance Payload" data={payload.acceptance_demo} />
    </div>
  );
}

function RawPayload({ title, data }: { title: string; data: unknown }) {
  return (
    <details style={{ ...cardStyle, padding: 0, overflow: "hidden" }}>
      <summary style={{ cursor: "pointer", padding: "16px 18px", color: "#f8fafc", fontWeight: 600 }}>{title} · 查看原始 payload</summary>
      <pre style={{ ...codeStyle, margin: 0, borderRadius: 0 }}>{JSON.stringify(data, null, 2)}</pre>
    </details>
  );
}

function BoundaryList({ items }: { items: Array<Record<string, unknown>> }) {
  if (!items.length) {
    return <EmptyState message="暂无 boundary。" />;
  }
  return (
    <div style={{ display: "grid", gap: 10, marginTop: 14 }}>
      {items.map((item, index) => (
        <div key={`${stringValue(item.label)}-${index}`} style={{ ...cardStyle, padding: 14 }}>
          <div style={{ color: "#f8fafc", fontWeight: 600 }}>
            {stringValue(item.priority)} / {stringValue(item.label)}
          </div>
          <div style={{ ...mutedStyle, marginTop: 6 }}>{stringValue(item.objective)}</div>
        </div>
      ))}
    </div>
  );
}

function TimelineCard({ title, items }: { title: string; items: string[] }) {
  return (
    <div style={{ ...cardStyle, padding: 16 }}>
      <div style={{ color: "#f8fafc", fontWeight: 600 }}>{title}</div>
      <div style={{ ...mutedStyle, marginTop: 10 }}>
        {items.length ? items.map((item) => <div key={item}>- {item}</div>) : "暂无"}
      </div>
    </div>
  );
}

function StoryCard({
  title,
  subtitle,
  items,
  body,
}: {
  title: string;
  subtitle: string;
  items?: Array<{ label: string; value: string }>;
  body?: ReactNode;
}) {
  return (
    <article style={cardStyle}>
      <div style={{ color: "#f8fafc", fontSize: 20, fontWeight: 700 }}>{title}</div>
      <div style={{ ...mutedStyle, marginTop: 8 }}>{subtitle}</div>
      {items?.length ? (
        <div style={{ display: "grid", gap: 10, marginTop: 16 }}>
          {items.map((item) => (
            <div key={item.label} style={{ display: "flex", justifyContent: "space-between", gap: 16, borderTop: "1px solid rgba(148, 163, 184, 0.12)", paddingTop: 10 }}>
              <div style={{ color: "#94a3b8", fontSize: 13, letterSpacing: "0.06em", textTransform: "uppercase" }}>{item.label}</div>
              <div style={{ color: "#f8fafc", textAlign: "right" }}>{item.value}</div>
            </div>
          ))}
        </div>
      ) : null}
      {body}
    </article>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ ...cardStyle, padding: 16 }}>
      <div style={labelStyle}>{label}</div>
      <div style={{ marginTop: 10, fontSize: 22, fontWeight: 700, color: "#f8fafc" }}>{value}</div>
    </div>
  );
}

function EvidenceCard({ title, body }: { title: string; body: ReactNode }) {
  return (
    <div style={cardStyle}>
      <div style={{ color: "#f8fafc", fontSize: 18, fontWeight: 700 }}>{title}</div>
      <div style={{ marginTop: 12 }}>{body}</div>
    </div>
  );
}

function SectionHeader({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return (
    <div style={{ marginBottom: 18 }}>
      <div style={labelStyle}>{eyebrow}</div>
      <h2 style={{ ...valueTitleStyle, fontSize: 30 }}>{title}</h2>
      <p style={{ ...mutedStyle, marginTop: 10, maxWidth: 820 }}>{description}</p>
    </div>
  );
}

function EmptyState({ message, tone = "neutral" }: { message: string; tone?: "neutral" | "error" }) {
  return (
    <div
      style={{
        ...cardStyle,
        color: tone === "error" ? "#fecaca" : "#cbd5e1",
        borderColor: tone === "error" ? "rgba(248, 113, 113, 0.28)" : "rgba(148, 163, 184, 0.14)",
      }}
    >
      {message}
    </div>
  );
}

function statusPill(status: string, label?: string) {
  const lower = status.toLowerCase();
  const tone =
    lower === "ready"
      ? { background: "rgba(16, 185, 129, 0.14)", color: "#d1fae5", borderColor: "rgba(16, 185, 129, 0.26)" }
      : lower === "missing"
        ? { background: "rgba(248, 113, 113, 0.12)", color: "#fecaca", borderColor: "rgba(248, 113, 113, 0.24)" }
        : lower === "error"
          ? { background: "rgba(244, 63, 94, 0.14)", color: "#fecdd3", borderColor: "rgba(244, 63, 94, 0.24)" }
          : { background: "rgba(56, 189, 248, 0.12)", color: "#dbeafe", borderColor: "rgba(56, 189, 248, 0.24)" };

  return (
    <span style={{ ...pillBaseStyle, ...tone }}>
      {label ? `${label}: ` : ""}
      {status}
    </span>
  );
}

function linkButton(label: string, href: string, external = false) {
  return (
    <a
      href={href}
      target={external ? "_blank" : undefined}
      rel={external ? "noreferrer" : undefined}
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "12px 16px",
        borderRadius: 999,
        border: "1px solid rgba(125, 211, 252, 0.3)",
        background: "rgba(14, 165, 233, 0.12)",
        color: "#e0f2fe",
        textDecoration: "none",
        fontWeight: 600,
      }}
    >
      {label}
    </a>
  );
}

function stringValue(value: unknown, fallback = "-") {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  return String(value);
}

function joinList(value: unknown) {
  const items = listOfUnknown(value).map((item) => String(item));
  return items.length ? items.join(", ") : "-";
}

function listOfUnknown(value: unknown) {
  return Array.isArray(value) ? value : [];
}

function recordOfUnknown(value: unknown) {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
}

function listOfRecords(value: unknown) {
  return listOfUnknown(value).filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object" && !Array.isArray(item));
}
