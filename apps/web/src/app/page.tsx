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
  width: "min(980px, 100%)",
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

export default function HomePage() {
  return (
    <div style={shellStyle}>
      <div style={panelStyle}>
        <div style={{ fontSize: 12, letterSpacing: "0.16em", textTransform: "uppercase", color: "#94a3b8", fontWeight: 700 }}>
          Versefina
        </div>
        <h1 style={{ marginTop: 14, fontSize: 42, lineHeight: 1.15, color: "#f8fafc" }}>
          Open the live event sandbox first
        </h1>
        <p style={{ marginTop: 18, fontSize: 16, lineHeight: 1.9, color: "#cbd5e1", maxWidth: 760 }}>
          The main entry is now the Roadmap 1.7 event sandbox. You can send in one market message, watch participants activate,
          replay the round-by-round interaction path, and inspect the belief, market-state, and scenario changes.
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
            Open event sandbox
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
            Open legacy 1.6 demo
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
            Open existing workspace
          </Link>
        </div>
      </div>
    </div>
  );
}
