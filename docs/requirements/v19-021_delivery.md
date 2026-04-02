# V19-021 Dual Pane Workbench Mode

## Goal
Implement Dual Pane Workbench Mode for roadmap_1_9 so the new graph-first workbench becomes the primary Versefina product center.

## Acceptance
- Dual Pane Workbench Mode is visible and usable in the roadmap_1_9 workbench flow.
- The implementation uses real Versefina payloads and stays fully Chinese for user-visible copy.
- The story remains compatible with existing event-sandbox, replay, validation, and finahunt ingestion flows where relevant.

## Related Files
- apps/web/src/app/workbench/[eventId]/page.tsx
- apps/web/src/features/workbench/EventWorkbenchScreen.tsx
- apps/web/src/features/workbench/workbenchShared.tsx
- docs/requirements/v19-021_delivery.md
