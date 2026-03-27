import type {
  CreateEventPayload,
  EventRecordPayload,
  InfluenceGraphPayload,
  ParticipantListPayload,
  ReplayPayload,
  RoundCollectionPayload,
  SimulationSummaryPayload,
  ValidationPayload,
} from "./types";

const API_PROXY_BASE_URL = "/api/event-sandbox";
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
    const message = payload?.error_message ?? `HTTP ${response.status}`;
    throw new Error(message);
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

export async function createEventChain(payload: CreateEventPayload): Promise<{ event_id: string }> {
  const created = await requestJson<{ event_id: string }>("/events", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  await requestJson(`/events/${created.event_id}/structure`, { method: "POST", body: "{}" });
  await requestJson(`/events/${created.event_id}/participants/prepare`, { method: "POST", body: "{}" });
  await requestJson(`/events/${created.event_id}/simulate`, { method: "POST", body: "{}" });
  return created;
}

export function getApiBaseUrl() {
  return DIRECT_API_BASE_URL;
}

export function getEvent(eventId: string) {
  return requestJson<EventRecordPayload>(`/events/${eventId}`);
}

export function getParticipants(eventId: string) {
  return requestJson<ParticipantListPayload>(`/events/${eventId}/participants`);
}

export function getSimulation(eventId: string) {
  return requestJson<SimulationSummaryPayload>(`/events/${eventId}/simulation`);
}

export function getRounds(eventId: string) {
  return requestJson<RoundCollectionPayload>(`/events/${eventId}/simulation/rounds`);
}

export function getReplay(eventId: string) {
  return requestJson<ReplayPayload>(`/events/${eventId}/replay`);
}

export function getInfluenceGraph(eventId: string) {
  return requestJson<InfluenceGraphPayload>(`/events/${eventId}/influence-graph`);
}

export function getBelief(eventId: string) {
  return requestJson<Record<string, unknown>>(`/events/${eventId}/belief`);
}

export function getScenarios(eventId: string) {
  return requestJson<Record<string, unknown>>(`/events/${eventId}/scenarios`);
}

export function getValidation(eventId: string) {
  return requestJson<ValidationPayload>(`/events/${eventId}/validation`);
}

export function getReport(eventId: string) {
  return requestJson<Record<string, unknown>>(`/events/${eventId}/report`);
}
