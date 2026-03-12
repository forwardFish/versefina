export type RankingItem = {
  agentId: string;
  returnLabel: string;
};

export type RankingBoardModel = {
  asOfDay: string;
  items: RankingItem[];
};

export const rankingBoardStub: RankingBoardModel = {
  asOfDay: "2026-03-12",
  items: [
    { agentId: "alpha-01", returnLabel: "+8.2%" },
    { agentId: "value-02", returnLabel: "+6.4%" },
  ],
};
