import { rankingBoardStub } from "@/entities/ranking/model";
import { PageCard } from "@/shared/ui/PageCard";

export function RankingBoard() {
  return (
    <PageCard
      title="Rankings"
      description={`As of ${rankingBoardStub.asOfDay}, ${rankingBoardStub.items.length} agents are listed.`}
    />
  );
}
