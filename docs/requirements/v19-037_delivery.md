# V19-037 Roadmap 1.9 Dashboard Source Switch

## Goal
Implement Roadmap 1.9 Dashboard Source Switch for roadmap_1_9 so the new graph-first workbench becomes the primary Versefina product center.

## Acceptance
- Roadmap 1.9 Dashboard Source Switch is visible and usable in the roadmap_1_9 workbench flow.
- The implementation uses real Versefina payloads and stays fully Chinese for user-visible copy.
- The story remains compatible with existing event-sandbox, replay, validation, and finahunt ingestion flows where relevant.

## Related Files
- apps/api/src/api/query/routes.py
- apps/api/src/domain/workbench/service.py
- apps/api/src/services/container.py
- apps/api/tests/test_workbench_api.py
- docs/requirements/v19-037_delivery.md
