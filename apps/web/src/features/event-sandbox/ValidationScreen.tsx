"use client";

import { getApiBaseUrl, getValidation } from "./api";
import type { ValidationPayload } from "./types";
import { ActionLink, JsonCard, Notice, PageShell, SectionHeader, gridTwoStyle, panelStyle, useAsyncPayload } from "./shared";

export function EventSandboxValidationScreen({ eventId }: { eventId: string }) {
  const state = useAsyncPayload<ValidationPayload>(() => getValidation(eventId), [eventId]);

  return (
    <PageShell
      eyebrow="验证"
      title={`验证结果：${eventId}`}
      description="这里把报告、Why、Outcome 和 Reliability 放到一起，方便你判断这次真实推演是否站得住。"
      actions={
        <>
          <ActionLink href={`/event-sandbox/${eventId}`} label="返回总览" />
          <ActionLink href={`/event-sandbox/${eventId}/replay`} label="查看回放" />
          <ActionLink href={`${getApiBaseUrl()}/docs`} label="打开 Swagger" external />
        </>
      }
    >
      {state.status === "loading" ? <Notice>正在加载验证结果...</Notice> : null}
      {state.status === "error" ? <Notice tone="error">{state.error}</Notice> : null}
      {state.data ? (
        <section style={panelStyle}>
          <SectionHeader
            eyebrow="验证区"
            title={`状态：${state.data.status}`}
            description="验证页把解释、真实结果和可靠性放到同一个位置。"
          />
          <div style={gridTwoStyle}>
            <JsonCard title="报告" data={state.data.report} />
            <JsonCard title="Why" data={state.data.why} />
            <JsonCard title="真实结果" data={state.data.outcomes} />
            <JsonCard title="可靠性" data={state.data.reliability} />
          </div>
        </section>
      ) : null}
    </PageShell>
  );
}
