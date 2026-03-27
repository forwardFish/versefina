"use client";

import { useRouter } from "next/navigation";
import React, { useState } from "react";

import { createEventChain, getApiBaseUrl, importEventFromFinahunt } from "./api";
import {
  ActionLink,
  LabelBlock,
  MiniCard,
  Notice,
  PageShell,
  SectionHeader,
  gridThreeStyle,
  inputStyle,
  mutedStyle,
  panelStyle,
} from "./shared";

const sampleBulletStyle = {
  margin: 0,
  paddingLeft: 18,
  color: "#cbd5e1",
  lineHeight: 1.8,
} as const;

const metricGridStyle = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
  gap: 12,
} as const;

export function EventSandboxEntryScreen() {
  const router = useRouter();
  const [title, setTitle] = useState("锂价冲击");
  const [body, setBody] = useState(
    "锂盐供应收紧推动上游价格快速走高，产业链渠道开始确认涨价，短线资金追逐资源端标的。",
  );
  const [submitting, setSubmitting] = useState(false);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const created = await createEventChain({
        title,
        body,
        source: "manual_text",
      });
      router.push(`/event-sandbox/${created.event_id}`);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "创建事件失败。");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleFinahuntImport() {
    setImporting(true);
    setError("");
    try {
      const imported = await importEventFromFinahunt({ auto_structure_prepare_simulate: true });
      router.push(`/event-sandbox/${imported.event_id}`);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "导入真实 Finahunt 事件失败。");
    } finally {
      setImporting(false);
    }
  }

  return (
    <PageShell
      eyebrow="Versefina 1.7 沙盘"
      title="真实事件演化墙"
      description="这里不是静态 Demo，而是一条真实规则链路的入口。你可以手工输入一条事件，也可以直接从 Finahunt 的真实运行结果导入，然后一路看到参与者激活、多轮互动、影响传播和最终验证。"
      actions={
        <>
          <ActionLink href={`${getApiBaseUrl()}/docs`} label="打开 Swagger" external />
          <ActionLink href="http://127.0.0.1:8010/versefina/runtime" label="打开运行审计页" external />
          <ActionLink href="/event-sandbox/evt-copper-inventory-squeeze-20260325160351771104" label="查看现成样例" />
          <ActionLink href="/roadmap-1-6-demo" label="查看旧版 1.6 演示" />
        </>
      }
    >
      <section style={panelStyle}>
        <SectionHeader
          eyebrow="入口"
          title="提交事件或导入真实来源"
          description="手工输入会直接调用真实 API 完成结构化、参与者准备和推演。导入按钮会从最新的 Finahunt 真实运行结果中选出事件候选，并自动生成 Versefina 事件沙盘。"
        />
        <form onSubmit={handleSubmit} style={{ display: "grid", gap: 18 }}>
          <LabelBlock label="事件标题">
            <input
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              style={inputStyle}
              placeholder="例如：锂价冲击"
            />
          </LabelBlock>
          <LabelBlock label="消息正文">
            <textarea
              value={body}
              onChange={(event) => setBody(event.target.value)}
              style={{ ...inputStyle, minHeight: 180, resize: "vertical" }}
              placeholder="描述你要推演的真实市场消息。"
            />
          </LabelBlock>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center" }}>
            <button
              type="submit"
              disabled={submitting}
              style={{
                border: "1px solid rgba(56, 189, 248, 0.34)",
                borderRadius: 999,
                padding: "14px 20px",
                background: "rgba(14, 165, 233, 0.16)",
                color: "#e0f2fe",
                fontWeight: 700,
                cursor: submitting ? "wait" : "pointer",
              }}
            >
              {submitting ? "正在运行真实链路..." : "启动事件沙盘"}
            </button>
            <button
              type="button"
              disabled={importing}
              onClick={() => void handleFinahuntImport()}
              style={{
                border: "1px solid rgba(251, 146, 60, 0.34)",
                borderRadius: 999,
                padding: "14px 20px",
                background: "rgba(249, 115, 22, 0.16)",
                color: "#ffedd5",
                fontWeight: 700,
                cursor: importing ? "wait" : "pointer",
              }}
            >
              {importing ? "正在导入真实 Finahunt 事件..." : "导入真实 Finahunt 事件"}
            </button>
            <span style={mutedStyle}>页面只读取真实 API 结果，不用 mock 数据冒充效果。</span>
          </div>
          {error ? <Notice tone="error">{error}</Notice> : null}
        </form>
      </section>

      <section style={{ ...panelStyle, marginTop: 20 }}>
        <SectionHeader
          eyebrow="你会看到什么"
          title="不是一张表单，而是一整面演化墙"
          description="提交后，下一页会把这条事件如何推动金融 Agent 逐轮演化完整展示出来。"
        />
        <div style={gridThreeStyle}>
          <MiniCard title="参与者编排" value="展示激活了多少金融 Agent、各自角色、激活原因和当前状态。" />
          <MiniCard title="轮次时间轴" value="展示 3 到 5 轮推演，谁先动、谁跟随、谁施压以及关键转折点。" />
          <MiniCard title="影响传播图" value="把谁影响了谁、影响原因和方向放到同一张网络图里。" />
          <MiniCard title="信念与剧本" value="按轮次展示 belief、bull/base/bear 剧本和当前主导路径。" />
          <MiniCard title="市场状态" value="直接看到从 DORMANT 到 INVALIDATED 的状态变化。" />
          <MiniCard title="验证结果" value="最终页会显示 predicted、actual、score、why 和 reliability。" />
        </div>
      </section>

      <section style={{ ...panelStyle, marginTop: 20 }}>
        <SectionHeader
          eyebrow="产品旅程"
          title="这条链路会把一条消息一路带到验证"
          description="你可以把它理解成一面单事件演化墙：先输入，再看过程，最后看结果。"
        />
        <div style={metricGridStyle}>
          <MiniCard title="第 1 步" value="事件结构化：提取类型、标的、题材、证据和失效条件。" />
          <MiniCard title="第 2 步" value="参与者激活：生成首发者、跟随者、风险观察者的阵列。" />
          <MiniCard title="第 3 步" value="多轮互动：按轮次输出动作、状态、影响传播和关键变化。" />
          <MiniCard title="第 4 步" value="结果收口：把 replay、validation、why 和 reliability 一起展示。" />
        </div>
        <div style={{ marginTop: 18, display: "grid", gap: 16 }}>
          <div
            style={{
              borderRadius: 18,
              border: "1px solid rgba(148, 163, 184, 0.14)",
              background: "rgba(15, 23, 42, 0.68)",
              padding: "18px 18px 16px",
            }}
          >
            <div style={{ fontWeight: 700, color: "#f8fafc" }}>现成样例里已经能看到什么</div>
            <ul style={sampleBulletStyle}>
              <li>8 个金融 Agent 被激活，并分成首发、跟随和风险观察三类角色。</li>
              <li>3 轮推演把市场状态从点火推进到传播和脆弱阶段。</li>
              <li>参与者详情页可以看到入边、出边和逐轮动作。</li>
              <li>验证页可以同时看到 predicted、actual、score 和 why。</li>
              <li>现在也可以直接从真实 Finahunt 排行结果导入事件，并在总览页看到来源 run 和消息链路。</li>
            </ul>
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
            <ActionLink href="/event-sandbox/evt-copper-inventory-squeeze-20260325160351771104" label="打开总览样例" />
            <ActionLink href="/event-sandbox/evt-copper-inventory-squeeze-20260325160351771104/replay" label="打开回放样例" />
            <ActionLink
              href="/event-sandbox/evt-copper-inventory-squeeze-20260325160351771104/participants/institution_confirmation%3Atrend_confirmation"
              label="打开参与者样例"
            />
            <ActionLink href="/event-sandbox/evt-copper-inventory-squeeze-20260325160351771104/validation" label="打开验证样例" />
          </div>
        </div>
      </section>
    </PageShell>
  );
}
