import type { Metadata } from "next";

import { EventWorkbenchScreen } from "@/features/workbench/EventWorkbenchScreen";

export const metadata: Metadata = {
  title: "Versefina Graph-first 事件工作台",
  description: "查看单事件的图谱主舞台、双栏观察态和互动工作台。",
};

export default async function WorkbenchEventPage({
  params,
  searchParams,
}: {
  params: Promise<{ eventId: string }>;
  searchParams: Promise<{ round?: string }>;
}) {
  const { eventId } = await params;
  const resolvedSearchParams = await searchParams;
  return <EventWorkbenchScreen eventId={eventId} initialRoundId={resolvedSearchParams.round ?? null} />;
}
