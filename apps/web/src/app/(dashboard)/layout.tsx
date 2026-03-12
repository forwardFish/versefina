import type { ReactNode } from "react";
import Link from "next/link";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r bg-gray-50 p-4">
        <nav className="space-y-2">
          <Link href="/onboarding" className="block rounded p-2 hover:bg-gray-200">
            接入
          </Link>
          <Link href="/agents/mock_agent_001" className="block rounded p-2 hover:bg-gray-200">
            Mock Agent
          </Link>
          <Link href="/universe" className="block rounded p-2 hover:bg-gray-200">
            宇宙全景
          </Link>
        </nav>
      </aside>
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}
