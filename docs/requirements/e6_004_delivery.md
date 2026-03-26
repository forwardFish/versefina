# E6-004 Delivery

- Scope: archetype seed abstraction from market style embeddings
- Routes:
  - `POST /api/v1/statements/{statement_id}/archetype-seed`
  - `GET /api/v1/statements/{statement_id}/archetype-seed`
- Guarantees:
  - maps style embeddings into reusable archetype names and participant-family seeds
  - emits reaction rules and a participant-profile payload for downstream reuse
  - degrades to a generic balanced seed when style signals are weak
