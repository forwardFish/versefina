# V17-021 Delivery

## Story
- `V17-021`
- `Event Sandbox Input Page`

## Delivered
- `GET /event-sandbox` renders a product-facing input page.
- The page uses the real Versefina API chain through `createEventChain`.
- Submitting one message creates an event, structures it, prepares participants, and runs simulation before redirecting to the event overview.
- Invalid or rejected submissions surface structured feedback on the page.

## Main Files
- `apps/web/src/app/event-sandbox/page.tsx`
- `apps/web/src/features/event-sandbox/EventSandboxInputPage.tsx`
- `apps/web/src/features/event-sandbox/EntryScreen.tsx`
- `apps/web/src/features/event-sandbox/api.ts`
- `apps/web/src/features/event-sandbox/types.ts`
- `apps/web/src/features/event-sandbox/EventSandboxInputPage.test.tsx`

## Validation
- Unit coverage for the page wrapper exists in `EventSandboxInputPage.test.tsx`.
- Manual validation path:
  1. Open `/event-sandbox`
  2. Submit one message
  3. Confirm redirect to `/event-sandbox/{eventId}`
  4. Confirm structured feedback appears for invalid inputs
