"use client";

import Link from "next/link";
import React, { useEffect, useMemo, useRef, useState, type CSSProperties, type ReactNode } from "react";

import type { ParticipantActionRecord, RoundSnapshotRecord } from "./types";

export type AsyncState<T> = {
  status: "loading" | "ready" | "error";
  data: T | null;
  error: string;
};

export const WORKBENCH_WINDOWS = [
  "pre_open",
  "open_5m",
  "morning_30m",
  "midday_reprice",
  "afternoon_follow",
  "close_positioning",
];

export const shellStyle: CSSProperties = {
  minHeight: "100vh",
  background:
    "radial-gradient(circle at top left, rgba(14, 165, 233, 0.12), transparent 22%), radial-gradient(circle at top right, rgba(34, 197, 94, 0.10), transparent 24%), linear-gradient(180deg, #f6fbff 0%, #edf4ff 52%, #f7fbff 100%)",
  color: "#0f172a",
  fontFamily: '"Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif',
};

export const containerStyle: CSSProperties = {
  width: "min(1540px, calc(100% - 28px))",
  margin: "0 auto",
  padding: "18px 0 44px",
};

export const surfaceStyle: CSSProperties = {
  borderRadius: 28,
  border: "1px solid rgba(148, 163, 184, 0.22)",
  background: "rgba(255, 255, 255, 0.88)",
  boxShadow: "0 28px 72px rgba(15, 23, 42, 0.08)",
  backdropFilter: "blur(10px)",
};

export const cardStyle: CSSProperties = {
  borderRadius: 22,
  border: "1px solid rgba(148, 163, 184, 0.18)",
  background: "rgba(255, 255, 255, 0.94)",
  boxShadow: "0 10px 24px rgba(15, 23, 42, 0.04)",
};

export const subtleCardStyle: CSSProperties = {
  ...cardStyle,
  background: "rgba(248, 250, 252, 0.96)",
};

export const eyebrowStyle: CSSProperties = {
  fontSize: 12,
  lineHeight: 1,
  letterSpacing: "0.14em",
  textTransform: "uppercase",
  color: "#64748b",
  fontWeight: 700,
};

export const mutedStyle: CSSProperties = {
  color: "#475569",
  fontSize: 14,
  lineHeight: 1.7,
};

export const titleStyle: CSSProperties = {
  color: "#0f172a",
  fontSize: 32,
  lineHeight: 1.08,
  fontWeight: 800,
};

export const actionButtonStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  gap: 8,
  borderRadius: 999,
  padding: "10px 15px",
  border: "1px solid rgba(59, 130, 246, 0.18)",
  background: "rgba(255, 255, 255, 0.88)",
  color: "#0f172a",
  fontWeight: 700,
  textDecoration: "none",
  cursor: "pointer",
};

export const primaryButtonStyle: CSSProperties = {
  ...actionButtonStyle,
  background: "linear-gradient(135deg, rgba(37,99,235,0.14), rgba(16,185,129,0.12))",
  borderColor: "rgba(37, 99, 235, 0.24)",
};

export const softButtonStyle: CSSProperties = {
  ...actionButtonStyle,
  background: "rgba(248, 250, 252, 0.98)",
  borderColor: "rgba(148, 163, 184, 0.2)",
};

export const inputStyle: CSSProperties = {
  width: "100%",
  borderRadius: 18,
  padding: "14px 16px",
  border: "1px solid rgba(148, 163, 184, 0.24)",
  background: "#ffffff",
  color: "#0f172a",
  outline: "none",
  fontSize: 15,
  lineHeight: 1.7,
};

export const gridTwoStyle: CSSProperties = {
  display: "grid",
  gap: 18,
  gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
};

export const gridThreeStyle: CSSProperties = {
  display: "grid",
  gap: 16,
  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
};

export const metricTileStyle: CSSProperties = {
  ...subtleCardStyle,
  padding: "14px 16px",
  display: "grid",
  gap: 8,
};

type FamilyVisualMeta = {
  label: string;
  accent: string;
  background: string;
  border: string;
};

