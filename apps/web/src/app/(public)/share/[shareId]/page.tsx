import { PublicSharePage } from "@/features/public-share/PublicSharePage";

type SharePageProps = {
  params: Promise<{ shareId: string }>;
};

export default async function SharePage({ params }: SharePageProps) {
  const { shareId } = await params;
  return <PublicSharePage shareId={shareId} />;
}
