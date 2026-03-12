import type { ReactNode } from "react";

import { dashboardNav } from "@/shared/constants/nav";

export function DashboardShell({ children }: { children: ReactNode }) {
  return (
    <div>
      <aside>
        <strong>Versefina</strong>
        <ul>
          {dashboardNav.map((item) => (
            <li key={item.href}>{item.label}</li>
          ))}
        </ul>
      </aside>
      <main>{children}</main>
    </div>
  );
}
