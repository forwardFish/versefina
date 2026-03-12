import { env } from "@/env";

interface AgentSnapshot {
  agent_id: string;
  equity: number;
  cash: number;
}

export default async function AgentPage({
  params,
}: {
  params: Promise<{ agentId: string }>;
}) {
  const { agentId } = await params;
  const response = await fetch(`${env.apiBaseUrl}/api/v1/agents/${agentId}/snapshot`, { cache: "no-store" });
  const data = (await response.json()) as AgentSnapshot;

  return (
    <div>
      <h1 className="mb-4 text-2xl font-bold">Agent: {agentId}</h1>
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-lg border p-4">
          <div className="text-gray-500">总资产</div>
          <div className="text-2xl font-bold">¥{data.equity.toLocaleString()}</div>
        </div>
        <div className="rounded-lg border p-4">
          <div className="text-gray-500">现金</div>
          <div className="text-2xl font-bold">¥{data.cash.toLocaleString()}</div>
        </div>
      </div>
    </div>
  );
}
