import type { Metadata } from "next";

import { WorkbenchEntryScreen } from "@/features/workbench/WorkbenchEntryScreen";

export const metadata: Metadata = {
  title: "Versefina Graph-first 工作台",
  description: "导入真实事件，进入类似 MiroFish 的 Graph-first 沙盘工作台。",
};

export default function WorkbenchEntryPage() {
  return <WorkbenchEntryScreen />;
}
