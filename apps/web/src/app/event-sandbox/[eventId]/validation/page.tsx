import { EventSandboxValidationScreen } from "@/features/event-sandbox/ValidationScreen";

export default async function EventSandboxValidationPage({
  params,
}: {
  params: Promise<{ eventId: string }>;
}) {
  const { eventId } = await params;
  return <EventSandboxValidationScreen eventId={eventId} />;
}
