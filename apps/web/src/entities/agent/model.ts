export type AgentSummary = {
  agentId: string;
  worldId: string;
  status: string;
  summary: string;
};

export const agentSummaryStub: AgentSummary = {
  agentId: "alpha-01",
  worldId: "cn-a",
  status: "ACTIVE",
  summary: "Read-only observation scaffold for an agent dashboard.",
};
