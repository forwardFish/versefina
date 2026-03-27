import type { Metadata } from "next";

import { EventSandboxReplayScreen } from "@/features/event-sandbox/ReplayScreen";

export const metadata: Metadata = {
  title: "事件回放",
  description: "按轮次回放真实事件演化过程，查看动作、状态和传播变化。",
};

export default async function EventSandboxReplayPage({
  params,
}: {
  params: Promise<{ eventId: string }>;
}) {
  const { eventId } = await params;
  return <EventSandboxReplayScreen eventId={eventId} />;
}
