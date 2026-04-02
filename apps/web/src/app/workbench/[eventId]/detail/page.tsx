import type { Metadata } from "next";

import { WorkbenchDetailScreen } from "@/features/workbench/WorkbenchDetailScreen";

export const metadata: Metadata = {
  title: "Versefina Workbench Detail",
  description: "查看 workbench 的完整详细页面，包括 Agent、交易边、影响边和当天流水。",
};

export default async function WorkbenchDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ eventId: string }>;
  searchParams: Promise<{ round?: string }>;
}) {
  const { eventId } = await params;
  const resolvedSearchParams = await searchParams;
  return <WorkbenchDetailScreen eventId={eventId} initialRoundId={resolvedSearchParams.round ?? null} />;
}
