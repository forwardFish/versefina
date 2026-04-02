import { redirect } from "next/navigation";

export default async function LegacyEventSandboxOverviewPage({
  params,
}: {
  params: Promise<{ eventId: string }>;
}) {
  const { eventId } = await params;
  redirect(`/workbench/${eventId}`);
}
