import React from "react";
import Link from "next/link";

const shellStyle = {
  minHeight: "100vh",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background:
    "radial-gradient(circle at top left, rgba(14,165,233,0.16), transparent 22%), radial-gradient(circle at bottom right, rgba(249,115,22,0.16), transparent 22%), linear-gradient(160deg, #08111f 0%, #101b30 50%, #091220 100%)",
  color: "#e2e8f0",
  fontFamily: '"Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif',
  padding: 20,
} as const;

const panelStyle = {
  width: "min(1100px, 100%)",
  borderRadius: 28,
  padding: "36px 32px",
  border: "1px solid rgba(148, 163, 184, 0.16)",
  background: "rgba(8, 15, 30, 0.88)",
  boxShadow: "0 24px 64px rgba(2, 6, 23, 0.42)",
} as const;

const actionStyle = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "14px 20px",
  borderRadius: 999,
  textDecoration: "none",
  fontWeight: 700,
} as const;

const cardStyle = {
  borderRadius: 20,
  border: "1px solid rgba(148, 163, 184, 0.16)",
  background: "rgba(15, 23, 42, 0.72)",
  padding: "18px 18px 16px",
} as const;

export default function HomePage() {
  return (
    <div style={shellStyle}>
      <div style={panelStyle}>
        <div
          style={{
            fontSize: 12,
            letterSpacing: "0.16em",
            textTransform: "uppercase",
            color: "#94a3b8",
            fontWeight: 700,
          }}
        >
          Versefina
        </div>
        <h1 style={{ marginTop: 14, fontSize: 42, lineHeight: 1.15, color: "#f8fafc" }}>
          先打开真实事件沙盘
        </h1>
        <p style={{ marginTop: 18, fontSize: 16, lineHeight: 1.9, color: "#cbd5e1", maxWidth: 840 }}>
          当前主入口已经切换到 Roadmap 1.7 事件沙盘。你可以从一条真实市场消息出发，看到金融 Agent
          如何被激活、如何逐轮互动、谁影响了谁，以及信念、市场状态和剧本如何演化。
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginTop: 24 }}>
          <Link
            href="/event-sandbox"
            style={{
              ...actionStyle,
              background: "rgba(14, 165, 233, 0.16)",
              border: "1px solid rgba(125, 211, 252, 0.32)",
              color: "#e0f2fe",
            }}
          >
            打开事件沙盘
          </Link>
          <Link
            href="/roadmap-1-6-demo"
            style={{
              ...actionStyle,
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(148, 163, 184, 0.18)",
              color: "#e2e8f0",
            }}
          >
            打开旧版 1.6 演示
          </Link>
          <Link
            href="/onboarding"
            style={{
              ...actionStyle,
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(148, 163, 184, 0.18)",
              color: "#e2e8f0",
            }}
          >
            打开现有工作台
          </Link>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: 16,
            marginTop: 28,
          }}
        >
          <div style={cardStyle}>
            <div style={{ color: "#7dd3fc", fontSize: 12, fontWeight: 700, letterSpacing: "0.08em" }}>真实输入</div>
            <div style={{ marginTop: 10, fontSize: 20, fontWeight: 700 }}>消息进入即建事件种子</div>
            <div style={{ marginTop: 10, color: "#cbd5e1", lineHeight: 1.7 }}>
              支持手工输入和后续的 finahunt 真实事件导入，保留来源、时间和上下文线索。
            </div>
          </div>
          <div style={cardStyle}>
            <div style={{ color: "#7dd3fc", fontSize: 12, fontWeight: 700, letterSpacing: "0.08em" }}>参与演化</div>
            <div style={{ marginTop: 10, fontSize: 20, fontWeight: 700 }}>谁先动、谁跟随、谁施压</div>
            <div style={{ marginTop: 10, color: "#cbd5e1", lineHeight: 1.7 }}>
              页面会展示参与者角色、逐轮动作、影响边和关键转折点，而不是只给一份静态结论。
            </div>
          </div>
          <div style={cardStyle}>
            <div style={{ color: "#7dd3fc", fontSize: 12, fontWeight: 700, letterSpacing: "0.08em" }}>结果验证</div>
            <div style={{ marginTop: 10, fontSize: 20, fontWeight: 700 }}>市场状态与验证一屏收口</div>
            <div style={{ marginTop: 10, color: "#cbd5e1", lineHeight: 1.7 }}>
              你能同时看到 belief、scenario、market state、validation、why 和 reliability。
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
