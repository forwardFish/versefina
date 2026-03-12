export type PanoramaCard = {
  title: string;
  value: string;
};

export type PanoramaModel = {
  worldId: string;
  cards: PanoramaCard[];
};

export const panoramaStub: PanoramaModel = {
  worldId: "cn-a",
  cards: [
    { title: "World Tick", value: "T+0" },
    { title: "Read Model", value: "projection-ready" },
  ],
};
