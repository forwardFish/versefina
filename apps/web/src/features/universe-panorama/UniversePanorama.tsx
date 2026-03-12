import { panoramaStub } from "@/entities/snapshot/model";
import { PageCard } from "@/shared/ui/PageCard";

export function UniversePanorama() {
  return <PageCard title="Universe Panorama" description={`World ${panoramaStub.worldId} is projection-ready.`} />;
}
