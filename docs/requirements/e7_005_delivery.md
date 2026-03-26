# E7-005 Delivery

- Scope: MVP acceptance pack and migration handoff for roadmap 1.6
- Routes:
  - `POST /api/v1/roadmaps/1.6/acceptance-pack`
  - `GET /api/v1/roadmaps/1.6/acceptance-pack`
- Guarantees:
  - distinguishes P0 and P1 boundaries for the new event-participant-first line
  - records how Sprint 1-7 assets map into the migration path
  - persists a reusable acceptance pack payload that points fresh sessions to `NOW.md`, `STATE.md`, `DECISIONS.md`, and `current_handoff.md`
