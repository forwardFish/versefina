"use client";

import React from "react";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState, type CSSProperties, type ReactNode } from "react";

export type AsyncState<T> = {
  status: "loading" | "ready" | "error";
  data: T | null;
  error: string;
};

export const shellStyle: CSSProperties = {
  minHeight: "100vh",
  background:
    "radial-gradient(circle at top left, rgba(14,165,233,0.18), transparent 22%), radial-gradient(circle at top right, rgba(251,146,60,0.18), transparent 24%), linear-gradient(160deg, #081120 0%, #0c1729 42%, #0a1120 100%)",
  color: "#e2e8f0",
  fontFamily: '"Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif',
};

export const containerStyle: CSSProperties = {
  width: "min(1280px, calc(100% - 32px))",
  margin: "0 auto",
  padding: "28px 0 72px",
};

export const heroStyle: CSSProperties = {
  borderRadius: 30,
  padding: "28px 24px",
  border: "1px solid rgba(148, 163, 184, 0.18)",
  background: "linear-gradient(180deg, rgba(10, 18, 33, 0.96), rgba(9, 14, 26, 0.92))",
  boxShadow: "0 26px 66px rgba(2, 6, 23, 0.46)",
};

export const panelStyle: CSSProperties = {
  borderRadius: 24,
  padding: 20,
  border: "1px solid rgba(148, 163, 184, 0.14)",
  background: "rgba(9, 16, 31, 0.92)",
  boxShadow: "0 16px 40px rgba(2, 6, 23, 0.28)",
};

export const cardStyle: CSSProperties = {
  borderRadius: 20,
  padding: 18,
  border: "1px solid rgba(148, 163, 184, 0.12)",
  background: "rgba(15, 23, 42, 0.72)",
};

export const labelStyle: CSSProperties = {
  fontSize: 12,
  lineHeight: 1,
  letterSpacing: "0.16em",
  textTransform: "uppercase",
  color: "#94a3b8",
  fontWeight: 700,
};

export const titleStyle: CSSProperties = {
  marginTop: 8,
  fontSize: 30,
  lineHeight: 1.15,
  color: "#f8fafc",
  fontWeight: 700,
};

export const mutedStyle: CSSProperties = {
  fontSize: 14,
  lineHeight: 1.8,
  color: "#cbd5e1",
};

export const gridTwoStyle: CSSProperties = {
  display: "grid",
  gap: 18,
  gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
};

export const gridThreeStyle: CSSProperties = {
  display: "grid",
  gap: 18,
  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
};

export const codeStyle: CSSProperties = {
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

export const linkStyle: CSSProperties = {
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
};

export const inputStyle: CSSProperties = {
  width: "100%",
  borderRadius: 18,
  padding: "14px 16px",
  background: "rgba(15, 23, 42, 0.92)",
  color: "#f8fafc",
  border: "1px solid rgba(148, 163, 184, 0.18)",
  outline: "none",
  fontSize: 15,
  lineHeight: 1.7,
};

export const pillStyle: CSSProperties = {
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

export const pillButtonStyle: CSSProperties = {
  borderRadius: 999,
  border: "1px solid rgba(148, 163, 184, 0.2)",
  padding: "10px 14px",
  color: "#dbeafe",
  cursor: "pointer",
};

export function useAsyncPayload<T>(loader: () => Promise<T>, deps: Array<string | number>) {
  const [state, setState] = useState<AsyncState<T>>({
    status: "loading",
    data: null,
    error: "",
  });
  const dependencyKey = useMemo(() => deps.map((value) => String(value)).join("::"), [deps]);
  const loaderRef = useRef(loader);

  useEffect(() => {
    loaderRef.current = loader;
  }, [loader]);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setState({ status: "loading", data: null, error: "" });
      try {
        const result = await loaderRef.current();
        if (!cancelled) {
          setState({ status: "ready", data: result, error: "" });
        }
      } catch (error) {
        if (!cancelled) {
          setState({
            status: "error",
            data: null,
            error: error instanceof Error ? error.message : "unknown_error",
          });
        }
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [dependencyKey]);

  return state;
}

export function PageShell({
  eyebrow,
  title,
  description,
  actions,
  children,
}: {
  eyebrow: string;
  title: string;
  description: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <main style={shellStyle}>
      <div style={containerStyle}>
        <section style={heroStyle}>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 16, justifyContent: "space-between", alignItems: "flex-start" }}>
            <div style={{ maxWidth: 840 }}>
              <div style={labelStyle}>{eyebrow}</div>
              <h1 style={titleStyle}>{title}</h1>
              <p style={{ ...mutedStyle, marginTop: 16, maxWidth: 780 }}>{description}</p>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>{actions}</div>
          </div>
        </section>
        <div style={{ marginTop: 20, display: "grid", gap: 20 }}>{children}</div>
      </div>
    </main>
  );
}

