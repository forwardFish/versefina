import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import HomePage from "./page";

describe("HomePage", () => {
  it("promotes the workbench as the main entry", () => {
    const markup = renderToStaticMarkup(<HomePage />);

    expect(markup).toContain("打开 Graph-first 事件沙盘工作台");
    expect(markup).toContain("/workbench");
    expect(markup).toContain("打开旧入口兼容页");
  });
});
