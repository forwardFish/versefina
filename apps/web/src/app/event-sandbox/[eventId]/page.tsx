import type { Metadata } from "next";

import { EventSandboxOverviewScreen } from "@/features/event-sandbox/OverviewScreen";

export const metadata: Metadata = {
  title: "事件沙盘总览",
  description: "查看真实事件的参与者激活、轮次演化、影响传播、市场状态和剧本结论。",
};

export default async function EventSandboxOverviewPage({
  params,
}: {
  params: Promise<{ eventId: string }>;
}) {
  const { eventId } = await params;
  return <EventSandboxOverviewScreen eventId={eventId} />;
}
