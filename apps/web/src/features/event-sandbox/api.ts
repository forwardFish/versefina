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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8001";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  const payload = (await response.json()) as T & {
    error_code?: string;
    error_message?: string;
  };
  if (!response.ok) {
    const message = payload.error_message ?? `HTTP ${response.status}`;
    throw new Error(message);
  }
  return payload;
}

export async function createEventChain(payload: CreateEventPayload): Promise<{ event_id: string }> {
  const created = await requestJson<{ event_id: string }>("/api/v1/events", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  await requestJson(`/api/v1/events/${created.event_id}/structure`, { method: "POST", body: "{}" });
  await requestJson(`/api/v1/events/${created.event_id}/participants/prepare`, { method: "POST", body: "{}" });
  await requestJson(`/api/v1/events/${created.event_id}/simulate`, { method: "POST", body: "{}" });
  return created;
}

export function getApiBaseUrl() {
  return API_BASE_URL;
}

export function getEvent(eventId: string) {
  return requestJson<EventRecordPayload>(`/api/v1/events/${eventId}`);
}

export function getParticipants(eventId: string) {
  return requestJson<ParticipantListPayload>(`/api/v1/events/${eventId}/participants`);
}

export function getSimulation(eventId: string) {
  return requestJson<SimulationSummaryPayload>(`/api/v1/events/${eventId}/simulation`);
}

export function getRounds(eventId: string) {
  return requestJson<RoundCollectionPayload>(`/api/v1/events/${eventId}/simulation/rounds`);
}

export function getReplay(eventId: string) {
  return requestJson<ReplayPayload>(`/api/v1/events/${eventId}/replay`);
}

export function getInfluenceGraph(eventId: string) {
  return requestJson<InfluenceGraphPayload>(`/api/v1/events/${eventId}/influence-graph`);
}

export function getBelief(eventId: string) {
  return requestJson<Record<string, unknown>>(`/api/v1/events/${eventId}/belief`);
}

export function getScenarios(eventId: string) {
  return requestJson<Record<string, unknown>>(`/api/v1/events/${eventId}/scenarios`);
}

export function getValidation(eventId: string) {
  return requestJson<ValidationPayload>(`/api/v1/events/${eventId}/validation`);
}

export function getReport(eventId: string) {
  return requestJson<Record<string, unknown>>(`/api/v1/events/${eventId}/report`);
}