const FAMILY_VISUALS: Record<string, FamilyVisualMeta> = {
  institution_confirmation: {
    label: "机构",
    accent: "#2563eb",
    background: "linear-gradient(180deg, rgba(239,246,255,1), rgba(219,234,254,0.94))",
    border: "rgba(37,99,235,0.24)",
  },
  retail_fast_money: {
    label: "散户",
    accent: "#f97316",
    background: "linear-gradient(180deg, rgba(255,247,237,1), rgba(255,237,213,0.94))",
    border: "rgba(249,115,22,0.24)",
  },
  risk_control: {
    label: "风控",
    accent: "#dc2626",
    background: "linear-gradient(180deg, rgba(254,242,242,1), rgba(254,226,226,0.94))",
    border: "rgba(220,38,38,0.24)",
  },
  quant_risk_budget: {
    label: "风控",
    accent: "#dc2626",
    background: "linear-gradient(180deg, rgba(254,242,242,1), rgba(254,226,226,0.94))",
    border: "rgba(220,38,38,0.24)",
  },
  industry_research: {
    label: "研究",
    accent: "#0f766e",
    background: "linear-gradient(180deg, rgba(240,253,250,1), rgba(204,251,241,0.92))",
    border: "rgba(15,118,110,0.22)",
  },
  policy_research: {
    label: "研究",
    accent: "#64748b",
    background: "linear-gradient(180deg, rgba(248,250,252,1), rgba(226,232,240,0.94))",
    border: "rgba(100,116,139,0.24)",
  },
  media_sentiment: {
    label: "媒体",
    accent: "#db2777",
    background: "linear-gradient(180deg, rgba(253,242,248,1), rgba(252,231,243,0.92))",
    border: "rgba(219,39,119,0.24)",
  },
  supply_chain_channel: {
    label: "渠道",
    accent: "#d97706",
    background: "linear-gradient(180deg, rgba(255,251,235,1), rgba(254,243,199,0.94))",
    border: "rgba(217,119,6,0.24)",
  },
};

export function useAsyncPayload<T>(loader: () => Promise<T>, deps: Array<string | number | null | undefined>) {
  const [state, setState] = useState<AsyncState<T>>({
    status: "loading",
    data: null,
    error: "",
  });
  const dependencyKey = useMemo(() => deps.map((item) => String(item ?? "")).join("::"), [deps]);
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

export function usePlaybackTimeline<T extends { round_id: string }>(
  rounds: T[],
  selectedRoundId: string | null,
  onSelectRound: (roundId: string) => void,
) {
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (!isPlaying || rounds.length === 0 || !selectedRoundId) {
      return;
    }
    const currentIndex = rounds.findIndex((round) => round.round_id === selectedRoundId);
    if (currentIndex < 0 || currentIndex >= rounds.length - 1) {
      setIsPlaying(false);
      return;
    }
    const handle = window.setTimeout(() => {
      onSelectRound(rounds[currentIndex + 1]?.round_id ?? selectedRoundId);
    }, 1200);
    return () => window.clearTimeout(handle);
  }, [isPlaying, onSelectRound, rounds, selectedRoundId]);

  return {
    isPlaying,
    toggle() {
      setIsPlaying((current) => !current);
    },
    stop() {
      setIsPlaying(false);
    },
    jumpToFirst() {
      if (rounds.length) {
        onSelectRound(rounds[0].round_id);
      }
      setIsPlaying(false);
    },
  };
}

export function WorkbenchShell({
  title,
  description,
  actions,
  children,
}: {
  title: string;
  description: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <main style={shellStyle}>
      <div style={containerStyle}>
        <section style={{ ...surfaceStyle, padding: "24px 24px 28px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", flexWrap: "wrap" }}>
            <div style={{ maxWidth: 980 }}>
              <div style={eyebrowStyle}>Versefina 分析工作台</div>
              <h1 style={{ ...titleStyle, marginTop: 10 }}>{title}</h1>
              <p style={{ ...mutedStyle, marginTop: 14, maxWidth: 900 }}>{description}</p>
            </div>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>{actions}</div>
          </div>
        </section>
        <div style={{ marginTop: 18, display: "grid", gap: 18 }}>{children}</div>
      </div>
    </main>
  );
}

export function ActionLink({ href, label, external = false }: { href: string; label: string; external?: boolean }) {
  if (external) {
    return (
      <a href={href} target="_blank" rel="noreferrer" style={softButtonStyle}>
        {label}
      </a>
    );
  }
  return (
    <Link href={href} style={softButtonStyle}>
      {label}
    </Link>
  );
}

