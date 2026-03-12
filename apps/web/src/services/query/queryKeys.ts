export const queryKeys = {
  rankings: ["rankings"] as const,
  universe: ["universe"] as const,
  agentSnapshot: (agentId: string) => ["agent", agentId, "snapshot"] as const,
};
