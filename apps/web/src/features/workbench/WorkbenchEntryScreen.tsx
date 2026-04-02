"use client";

import { useRouter } from "next/navigation";
import React, { useState } from "react";

import { createWorkbenchEventChain, getApiBaseUrl, importEventFromFinahunt } from "./api";
import {
  ActionLink,
  WorkbenchShell,
  cardStyle,
  gridThreeStyle,
  gridTwoStyle,
  inputStyle,
  mutedStyle,
  Notice,
  primaryButtonStyle,
  softButtonStyle,
  StatPill,
  subtleCardStyle,
} from "./workbenchShared";

const statusCardStyle = {
  ...subtleCardStyle,
  padding: 18,
  display: "grid",
  gap: 12,
} as const;

const workflowCardStyle = {
  ...cardStyle,
  padding: 18,
  display: "grid",
  gap: 10,
} as const;

export function WorkbenchEntryScreen() {
  const router = useRouter();
  const [title, setTitle] = useState("铜库存挤压");
  const [body, setBody] = useState("库存快速下降推动铜链条补库预期升温，渠道和机构确认资金开始向上游资源端聚焦。");
  const [submitting, setSubmitting] = useState(false);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState("");

  async function handleManualSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const created = await createWorkbenchEventChain({
        title,
        body,
        source: "manual_text",
      });
      router.push(`/workbench/${created.event_id}`);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "创建工作台事件失败。");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleFinahuntImport() {
    setImporting(true);
    setError("");
    try {
      const imported = await importEventFromFinahunt({ auto_structure_prepare_simulate: true });
      router.push(`/workbench/${imported.event_id}`);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "导入真实 finahunt 事件失败。");
    } finally {
      setImporting(false);
    }
  }

  return (
    <WorkbenchShell
      title="Graph-first 事件沙盘工作台"
      description="这里不再把你直接扔进旧的事件详情页，而是先进入一个 MiroFish 风格的工作台入口：先导入真实事件，再进入图谱主舞台、双栏观察态、报告工作台和互动工作台。"
      actions={
        <>
          <ActionLink href={`${getApiBaseUrl()}/docs`} label="Swagger" external />
          <ActionLink href="http://127.0.0.1:8010/versefina/runtime" label="运行审计页" external />
          <ActionLink href="/event-sandbox" label="旧入口兼容页" />
        </>
      }
    >
      <section style={gridTwoStyle}>
        <article style={{ ...cardStyle, padding: 24 }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: "#2563eb", letterSpacing: "0.08em", textTransform: "uppercase" }}>
            上传 / 导入
          </div>
          <h2 style={{ marginTop: 12, fontSize: 36, lineHeight: 1.08, color: "#0f172a" }}>
            先把真实事件带进来，再让图谱自己动起来
          </h2>
          <p style={{ ...mutedStyle, marginTop: 14, maxWidth: 680 }}>
            工作台支持两种入口：从 finahunt 真实运行结果直接导入，或者手工输入一条市场事件来立即启动结构化、参与者准备和模拟。
          </p>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 18 }}>
            <button type="button" onClick={() => void handleFinahuntImport()} disabled={importing} style={primaryButtonStyle}>
              {importing ? "正在导入 finahunt 事件..." : "从 finahunt 导入真实事件"}
            </button>
            <ActionLink href="/workbench/evt-a-3-20-20260327132238026464" label="查看现成图谱样例" />
          </div>
        </article>
        <article style={statusCardStyle}>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <StatPill label="产品中心" value="/workbench" />
            <StatPill label="主视图" value="图谱 / 双栏 / 工作台" />
            <StatPill label="主舞台" value="影响网络优先" />
          </div>
          <div style={{ ...mutedStyle, marginTop: 6 }}>
            进入事件后，你会先看到左侧事件图谱、中间大画布、右侧决策与状态面板，以及底部回放时间轴。
          </div>
        </article>
      </section>

      <section style={gridTwoStyle}>
        <article style={{ ...cardStyle, padding: 24 }}>
          <div style={{ fontSize: 18, fontWeight: 800, color: "#0f172a" }}>手工创建工作台事件</div>
          <form onSubmit={handleManualSubmit} style={{ display: "grid", gap: 14, marginTop: 16 }}>
            <input value={title} onChange={(event) => setTitle(event.target.value)} style={inputStyle} placeholder="输入事件标题" />
            <textarea
              value={body}
              onChange={(event) => setBody(event.target.value)}
              style={{ ...inputStyle, minHeight: 150, resize: "vertical" }}
              placeholder="输入会引发市场演化的真实或拟真市场消息"
            />
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
              <button type="submit" disabled={submitting} style={primaryButtonStyle}>
                {submitting ? "正在创建工作台..." : "创建并进入工作台"}
              </button>
              <span style={mutedStyle}>创建后会自动跑完结构化、参与者准备和模拟，再跳到图谱主舞台。</span>
            </div>
            {error ? <Notice tone="error">{error}</Notice> : null}
          </form>
        </article>

        <article style={{ ...cardStyle, padding: 24 }}>
          <div style={{ fontSize: 18, fontWeight: 800, color: "#0f172a" }}>五步工作流概览</div>
          <div style={{ ...gridThreeStyle, marginTop: 16 }}>
            {[
              ["01 图谱构建", "把事件、市场对象、family、clone 和三类边统一进主画布。"],
              ["02 环境搭建", "顶栏状态、右侧面板、底部时间轴全部围绕同一事件同步。"],
              ["03 开始模拟", "按 round / window 观察谁先动、谁跟随、谁减仓、谁退出。"],
              ["04 报告生成", "把 replay、report、validation 和 provenance 收进工作台。"],
              ["05 深度互动", "在图谱、状态、clone、报告之间问答，并拿到证据引用。"],
            ].map(([titleText, bodyText]) => (
              <div key={titleText} style={workflowCardStyle}>
                <div style={{ fontWeight: 800, color: "#0f172a" }}>{titleText}</div>
                <div style={mutedStyle}>{bodyText}</div>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section style={{ ...subtleCardStyle, padding: 20 }}>
        <div style={{ fontSize: 18, fontWeight: 800, color: "#0f172a" }}>你运行后应该看到什么</div>
        <div style={{ ...gridThreeStyle, marginTop: 16 }}>
          {[
            ["左侧事件图谱", "来源消息、结构化结果、commodity/sector/symbol、因果链、确认与失效条件。"],
            ["中间大画布", "event / market object / family / clone 节点，加 event / influence / trade 三类边。"],
            ["右侧细节面板", "Event / Seed、Decision / Trade、State / Scenario、Why / Drilldown 四个标签。"],
            ["底部时间轴", "固定窗口 pre_open / open_5m / morning_30m / midday_reprice / afternoon_follow / close_positioning。"],
            ["双栏观察态", "左边大图谱，右边工作台分析区，适合边看边解释。"],
            ["报告与互动", "Report / Replay 模式和 Why / Interactive 模式，持续围绕同一事件。"],
          ].map(([heading, bodyText]) => (
            <div key={heading} style={workflowCardStyle}>
              <div style={{ fontWeight: 800, color: "#0f172a" }}>{heading}</div>
              <div style={mutedStyle}>{bodyText}</div>
            </div>
          ))}
        </div>
      </section>
    </WorkbenchShell>
  );
}