export function StatPill({ label, value, tone = "neutral" }: { label: string; value: string; tone?: "neutral" | "bull" | "bear" }) {
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 8,
        padding: "8px 12px",
        borderRadius: 999,
        border:
          tone === "bull"
            ? "1px solid rgba(34,197,94,0.24)"
            : tone === "bear"
              ? "1px solid rgba(239,68,68,0.24)"
              : "1px solid rgba(148, 163, 184, 0.18)",
        background:
          tone === "bull"
            ? "rgba(220,252,231,0.8)"
            : tone === "bear"
              ? "rgba(254,226,226,0.8)"
              : "rgba(255,255,255,0.84)",
      }}
    >
      <span style={{ ...eyebrowStyle, fontSize: 11, letterSpacing: "0.08em" }}>{label}</span>
      <span style={{ fontWeight: 700, color: "#0f172a" }}>{value}</span>
    </div>
  );
}

export function Notice({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "error" }) {
  return (
    <div
      style={{
        ...cardStyle,
        padding: "16px 18px",
        color: tone === "error" ? "#991b1b" : "#0f172a",
        borderColor: tone === "error" ? "rgba(248,113,113,0.28)" : "rgba(148,163,184,0.18)",
      }}
    >
      {children}
    </div>
  );
}

export function formatList(value: unknown, fallback = "无") {
  if (!Array.isArray(value) || value.length === 0) {
    return fallback;
  }
  return value.map((item) => String(item)).join(", ");
}

export function stringValue(value: unknown, fallback = "无") {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  return String(value);
}

export function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
}

export function asArray<T = unknown>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : [];
}

export function readStringList(value: unknown): string[] {
  return asArray(value).map((item) => String(item)).filter((item) => item.trim().length > 0);
}

export function toNumber(value: unknown): number {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string") {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }
  return 0;
}

export function numberValue(value: unknown, fallback = "0.00") {
  const resolved = toNumber(value);
  return Number.isFinite(resolved) ? resolved.toFixed(2) : fallback;
}

export function formatCurrency(value: unknown, fallback = "--") {
  const resolved = toNumber(value);
  if (!Number.isFinite(resolved) || Math.abs(resolved) < 0.0001) {
    return fallback;
  }
  if (Math.abs(resolved) >= 1_000_000_000) {
    return `${(resolved / 1_000_000_000).toFixed(2)}B`;
  }
  if (Math.abs(resolved) >= 1_000_000) {
    return `${(resolved / 1_000_000).toFixed(2)}M`;
  }
  if (Math.abs(resolved) >= 1_000) {
    return `${(resolved / 1_000).toFixed(1)}K`;
  }
  return resolved.toFixed(2);
}

export function formatSignedCurrency(value: unknown, fallback = "--") {
  const resolved = toNumber(value);
  if (!Number.isFinite(resolved) || Math.abs(resolved) < 0.0001) {
    return fallback;
  }
  const prefix = resolved > 0 ? "+" : "";
  return `${prefix}${formatCurrency(resolved, fallback)}`;
}

export function formatPercent(value: unknown, digits = 0, fallback = "--") {
  const resolved = toNumber(value);
  if (!Number.isFinite(resolved)) {
    return fallback;
  }
  return `${(resolved * 100).toFixed(digits)}%`;
}

export function formatPositionBook(value: unknown, fallback = "暂无仓位") {
  const record = asRecord(value);
  const entries = Object.entries(record).filter(([, amount]) => Math.abs(toNumber(amount)) > 0.0001);
  if (entries.length === 0) {
    return fallback;
  }
  return entries.map(([symbol, amount]) => `${symbol}: ${formatCurrency(amount)}`).join(" | ");
}

export function windowLabel(windowId: unknown) {
  const value = String(windowId ?? "").trim();
  if (!value) {
    return "窗口";
  }
  return value.replaceAll("_", " ");
}

export function polarityTone(polarity: unknown): "bull" | "bear" | "neutral" {
  const value = String(polarity ?? "").toLowerCase();
  if (value.includes("bear") || value.includes("sell") || value.includes("reduce") || value.includes("warning")) {
    return "bear";
  }
  if (value.includes("bull") || value.includes("buy") || value.includes("constructive")) {
    return "bull";
  }
  return "neutral";
}

export function polarityColor(polarity: unknown) {
  const tone = polarityTone(polarity);
  if (tone === "bull") {
    return "#15803d";
  }
  if (tone === "bear") {
    return "#dc2626";
  }
  return "#475569";
}

export function edgeTypeColor(edgeType: unknown, polarity: unknown, orderSide?: unknown) {
  const type = String(edgeType ?? "").toLowerCase();
  if (type === "trade") {
    return String(orderSide ?? "").toLowerCase() === "sell" ? "rgba(234, 88, 12, 0.86)" : "rgba(37, 99, 235, 0.86)";
  }
  if (type === "influence") {
    return polarityTone(polarity) === "bear" ? "rgba(220, 38, 38, 0.82)" : "rgba(22, 163, 74, 0.82)";
  }
  return "rgba(100, 116, 139, 0.7)";
}

