import React from "react";
import Link from "next/link";

const shellStyle = {
  minHeight: "100vh",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background:
    "radial-gradient(circle at top left, rgba(16,185,129,0.12), transparent 20%), radial-gradient(circle at top right, rgba(59,130,246,0.12), transparent 20%), linear-gradient(180deg, #f8fbff 0%, #eef5ff 54%, #f8fafc 100%)",
  color: "#0f172a",
  fontFamily: '"Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif',
  padding: 24,
} as const;

const panelStyle = {
  width: "min(1120px, 100%)",
  borderRadius: 30,
  padding: "36px 32px",
  border: "1px solid rgba(148,163,184,0.22)",
  background: "rgba(255,255,255,0.86)",
  boxShadow: "0 26px 72px rgba(15,23,42,0.08)",
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
  borderRadius: 22,
  border: "1px solid rgba(148,163,184,0.18)",
  background: "rgba(248,250,252,0.94)",
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
            color: "#64748b",
            fontWeight: 700,
          }}
        >
          Versefina
        </div>
        <h1 style={{ marginTop: 14, fontSize: 42, lineHeight: 1.1, color: "#0f172a" }}>
          打开 Graph-first 事件沙盘工作台
        </h1>
        <p style={{ marginTop: 18, fontSize: 16, lineHeight: 1.9, color: "#475569", maxWidth: 860 }}>
          当前产品中心已经切到 `/workbench`。你可以从真实事件导入开始，进入类似 MiroFish 的图谱主舞台、双栏观察态、报告工作台和互动工作台。
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginTop: 24 }}>
          <Link
            href="/workbench"
            style={{
              ...actionStyle,
              background: "linear-gradient(135deg, rgba(59,130,246,0.14), rgba(16,185,129,0.14))",
              border: "1px solid rgba(59,130,246,0.28)",
              color: "#0f172a",
            }}
          >
            打开新工作台
          </Link>
          <Link
            href="/event-sandbox"
            style={{
              ...actionStyle,
              background: "rgba(255,255,255,0.92)",
              border: "1px solid rgba(148,163,184,0.22)",
              color: "#0f172a",
            }}
          >
            打开旧入口兼容页
          </Link>
          <a
            href="http://127.0.0.1:8001/docs"
            target="_blank"
            rel="noreferrer"
            style={{
              ...actionStyle,
              background: "rgba(255,255,255,0.92)",
              border: "1px solid rgba(148,163,184,0.22)",
              color: "#0f172a",
            }}
          >
            Swagger
          </a>
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
            <div style={{ color: "#2563eb", fontSize: 12, fontWeight: 700, letterSpacing: "0.08em" }}>Graph-first</div>
            <div style={{ marginTop: 10, fontSize: 20, fontWeight: 800 }}>大画布优先</div>
            <div style={{ marginTop: 10, color: "#475569", lineHeight: 1.7 }}>
              默认先看图谱主舞台和 Trade Pulse，而不是卡片墙或 JSON。
            </div>
          </div>
          <div style={cardStyle}>
            <div style={{ color: "#2563eb", fontSize: 12, fontWeight: 700, letterSpacing: "0.08em" }}>Workbench</div>
            <div style={{ marginTop: 10, fontSize: 20, fontWeight: 800 }}>双栏与报告态</div>
            <div style={{ marginTop: 10, color: "#475569", lineHeight: 1.7 }}>
              同一事件在图谱、双栏、工作台三个模式之间切换，而不是跳出到平行系统。
            </div>
          </div>
          <div style={cardStyle}>
            <div style={{ color: "#2563eb", fontSize: 12, fontWeight: 700, letterSpacing: "0.08em" }}>Evidence</div>
            <div style={{ marginTop: 10, fontSize: 20, fontWeight: 800 }}>证据引用优先</div>
            <div style={{ marginTop: 10, color: "#475569", lineHeight: 1.7 }}>
              图谱问答、状态解释和报告都优先引用 replay、validation 和 lineage，而不是空讲。
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
