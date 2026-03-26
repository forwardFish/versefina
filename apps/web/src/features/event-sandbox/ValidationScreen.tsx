"use client";

import { getApiBaseUrl, getValidation } from "./api";
import type { ValidationPayload } from "./types";
import { ActionLink, JsonCard, Notice, PageShell, SectionHeader, gridTwoStyle, panelStyle, useAsyncPayload } from "./shared";

export function EventSandboxValidationScreen({ eventId }: { eventId: string }) {
  const state = useAsyncPayload<ValidationPayload>(() => getValidation(eventId), [eventId]);

  return (
    <PageShell
      eyebrow="Validation"
      title={`Validation: ${eventId}`}
      description="This page combines report, why, outcomes, and reliability so you can inspect whether the live run is coherent."
      actions={
        <>
          <ActionLink href={`/event-sandbox/${eventId}`} label="Overview" />
          <ActionLink href={`/event-sandbox/${eventId}/replay`} label="Replay" />
          <ActionLink href={`${getApiBaseUrl()}/docs`} label="Swagger" external />
        </>
      }
    >
      {state.status === "loading" ? <Notice>Loading validation...</Notice> : null}
      {state.status === "error" ? <Notice tone="error">{state.error}</Notice> : null}
      {state.data ? (
        <section style={panelStyle}>
          <SectionHeader
            eyebrow="Validation pack"
            title={`Status: ${state.data.status}`}
            description="Validation combines explanation, outcomes, and reliability into one place."
          />
          <div style={gridTwoStyle}>
            <JsonCard title="Report" data={state.data.report} />
            <JsonCard title="Why" data={state.data.why} />
            <JsonCard title="Outcomes" data={state.data.outcomes} />
            <JsonCard title="Reliability" data={state.data.reliability} />
          </div>
        </section>
      ) : null}
    </PageShell>
  );
}
