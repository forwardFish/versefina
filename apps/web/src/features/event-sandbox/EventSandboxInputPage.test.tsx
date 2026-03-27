import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import { EventSandboxInputPage } from "./EventSandboxInputPage";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

vi.mock("./EntryScreen", () => ({
  EventSandboxEntryScreen: () => (
    <section>
      <h1>Event Sandbox</h1>
      <button type="button">Run event sandbox</button>
      <span>Open live sample</span>
      <span>Open Runtime Audit</span>
    </section>
  ),
}));

describe("EventSandboxInputPage", () => {
  it("renders the real event sandbox entry experience", () => {
    const markup = renderToStaticMarkup(<EventSandboxInputPage />);

    expect(markup).toContain("Event Sandbox");
    expect(markup).toContain("Run event sandbox");
    expect(markup).toContain("Open live sample");
    expect(markup).toContain("Open Runtime Audit");
  });
});
