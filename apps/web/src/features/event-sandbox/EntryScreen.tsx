"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { createEventChain, getApiBaseUrl } from "./api";
import {
  ActionLink,
  LabelBlock,
  MiniCard,
  Notice,
  PageShell,
  SectionHeader,
  gridThreeStyle,
  inputStyle,
  panelStyle,
  mutedStyle,
} from "./shared";

export function EventSandboxEntryScreen() {
  const router = useRouter();
  const [title, setTitle] = useState("Lithium price shock");
  const [body, setBody] = useState(
    "supply shock drives lithium prices higher across the battery chain and fast money starts chasing upstream names",
  );
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const created = await createEventChain({
        title,
        body,
        source: "manual_text",
      });
      router.push(`/event-sandbox/${created.event_id}`);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "unknown_error");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <PageShell
      eyebrow="Versefina Roadmap 1.7"
      title="Event Sandbox"
      description="Send one market message into the system, trigger structure + participant activation + simulation, and jump straight into the live event sandbox."
      actions={
        <>
          <ActionLink href={`${getApiBaseUrl()}/docs`} label="Open Swagger" external />
          <ActionLink href="http://127.0.0.1:8010/versefina/runtime" label="Open Runtime Audit" external />
          <ActionLink href="/roadmap-1-6-demo" label="Legacy 1.6 Demo" />
        </>
      }
    >
      <section style={panelStyle}>
        <SectionHeader
          eyebrow="Input"
          title="Create a real event and run the chain"
          description="The submit button calls the real API chain: create event, structure event, prepare participants, then run the simulation."
        />
        <form onSubmit={handleSubmit} style={{ display: "grid", gap: 18 }}>
          <LabelBlock label="Event title">
            <input
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              style={inputStyle}
              placeholder="Lithium price shock"
            />
          </LabelBlock>
          <LabelBlock label="Message body">
            <textarea
              value={body}
              onChange={(event) => setBody(event.target.value)}
              style={{ ...inputStyle, minHeight: 180, resize: "vertical" }}
              placeholder="Describe the market message you want to simulate."
            />
          </LabelBlock>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center" }}>
            <button
              type="submit"
              disabled={submitting}
              style={{
                border: "1px solid rgba(56, 189, 248, 0.34)",
                borderRadius: 999,
                padding: "14px 20px",
                background: "rgba(14, 165, 233, 0.16)",
                color: "#e0f2fe",
                fontWeight: 700,
                cursor: submitting ? "wait" : "pointer",
              }}
            >
              {submitting ? "Running real pipeline..." : "Run event sandbox"}
            </button>
            <span style={mutedStyle}>This page does not use mock data. It only reads and writes the live API.</span>
          </div>
          {error ? <Notice tone="error">{error}</Notice> : null}
        </form>
      </section>
      <section style={{ ...panelStyle, marginTop: 20 }}>
        <SectionHeader
          eyebrow="Expected result"
          title="What you will see after submit"
          description="The next page should show the activated participant roster, round-by-round actions, influence edges, belief changes, market state, and the current dominant scenario."
        />
        <div style={gridThreeStyle}>
          <MiniCard title="Participants" value="Activation roster with stance, authority, and trigger basis." />
          <MiniCard title="Rounds" value="Three to five simulation rounds with action logs and state transitions." />
          <MiniCard title="Influence" value="Who moved first, who followed, who de-risked, and why the network changed." />
          <MiniCard title="Belief" value="Consensus, opposition, divergence, and key supporters by round." />
          <MiniCard title="Market state" value="DORMANT to INVALIDATED transitions derived from the live run." />
          <MiniCard title="Scenario" value="Bull / base / bear confidence updates and the current dominant path." />
        </div>
      </section>
    </PageShell>
  );
}
