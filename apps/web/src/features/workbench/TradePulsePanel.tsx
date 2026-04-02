"use client";

import React, { useMemo } from "react";

import type { GenericRecord, ParticipantRecord, TradeCard, TradePulsePayload } from "./types";
import {
  actionLabel,
  cardStyle,
  cloneAlias,
  dayLabel,
  familyLabel,
  formatCurrency,
  formatShares,
  formatSignedCurrency,
  formatSignedShares,
  metricTileStyle,
  mutedStyle,
  orderSideLabel,
  stringValue,
  subtleCardStyle,
  toNumber,
} from "./workbenchShared";

type TradePulsePanelProps = {
  tradePulse: TradePulsePayload | null;
  marketMetrics: GenericRecord;
  participantsById: Record<string, ParticipantRecord>;
  onSelectTrade: (card: TradeCard) => void;
};

export function TradePulsePanel({ tradePulse, marketMetrics, participantsById, onSelectTrade }: TradePulsePanelProps) {
  const cards = useMemo(() => tradePulse?.trade_cards ?? [], [tradePulse?.trade_cards]);
  const metrics = useMemo(
    () => ({
      netFlow: toNumber(marketMetrics.net_flow),
      buyCloneCount: Math.max(
        toNumber(tradePulse?.buy_clone_count),
        cards.filter((card) => String(card.order_side ?? "").toLowerCase() === "buy").length,
      ),
      sellCloneCount: Math.max(
        toNumber(tradePulse?.sell_clone_count),
        cards.filter((card) => String(card.order_side ?? "").toLowerCase() === "sell").length,
      ),
      newEntryCloneCount: Math.max(toNumber(tradePulse?.new_entry_clone_count), 0),
      exitCloneCount: Math.max(toNumber(tradePulse?.exit_clone_count), 0),
      crowding: toNumber(marketMetrics.crowding_score),
      fragility: toNumber(marketMetrics.fragility_score),
    }),
    [cards, marketMetrics, tradePulse?.buy_clone_count, tradePulse?.exit_clone_count, tradePulse?.new_entry_clone_count, tradePulse?.sell_clone_count],
  );

  return (
    <section style={{ ...cardStyle, padding: 18, display: "grid", gap: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 14, flexWrap: "wrap", alignItems: "center" }}>
        <div>
          <div style={{ fontSize: 12, letterSpacing: "0.12em", textTransform: "uppercase", color: "#64748b", fontWeight: 700 }}>
            当天操作流水
          </div>
          <div style={{ marginTop: 8, fontSize: 24, fontWeight: 800, color: "#0f172a" }}>当天所有 Agent 操作</div>
          <div style={{ ...mutedStyle, marginTop: 8 }}>
            {tradePulse?.market_pulse_summary ?? "当前交易日还没有返回交易与影响摘要。"}
          </div>
        </div>
        <div style={{ ...mutedStyle, fontSize: 13 }}>
          {tradePulse ? `${dayLabel(tradePulse.day_index)} / ${stringValue(tradePulse.trade_date)} / ${stringValue(tradePulse.market_state)}` : "尚未加载当日流水"}
        </div>
      </div>

      <div style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
        <MetricTile label="净流量" value={formatSignedCurrency(metrics.netFlow)} />
        <MetricTile label="买入 Agent" value={String(metrics.buyCloneCount)} />
        <MetricTile label="卖出 Agent" value={String(metrics.sellCloneCount)} />
        <MetricTile label="首次进场" value={String(metrics.newEntryCloneCount)} />
        <MetricTile label="退出/清仓" value={String(metrics.exitCloneCount)} />
        <MetricTile label="拥挤度" value={`${Math.round(metrics.crowding * 100)}%`} />
        <MetricTile label="脆弱度" value={`${Math.round(metrics.fragility * 100)}%`} />
      </div>

      <div style={{ display: "grid", gap: 12 }}>
        {cards.length === 0 ? (
          <div style={{ ...subtleCardStyle, padding: 16, ...mutedStyle }}>这一天还没有记录到 Agent 交易、广播或减仓动作。</div>
        ) : (
          cards.map((card, index) => {
            const participant = participantsById[card.participant_id];
            const quantityDelta = toNumber(card.position_qty_after) - toNumber(card.position_qty_before);
            const positionDelta = toNumber(card.position_after) - toNumber(card.position_before);
            const cashDelta = toNumber(card.cash_after) - toNumber(card.cash_before);
            const symbol = stringValue(card.symbols?.[0], stringValue(card.symbols?.join(" / ")));
            return (
              <button
                key={card.card_id}
                type="button"
                data-testid={`trade-story-${card.participant_id}`}
                onClick={() => onSelectTrade(card)}
                style={{ ...subtleCardStyle, padding: 16, textAlign: "left", cursor: "pointer", display: "grid", gap: 12 }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                  <div style={{ fontSize: 17, fontWeight: 800, color: "#0f172a" }}>{describeTradeStory(card, index + 1)}</div>
                  <div style={{ ...mutedStyle, fontSize: 13 }}>
                    {participant?.capital_bucket ? `${participant.capital_bucket} / ` : ""}
                    {stringValue(card.next_state)}
                  </div>
                </div>

                <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))" }}>
                  <MetricLine label="方向 / 标的" value={`${orderSideLabel(card.order_side)} / ${symbol}`} />
                  <MetricLine label="股数 / 金额" value={`${formatShares(card.trade_quantity)} / ${formatCurrency(card.order_value)}`} />
                  <MetricLine label="持仓股数变化" value={formatSignedShares(quantityDelta)} />
                  <MetricLine label="仓位前后" value={`${formatCurrency(card.position_before)} -> ${formatCurrency(card.position_after)}`} />
                  <MetricLine label="现金前后" value={`${formatCurrency(card.cash_before)} -> ${formatCurrency(card.cash_after)}`} />
                  <MetricLine label="现金变化" value={formatSignedCurrency(cashDelta)} />
                </div>

                <div style={{ display: "flex", gap: 10, flexWrap: "wrap", ...mutedStyle, fontSize: 13 }}>
                  <span>参考价 {formatCurrency(card.reference_price)}</span>
                  <span>手数 {stringValue(card.lot_size, "--")}</span>
                  <span>价格来源 {stringValue(card.reference_price_source, "未标注")}</span>
                  <span>仓位变化 {formatSignedCurrency(positionDelta)}</span>
                </div>
              </button>
            );
          })
        )}
      </div>
    </section>
  );
}

