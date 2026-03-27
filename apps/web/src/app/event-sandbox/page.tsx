import type { Metadata } from "next";

import { EventSandboxInputPage } from "@/features/event-sandbox/EventSandboxInputPage";

export const metadata: Metadata = {
  title: "Versefina 事件推演沙盘",
  description: "创建一条真实市场事件，激活金融 Agent 阵列，并进入完整的事件推演时间线。",
};

export default function EventSandboxEntryPage() {
  return <EventSandboxInputPage />;
}
