import type { Metadata } from "next";

import { EventSandboxValidationScreen } from "@/features/event-sandbox/ValidationScreen";

export const metadata: Metadata = {
  title: "事件验证",
  description: "查看真实推演的验证结果，包括报告、Why、Outcome 和可靠性。",
};

export default async function EventSandboxValidationPage({
  params,
}: {
  params: Promise<{ eventId: string }>;
}) {
  const { eventId } = await params;
  return <EventSandboxValidationScreen eventId={eventId} />;
}
