"use client";

import React from "react";

import type { ReplayPayload } from "./types";
import {
  cardStyle,
  dayLabel,
  formatCurrency,
  mutedStyle,
  primaryButtonStyle,
  softButtonStyle,
  stringValue,
  summarizeDayNarrative,
} from "./workbenchShared";

type ReplayTimelineProps = {
  replay: ReplayPayload;
  selectedRoundId: string | null;
  onSelectRound: (roundId: string) => void;
  onContinueDay: () => void;
  onJumpToFirstDay: () => void;
  onTogglePlayback: () => void;
  isPlaying: boolean;
  isContinuing: boolean;
  sticky?: boolean;
  variant?: "full" | "compact";
};

export function ReplayTimeline({
  replay,
  selectedRoundId,
  onSelectRound,
  onContinueDay,
  onJumpToFirstDay,
  onTogglePlayback,
  isPlaying,
  isContinuing,
  sticky = false,
  variant = "full",
}: ReplayTimelineProps) {
  const rounds = replay.rounds ?? [];
  const activeRound = rounds.find((round) => round.round_id === selectedRoundId) ?? rounds[0] ?? null;

  if (variant === "compact") {
    return (
      <section
        style={{
          ...cardStyle,
          padding: 14,
          display: "grid",
          gap: 12,
          position: sticky ? "sticky" : "static",
          top: sticky ? 12 : undefined,
          zIndex: sticky ? 30 : undefined,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
          <div style={{ display: "grid", gap: 4 }}>
            <div style={{ fontSize: 12, letterSpacing: "0.12em", textTransform: "uppercase", color: "#64748b", fontWeight: 700 }}>
              多日时间线
            </div>
            <div style={{ fontSize: 18, fontWeight: 800, color: "#0f172a" }}>按天切换当前图谱</div>
            <div style={{ ...mutedStyle, fontSize: 13 }}>
              {activeRound ? `${dayLabel(activeRound.day_index)} / ${stringValue(activeRound.trade_date)}` : "尚未生成交易日"}
            </div>
          </div>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap", justifyContent: "flex-end" }}>
            <button type="button" onClick={onJumpToFirstDay} style={softButtonStyle}>
              回到第1天
            </button>
            <button type="button" onClick={onTogglePlayback} style={isPlaying ? primaryButtonStyle : softButtonStyle}>
              {isPlaying ? "暂停每日演化" : "播放每日演化"}
            </button>
            <button
              type="button"
              onClick={onContinueDay}
              style={primaryButtonStyle}
              disabled={isContinuing || replay.can_continue === false}
            >
              {isContinuing ? "正在推演..." : "继续推演下一交易日"}
            </button>
          </div>
        </div>

        <div style={{ display: "flex", gap: 10, overflowX: "auto", paddingBottom: 2 }}>
          {rounds.map((round, index) => {
            const selected = selectedRoundId ? round.round_id === selectedRoundId : index === 0;
            return (
              <button
                key={round.round_id}
                type="button"
                onClick={() => onSelectRound(round.round_id)}
                data-testid={`round-pill-${round.round_id}`}
                style={{
                  flex: "0 0 auto",
                  minWidth: 140,
                  ...cardStyle,
                  padding: "12px 14px",
                  textAlign: "left",
                  cursor: "pointer",
                  border: selected ? "1px solid rgba(37,99,235,0.34)" : "1px solid rgba(148,163,184,0.18)",
                  background: selected
                    ? "linear-gradient(180deg, rgba(219,234,254,0.96), rgba(239,246,255,0.98))"
                    : "rgba(255,255,255,0.94)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", gap: 8, alignItems: "center" }}>
                  <div style={{ fontSize: 12, color: "#0f172a", fontWeight: 800 }}>
                    {dayLabel(round.day_index, `第${index + 1}天`)}
                  </div>
                  <div style={{ display: "flex", gap: 4, flexWrap: "wrap", justifyContent: "flex-end" }}>
                    {round.is_incremental_generated ? <Tag text="增量" tone="blue" /> : null}
                    {round.turning_point ? <Tag text="拐点" tone="orange" /> : null}
                  </div>
                </div>
                <div style={{ ...mutedStyle, marginTop: 6, fontSize: 12 }}>{stringValue(round.trade_date, round.round_id)}</div>
                <div style={{ marginTop: 8, display: "flex", gap: 8, flexWrap: "wrap", color: "#0f172a", fontSize: 12, fontWeight: 700 }}>
                  <span>动作 {round.actions_count ?? round.participant_actions.length}</span>
                  <span>买 {round.buy_clone_count ?? 0}</span>
                  <span>卖 {round.sell_clone_count ?? 0}</span>
                </div>
              </button>
            );
          })}
        </div>
      </section>
    );
  }

  return (
    <section
      style={{
        ...cardStyle,
        padding: 18,
        display: "grid",
        gap: 16,
        position: sticky ? "sticky" : "static",
        top: sticky ? 12 : undefined,
        zIndex: sticky ? 30 : undefined,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 14, flexWrap: "wrap", alignItems: "center" }}>
        <div style={{ maxWidth: 880 }}>
          <div style={{ fontSize: 12, letterSpacing: "0.12em", textTransform: "uppercase", color: "#64748b", fontWeight: 700 }}>
            多日时间线
          </div>
          <div style={{ fontSize: 24, fontWeight: 800, color: "#0f172a", marginTop: 8 }}>按交易日切换 Agent 演化</div>
          <div style={{ ...mutedStyle, marginTop: 8 }}>{summarizeDayNarrative(activeRound)}</div>
        </div>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap", justifyContent: "flex-end" }}>
          <button type="button" onClick={onJumpToFirstDay} style={softButtonStyle}>
            回到第1天
          </button>
          <button type="button" onClick={onTogglePlayback} style={isPlaying ? primaryButtonStyle : softButtonStyle}>
            {isPlaying ? "暂停每日演化" : "播放每日演化"}
          </button>
          <button
            type="button"
            onClick={onContinueDay}
            style={primaryButtonStyle}
            disabled={isContinuing || replay.can_continue === false}
          >
            {isContinuing ? "正在推演..." : "继续推演下一交易日"}
          </button>
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
        <div style={{ ...mutedStyle, fontSize: 13 }}>
          已生成 {rounds.length} 天，默认起始 {stringValue(replay.default_day_count, "5")} 天。
        </div>
        <div style={{ ...mutedStyle, fontSize: 13 }}>
          {activeRound ? `${dayLabel(activeRound.day_index)} / ${stringValue(activeRound.trade_date)}` : "尚未生成交易日"}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
        {rounds.map((round, index) => {
          const selected = selectedRoundId ? round.round_id === selectedRoundId : index === 0;
          const buyCount =
            round.buy_clone_count ??
            round.participant_actions.filter((action) => String(action.order_side ?? "").toLowerCase() === "buy").length;
          const sellCount =
            round.sell_clone_count ??
            round.participant_actions.filter((action) => String(action.order_side ?? "").toLowerCase() === "sell").length;
          return (
            <button
              key={round.round_id}
              type="button"
              onClick={() => onSelectRound(round.round_id)}
              data-testid={`round-pill-${round.round_id}`}
              style={{
                ...cardStyle,
                padding: 14,
                textAlign: "left",
                cursor: "pointer",
                border: selected ? "1px solid rgba(37,99,235,0.34)" : "1px solid rgba(148,163,184,0.18)",
                background: selected
                  ? "linear-gradient(180deg, rgba(219,234,254,0.96), rgba(239,246,255,0.98))"
                  : "rgba(255,255,255,0.94)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
                <div style={{ fontSize: 11, color: "#64748b", letterSpacing: "0.08em", textTransform: "uppercase", fontWeight: 700 }}>
                  {dayLabel(round.day_index, `第${index + 1}天`)}
                </div>
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap", justifyContent: "flex-end" }}>
                  {round.is_incremental_generated ? <Tag text="增量" tone="blue" /> : null}
                  {round.turning_point ? <Tag text="拐点" tone="orange" /> : null}
                </div>
              </div>
              <div style={{ marginTop: 8, fontSize: 16, fontWeight: 800, color: "#0f172a" }}>{stringValue(round.trade_date, round.round_id)}</div>
              <div style={{ ...mutedStyle, marginTop: 6 }}>{stringValue(round.focus)}</div>
              <div style={{ display: "grid", gap: 6, marginTop: 12, color: "#0f172a", fontWeight: 700, fontSize: 12 }}>
                <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                  <span>动作 {round.actions_count ?? round.participant_actions.length}</span>
                  <span>买入 {buyCount}</span>
                  <span>卖出 {sellCount}</span>
                </div>
                <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                  <span>新进 {round.new_entry_clone_count ?? 0}</span>
                  <span>退出 {round.exit_clone_count ?? 0}</span>
                </div>
              </div>
              <div style={{ ...mutedStyle, marginTop: 10, fontSize: 12 }}>
                市场状态 {stringValue(round.market_state?.state, "未知")} / 净流量 {formatCurrency(round.market_state?.net_flow)}
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}

function Tag({ text, tone }: { text: string; tone: "blue" | "orange" }) {
  const palette =
    tone === "orange"
      ? {
          color: "#c2410c",
          background: "rgba(255,237,213,0.92)",
          border: "1px solid rgba(249,115,22,0.24)",
        }
      : {
          color: "#1d4ed8",
          background: "rgba(219,234,254,0.92)",
          border: "1px solid rgba(59,130,246,0.24)",
        };
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        borderRadius: 999,
        padding: "4px 8px",
        fontSize: 11,
        fontWeight: 800,
        letterSpacing: "0.06em",
        textTransform: "uppercase",
        ...palette,
      }}
    >
      {text}
    </span>
  );
}
