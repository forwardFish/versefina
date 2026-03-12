import { describe, expect, it } from "vitest";

import { formatPercent } from "./format";

describe("formatPercent", () => {
  it("returns the input label in scaffold mode", () => {
    expect(formatPercent("+8.2%")).toBe("+8.2%");
  });
});
