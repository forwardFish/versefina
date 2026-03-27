import type { Metadata } from "next";

import { EventSandboxParticipantScreen } from "@/features/event-sandbox/ParticipantScreen";

export const metadata: Metadata = {
  title: "参与者详情",
  description: "查看单个金融 Agent 的逐轮动作、受影响路径和输出影响路径。",
};

export default async function EventSandboxParticipantPage({
  params,
}: {
  params: Promise<{ eventId: string; participantId: string }>;
}) {
  const { eventId, participantId } = await params;
  return <EventSandboxParticipantScreen eventId={eventId} participantId={participantId} />;
}
