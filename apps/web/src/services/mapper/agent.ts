import { agentSummaryStub } from "@/entities/agent/model";

export function mapAgentSummary(agentId: string) {
  return {
    ...agentSummaryStub,
    agentId,
  };
}
