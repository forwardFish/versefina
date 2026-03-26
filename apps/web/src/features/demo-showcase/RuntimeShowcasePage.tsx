"use client";

import { useEffect, useState } from "react";

import { DemoShowcaseView } from "./DemoShowcaseView";
import type { RuntimeShowcasePayload } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8001";
const DASHBOARD_BASE_URL = process.env.NEXT_PUBLIC_DASHBOARD_BASE_URL ?? "http://127.0.0.1:8010";

export function RuntimeShowcasePage() {
  const [payload, setPayload] = useState<RuntimeShowcasePayload | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState<string>("");

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setStatus("loading");
      setErrorMessage("");
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/demo/runtime-showcase`, {
          cache: "no-store",
        });
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const json = (await response.json()) as RuntimeShowcasePayload;
        if (!cancelled) {
          setPayload(json);
          setStatus("ready");
        }
      } catch (error) {
        if (!cancelled) {
          setStatus("error");
          setErrorMessage(error instanceof Error ? error.message : "unknown_error");
        }
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <DemoShowcaseView
      apiBaseUrl={API_BASE_URL}
      dashboardBaseUrl={DASHBOARD_BASE_URL}
      payload={payload}
      status={status}
      errorMessage={errorMessage}
    />
  );
}
