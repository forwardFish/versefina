export type TradeLogItem = {
  symbol: string;
  side: string;
  quantity: string;
};

export const tradeLogStub: TradeLogItem[] = [{ symbol: "600519.SH", side: "BUY", quantity: "100" }];
