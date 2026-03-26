import { EventSandboxParticipantScreen } from "@/features/event-sandbox/ParticipantScreen";

export default async function EventSandboxParticipantPage({
  params,
}: {
  params: Promise<{ eventId: string; participantId: string }>;
}) {
  const { eventId, participantId } = await params;
  return <EventSandboxParticipantScreen eventId={eventId} participantId={participantId} />;
}