export function SectionHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description: string;
}) {
  return (
    <div style={{ marginBottom: 18 }}>
      <div style={labelStyle}>{eyebrow}</div>
      <h2 style={{ ...titleStyle, fontSize: 26 }}>{title}</h2>
      <p style={{ ...mutedStyle, marginTop: 10, maxWidth: 820 }}>{description}</p>
    </div>
  );
}

export function Notice({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "error" }) {
  return (
    <div
      style={{
        ...cardStyle,
        color: tone === "error" ? "#fecaca" : "#dbeafe",
        borderColor: tone === "error" ? "rgba(248,113,113,0.28)" : "rgba(56,189,248,0.18)",
      }}
    >
      {children}
    </div>
  );
}

export function MiniCard({ title, value }: { title: string; value: string }) {
  return (
    <div style={cardStyle}>
      <div style={labelStyle}>{title}</div>
      <div style={{ marginTop: 10, fontSize: 20, fontWeight: 700, color: "#f8fafc" }}>{value}</div>
    </div>
  );
}

export function MetricPanel({ title, items }: { title: string; items: Array<[string, string]> }) {
  return (
    <div style={cardStyle}>
      <div style={{ color: "#f8fafc", fontSize: 18, fontWeight: 700 }}>{title}</div>
      <div style={{ display: "grid", gap: 10, marginTop: 16 }}>
        {items.map(([label, value]) => (
          <div key={label} style={{ display: "flex", justifyContent: "space-between", gap: 12, borderTop: "1px solid rgba(148, 163, 184, 0.12)", paddingTop: 10 }}>
            <div style={{ color: "#94a3b8", fontSize: 13, letterSpacing: "0.06em", textTransform: "uppercase" }}>{label}</div>
            <div style={{ color: "#f8fafc", textAlign: "right" }}>{value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function JsonCard({ title, data }: { title: string; data: unknown }) {
  return (
    <div style={cardStyle}>
      <div style={{ color: "#f8fafc", fontSize: 18, fontWeight: 700 }}>{title}</div>
      <pre style={codeStyle}>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}

export function ActionLink({ href, label, external = false }: { href: string; label: string; external?: boolean }) {
  if (external) {
    return (
      <a href={href} target="_blank" rel="noreferrer" style={linkStyle}>
        {label}
      </a>
    );
  }
  return (
    <Link href={href} style={linkStyle}>
      {label}
    </Link>
  );
}

export function LabelBlock({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label style={{ display: "grid", gap: 8 }}>
      <span style={labelStyle}>{label}</span>
      {children}
    </label>
  );
}

export function KeyRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", gap: 12, borderTop: "1px solid rgba(148, 163, 184, 0.12)", paddingTop: 10 }}>
      <div style={{ color: "#94a3b8", fontSize: 13, letterSpacing: "0.06em", textTransform: "uppercase" }}>{label}</div>
      <div style={{ color: "#f8fafc", textAlign: "right" }}>{value}</div>
    </div>
  );
}

export function Pill({ label, tone = "neutral" }: { label: string; tone?: "neutral" | "warning" | "info" }) {
  const tones: Record<string, CSSProperties> = {
    neutral: { background: "rgba(15,23,42,0.88)", color: "#dbeafe", borderColor: "rgba(148,163,184,0.18)" },
    warning: { background: "rgba(251,191,36,0.16)", color: "#fde68a", borderColor: "rgba(251,191,36,0.24)" },
    info: { background: "rgba(14,165,233,0.14)", color: "#dbeafe", borderColor: "rgba(56,189,248,0.22)" },
  };
  return <span style={{ ...pillStyle, ...tones[tone] }}>{label}</span>;
}

export function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
}

export function joinList(value: unknown) {
  if (!Array.isArray(value) || !value.length) {
    return "-";
  }
  return value.map((item) => String(item)).join(", ");
}

export function stringValue(value: unknown, fallback = "-") {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  return String(value);
}

export function numberString(value: unknown) {
  if (typeof value === "number") {
    return value.toFixed(2);
  }
  return stringValue(value);
}
