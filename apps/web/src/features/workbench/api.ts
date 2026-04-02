"use client";

import type {
  CreateEventPayload,
  DecisionTracePayload,
  EventLineagePayload,
  EventRecordPayload,
  GraphStagePayload,
  ImportFinahuntEventPayload,
  ImportFinahuntEventResponse,
  MarketStateTransitionPayload,
  ParticipantListPayload,
  ReplayPayload,
  SimulationSummaryPayload,
  TradePulsePayload,
  ValidationPayload,
  WorkbenchAskPayload,
  WorkbenchAskResponse,
  WorkbenchReportPayload,
} from "./types";

const API_PROXY_BASE_URL = "/api/workbench";
const DIRECT_API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8001";

async function readJsonResponse<T>(response: Response): Promise<T> {
  const rawText = await response.text();
  const contentType = (response.headers.get("content-type") ?? "").toLowerCase();
  let payload: (T & { error_code?: string; error_message?: string }) | null = null;

  if (rawText) {
    try {
      payload = JSON.parse(rawText) as T & { error_code?: string; error_message?: string };
    } catch {
      const preview = rawText.slice(0, 240).trim() || `HTTP ${response.status}`;
      if (!contentType.includes("json")) {
        throw new Error(`接口返回了非 JSON 响应：${preview}`);
      }
      throw new Error(`接口返回了无效 JSON：${preview}`);
    }
  }

  if (!response.ok) {
    throw new Error(payload?.error_message ?? `HTTP ${response.status}`);
  }
  if (!payload) {
    throw new Error("接口返回了空响应。");
  }
  return payload;
}

async function fetchJson<T>(baseUrl: string, path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    cache: "no-store",
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  return readJsonResponse<T>(response);
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  try {
    return await fetchJson<T>(API_PROXY_BASE_URL, path, init);
  } catch (proxyError) {
    try {
      return await fetchJson<T>(`${DIRECT_API_BASE_URL}/api/v1`, path, init);
    } catch {
      throw proxyError;
    }
  }
}

export function getApiBaseUrl() {
  return DIRECT_API_BASE_URL;
}

export async function createWorkbenchEventChain(payload: CreateEventPayload): Promise<{ event_id: string }> {
  const created = await requestJson<{ event_id: string }>("/events", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  await requestJson(`/events/${created.event_id}/structure`, { method: "POST", body: "{}" });
  await requestJson(`/events/${created.event_id}/participants/prepare`, { method: "POST", body: "{}" });
  await requestJson(`/events/${created.event_id}/simulate`, { method: "POST", body: "{}" });
  return created;
}

export function importEventFromFinahunt(
  payload: ImportFinahuntEventPayload = {},
): Promise<ImportFinahuntEventResponse> {
  return requestJson<ImportFinahuntEventResponse>("/events/from-finahunt", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getEvent(eventId: string) {
  return requestJson<EventRecordPayload>(`/events/${eventId}`);
}

export function getLineage(eventId: string) {
  return requestJson<EventLineagePayload>(`/events/${eventId}/lineage`);
}

export function getParticipants(eventId: string) {
  return requestJson<ParticipantListPayload>(`/events/${eventId}/participants`);
}

export function getSimulation(eventId: string) {
  return requestJson<SimulationSummaryPayload>(`/events/${eventId}/simulation`);
}

export function continueSimulationDay(eventId: string) {
  return requestJson<{
    round_results?: Array<{ round_id?: string }>;
    new_round_results?: Array<{ round_id?: string }>;
    latest_round_result?: { round_id?: string };
    simulation_run?: { round_count?: number };
    replay?: ReplayPayload;
  }>(
    `/events/${eventId}/simulation/continue-day`,
    {
      method: "POST",
      body: "{}",
    },
  );
}

export function getReplay(eventId: string) {
  return requestJson<ReplayPayload>(`/events/${eventId}/replay`);
}

export function getValidation(eventId: string) {
  return requestJson<ValidationPayload>(`/events/${eventId}/validation`);
}

export function getGraphStage(eventId: string) {
  return requestJson<GraphStagePayload>(`/events/${eventId}/graph-stage`);
}

export function getTradePulse(eventId: string, roundId?: string, window?: string) {
  const search = new URLSearchParams();
  if (roundId) search.set("round", roundId);
  if (window) search.set("window", window);
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return requestJson<TradePulsePayload>(`/events/${eventId}/trade-pulse${suffix}`);
}

export function getDecisionTrace(eventId: string, cloneId: string, roundId?: string) {
  const suffix = roundId ? `?round=${encodeURIComponent(roundId)}` : "";
  return requestJson<DecisionTracePayload>(`/events/${eventId}/clones/${encodeURIComponent(cloneId)}/decision-trace${suffix}`);
}

export function getMarketStateTransition(eventId: string, transitionId: string) {
  return requestJson<MarketStateTransitionPayload>(
    `/events/${eventId}/market-state/transitions/${encodeURIComponent(transitionId)}`,
  );
}

export function getWorkbenchReport(eventId: string) {
  return requestJson<WorkbenchReportPayload>(`/events/${eventId}/workbench/report`);
}

export function askWorkbench(eventId: string, payload: WorkbenchAskPayload) {
  return requestJson<WorkbenchAskResponse>(`/events/${eventId}/workbench/ask`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
