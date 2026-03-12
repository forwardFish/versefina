import { mapAgentSummary } from "@/services/mapper/agent";
import { PageCard } from "@/shared/ui/PageCard";

type AgentObservationProps = {
  agentId: string;
};

export function AgentObservation({ agentId }: AgentObservationProps) {
  const agent = mapAgentSummary(agentId);
  return <PageCard title={`Agent ${agent.agentId}`} description={agent.summary} />;
}
