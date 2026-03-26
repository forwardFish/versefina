import { EventSandboxReplayScreen } from "@/features/event-sandbox/ReplayScreen";

export default async function EventSandboxReplayPage({
  params,
}: {
  params: Promise<{ eventId: string }>;
}) {
  const { eventId } = await params;
  return <EventSandboxReplayScreen eventId={eventId} />;
}