function MetricTile({ label, value }: { label: string; value: string }) {
  return (
    <div style={metricTileStyle}>
      <div style={{ fontSize: 11, letterSpacing: "0.08em", textTransform: "uppercase", color: "#64748b", fontWeight: 700 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 800, color: "#0f172a" }}>{value}</div>
    </div>
  );
}

function MetricLine({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: "grid", gap: 6 }}>
      <div style={{ fontSize: 11, letterSpacing: "0.08em", textTransform: "uppercase", color: "#64748b", fontWeight: 700 }}>{label}</div>
      <div style={{ color: "#0f172a", fontWeight: 700, lineHeight: 1.5 }}>{value}</div>
    </div>
  );
}

function describeTradeStory(card: TradeCard, fallbackIndex: number) {
  const alias = cloneAlias(card.participant_id, fallbackIndex);
  const family = familyLabel(card.participant_family);
  const action = actionLabel(card.action_type);
  const symbol = stringValue(card.symbols?.[0], "事件标的");
  const quantity = formatShares(card.trade_quantity);
  const amount = formatCurrency(card.order_value);
  const direction = orderSideLabel(card.order_side, action);
  const pieces = [`${dayLabel(card.day_index)}`, `${alias}（${family}）${action}`];

  if (direction && direction !== "观望" && !action.includes(direction)) {
    pieces.push(direction);
  }
  pieces.push(symbol);
  if (quantity !== "--") {
    pieces.push(quantity);
  }
  if (amount !== "--") {
    pieces.push(amount);
  }
  return pieces.join(" ");
}
