import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import HomePage from "./page";

describe("HomePage", () => {
  it("promotes the event sandbox as the main entry", () => {
    const markup = renderToStaticMarkup(<HomePage />);

    expect(markup).toContain("Open the live event sandbox first");
    expect(markup).toContain("/event-sandbox");
    expect(markup).toContain("Open legacy 1.6 demo");
  });
});