export function strengthWidth(strength: unknown) {
  return Math.max(1.4, Math.min(4.4, 1.2 + toNumber(strength) * 3.2));
}

export function dayLabel(dayIndex: unknown, fallback = "第?天") {
  const resolved = Math.max(0, Math.round(toNumber(dayIndex)));
  return resolved > 0 ? `第${resolved}天` : fallback;
}

export function familyVisualMeta(family: unknown): FamilyVisualMeta {
  const key = String(family ?? "").trim();
  return (
    FAMILY_VISUALS[key] ?? {
      label: key || "参与者",
      accent: "#475569",
      background: "linear-gradient(180deg, rgba(255,255,255,1), rgba(241,245,249,0.94))",
      border: "rgba(148,163,184,0.24)",
    }
  );
}

export function familyLabel(family: unknown) {
  return familyVisualMeta(family).label;
}

export function cloneAlias(participantId: unknown, fallbackIndex = 0) {
  const raw = String(participantId ?? "").trim();
  const alpha = raw.replace(/[^A-Za-z]/g, "");
  if (alpha) {
    return alpha.slice(0, 1).toUpperCase();
  }
  if (fallbackIndex > 0 && fallbackIndex <= 26) {
    return String.fromCharCode(64 + fallbackIndex);
  }
  return raw.slice(0, 2).toUpperCase() || "?";
}

export function actionLabel(actionName: unknown) {
  const action = String(actionName ?? "").trim().toUpperCase();
  const labels: Record<string, string> = {
    INIT_BUY: "首次买入",
    ADD_BUY: "继续买入",
    REDUCE: "减仓卖出",
    EXIT: "退出卖出",
    BROADCAST_BULL: "看多影响",
    BROADCAST_BEAR: "看空影响",
    VALIDATE: "继续验证",
    WATCH: "继续观察",
    IGNORE: "保持观望",
  };
  return labels[action] ?? (action || "执行动作");
}

export function orderSideLabel(orderSide: unknown, fallback = "观望") {
  const side = String(orderSide ?? "").trim().toLowerCase();
  if (side === "buy") {
    return "买入";
  }
  if (side === "sell") {
    return "卖出";
  }
  return fallback;
}

export function formatShares(quantity: unknown, unit = "股", fallback = "--") {
  const resolved = toNumber(quantity);
  if (!Number.isFinite(resolved) || Math.abs(resolved) < 0.0001) {
    return fallback;
  }
  return `${Math.round(resolved).toLocaleString("zh-CN")} ${unit}`;
}

export function formatSignedShares(quantity: unknown, unit = "股", fallback = "--") {
  const resolved = toNumber(quantity);
  if (!Number.isFinite(resolved) || Math.abs(resolved) < 0.0001) {
    return fallback;
  }
  const prefix = resolved > 0 ? "+" : "";
  return `${prefix}${Math.round(resolved).toLocaleString("zh-CN")} ${unit}`;
}

export function summarizeParticipantAction(action: ParticipantActionRecord, fallbackIndex = 0) {
  const alias = cloneAlias(action.participant_id, fallbackIndex);
  const family = familyLabel(action.participant_family);
  const label = actionLabel(action.action_name ?? action.action_type);
  const quantity = formatShares(action.trade_quantity);
  const amount = formatCurrency(action.order_value);
  if (quantity !== "--" || amount !== "--") {
    return `${alias}（${family}）${label}${quantity !== "--" ? ` ${quantity}` : ""}${amount !== "--" ? ` / ${amount}` : ""}`;
  }
  return `${alias}（${family}）${label}`;
}

export function summarizeDayNarrative(round: RoundSnapshotRecord | null) {
  if (!round) {
    return "当天暂无可展示的演化故事。";
  }
  if (!round.participant_actions.length) {
    return `${dayLabel(round.day_index)}暂无新增交易或影响动作。`;
  }
  const fragments = round.participant_actions
    .slice(0, 4)
    .map((action, index) => summarizeParticipantAction(action, index + 1));
  const suffix = round.participant_actions.length > 4 ? "，其余动作已收起到下方流水。" : "。";
  return `${dayLabel(round.day_index)}：${fragments.join("，")}${suffix}`;
}
