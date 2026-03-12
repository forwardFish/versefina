import { PageCard } from "@/shared/ui/PageCard";

type PublicSharePageProps = {
  shareId: string;
};

export function PublicSharePage({ shareId }: PublicSharePageProps) {
  return <PageCard title={`Share ${shareId}`} description="Anonymous public share surface for read-only viewing." />;
}
