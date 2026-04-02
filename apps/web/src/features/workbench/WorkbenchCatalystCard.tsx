"use client";

import React from "react";

import {
  ActionLink,
  StatPill,
  cardStyle,
  dayLabel,
  formatList,
  mutedStyle,
  stringValue,
} from "./workbenchShared";

export function WorkbenchCatalystCard({
  title,
  summary,
  eventType,
  symbols,
  dayIndex,
  tradeDate,
  detailHref,
}: {
  title: string;
  summary: string;
  eventType: string;
  symbols: unknown;
  dayIndex?: unknown;
  tradeDate?: string;
  detailHref: string;
}) {
  return (
    <section style={{ ...cardStyle, padding: 20, display: "grid", gap: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", flexWrap: "wrap" }}>
        <div style={{ display: "grid", gap: 10, maxWidth: 980 }}>
          <div style={{ fontSize: 12, letterSpacing: "0.12em", textTransform: "uppercase", color: "#64748b", fontWeight: 700 }}>
            事件催化
          </div>
          <div style={{ fontSize: 28, lineHeight: 1.12, fontWeight: 800, color: "#0f172a" }}>{title}</div>
          <div style={{ ...mutedStyle, fontSize: 15 }}>{summary}</div>
        </div>
        <ActionLink href={detailHref} label="查看详细页面" />
      </div>

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
        <StatPill label="事件类型" value={eventType} />
        <StatPill label="关联标的" value={formatList(symbols)} />
        <StatPill label="当前轮次" value={dayLabel(dayIndex, "第1天")} />
        <StatPill label="交易日期" value={stringValue(tradeDate, "--")} />
      </div>

      <div style={{ ...mutedStyle, fontSize: 13 }}>
        首页只保留催化、图谱和轮次。更多 Agent、交易边、影响边和完整流水，请进入详细页面查看。
      </div>
    </section>
  );
}
