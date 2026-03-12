import { env } from "@/env";

interface Position {
  symbol: string;
  qty: number;
  avg_cost: number;
}

interface AgentSnapshot {
  agent_id: string;
  equity: number;
  cash: number;
  status: string;
  tags: string[];
  positions: Position[];
}

export default async function AgentPage({
  params,
}: {
  params: Promise<{ agentId: string }>;
}) {
  const { agentId } = await params;
  const response = await fetch(`${env.apiBaseUrl}/api/v1/agents/${agentId}/snapshot`, {
    cache: "no-store",
  });
  const data = (await response.json()) as AgentSnapshot;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="mb-2 text-2xl font-bold">Agent: {agentId}</h1>
        <p className="text-sm text-gray-500">
          Status: <span className="font-medium text-gray-900">{data.status}</span>
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-lg border p-4">
          <div className="text-sm text-gray-500">Equity</div>
          <div className="text-2xl font-bold">¥{data.equity.toLocaleString()}</div>
        </div>
        <div className="rounded-lg border p-4">
          <div className="text-sm text-gray-500">Cash</div>
          <div className="text-2xl font-bold">¥{data.cash.toLocaleString()}</div>
        </div>
      </div>

      <div className="rounded-lg border p-4">
        <div className="mb-3 flex items-center gap-2">
          <h2 className="text-lg font-semibold">Tags</h2>
          <div className="flex flex-wrap gap-2">
            {data.tags.map((tag) => (
              <span key={tag} className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700">
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-lg border p-4">
        <h2 className="mb-4 text-lg font-semibold">Positions</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead>
              <tr className="border-b text-gray-500">
                <th className="pb-3 pr-4 font-medium">Symbol</th>
                <th className="pb-3 pr-4 font-medium">Quantity</th>
                <th className="pb-3 font-medium">Avg Cost</th>
              </tr>
            </thead>
            <tbody>
              {data.positions.map((position) => (
                <tr key={position.symbol} className="border-b last:border-0">
                  <td className="py-3 pr-4 font-medium text-gray-900">{position.symbol}</td>
                  <td className="py-3 pr-4 text-gray-700">{position.qty.toLocaleString()}</td>
                  <td className="py-3 text-gray-700">¥{position.avg_cost.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
