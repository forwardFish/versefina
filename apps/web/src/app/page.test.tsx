import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import HomePage from "./page";

describe("HomePage", () => {
  it("promotes the event sandbox as the main entry", () => {
    const markup = renderToStaticMarkup(<HomePage />);

    expect(markup).toContain("先打开真实事件沙盘");
    expect(markup).toContain("/event-sandbox");
    expect(markup).toContain("打开旧版 1.6 演示");
  });
});
