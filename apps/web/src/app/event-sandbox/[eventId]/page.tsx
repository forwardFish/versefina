import { EventSandboxOverviewScreen } from "@/features/event-sandbox/OverviewScreen";

export default async function EventSandboxOverviewPage({
  params,
}: {
  params: Promise<{ eventId: string }>;
}) {
  const { eventId } = await params;
  return <EventSandboxOverviewScreen eventId={eventId} />;
}
