# E7-004 Delivery

- Scope: participant/scenario weight feedback recommendations
- Routes:
  - `POST /api/v1/statements/{statement_id}/weight-feedback`
  - `GET /api/v1/statements/{statement_id}/weight-feedback`
- Guarantees:
  - emits preview-only participant and scenario weight recommendations
  - blocks direct application when calibration evidence is still insufficient
