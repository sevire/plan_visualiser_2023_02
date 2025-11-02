# UI Responsiveness and Client-Side Architecture Plan (Non‑Breaking, Incremental)

Purpose: Provide a concrete path to make the UI responsive, responsive-to-user, and resilient, with immediate client feedback, async persistence, and eventual consistency with the server. This plan is tailored to the current code under ui_src and the visual_main_ui_25.html entry page.

Assumptions and preferences (from you):
- No current server push; open to add one. Prefer something that works well with Django/DRF.
- Optimistic (instant) UX required for: move visual activity, add activity, remove activity, run lane algorithms (sort/compress). Others can wait for server responses.
- On conflicts: show a toast and reconcile to server truth.
- Scale: activities ~20/100/1000; swimlanes ~1/3/10; timelines ~1/2/10; styles ~20/50/200.
- Devices: mostly desktop; shouldn’t break on tablet/mobile. Minimum useful width for canvas ~800px.
- Open to a small state library or a custom lightweight store. Open to typed API client. No OpenAPI schema yet.
- OK to split bundle into feature chunks; modern browsers are target.


## High-level Architecture

1) Client-side cache (authoritative for the session)
- Maintain a normalized in-memory cache of key datasets:
  - planActivities: ordered list by plan order
  - visualActivitiesById: map unique_activity_id -> visual activity properties (position, track, style)
  - swimlanes: ordered by sequence
  - timelines: list and metadata
  - visualSettings: dimensions, options
- Expose typed selectors and mutation methods; decouple DOM updates from raw state writes.
- Keep the cache in sync via:
  - optimistic mutations (apply immediately)
  - async persist via API
  - background revalidation (refetch minimal resources after mutating)
  - server events (when available) to reconcile changes originating elsewhere.

2) Optimistic updates with reconciliation
- For the priority actions:
  - Move activity across swimlanes or tracks: update local state instantly, re-render; fire async PATCH; on failure, show toast and revert local change; on success, optionally revalidate specific entities.
  - Add/remove activities: update local state (+/- entity), re-render; fire async PUT/DELETE; reconcile on server reply (e.g., server assigns placement/track) with a toast if changes differ.
  - Sort/compress swimlane algorithms: update local order/positions locally using deterministic client-side algorithm previews (when feasible), or at least show progress overlay while server runs; reconcile to server layout and toast summary of changes.

3) Event model
- Internal event bus for UI events (selection change, hover, drag start/end, layout recalculated).
- Server event stream (once implemented) to broadcast updates: activity-updated, swimlane-updated, timeline-updated, visual-settings-updated. See server push details below.

4) Rendering
- DOM-driven panels (tables/cards) + Canvas for visual plot.
- Introduce small render controllers that subscribe to slices of state to update only the necessary regions.
- Avoid full re-plots if a single activity changes: allow partial repaints where possible (future optimization).


## Server Push Recommendation (Incremental)

Phase 1: Polling
- Add lightweight polling for visuals that are actively open: every 20–30s hit a cheap endpoint `/api/v1/model/visuals/{id}/delta?since=<ts>` returning a list of changed entity ids and their revision timestamps. If no delta endpoint yet, poll full resources but gate by ETag/If-None-Match.

Phase 2: SSE (Server-Sent Events) with Django/DRF
- SSE is simpler than WebSockets and fits DRF nicely via a small StreamingHttpResponse. Works across proxies/CDNs reasonably well.
- Endpoint: `/api/v1/events/visuals/{id}/stream`
- Payloads (newline-delimited SSE events):
  - event: visual-activity-updated; data: { id, fields, revision }
  - event: swimlane-updated; data: { id, fields, revision }
  - event: timeline-updated; data: { id, fields, revision }
  - event: visual-settings-updated; data: { fields, revision }
- Client consumes via EventSource, updating cache and reconciling if the local optimistic value differs.

Phase 3: WebSockets via Django Channels (optional)
- If you later need bidirectional collaboration, upgrade to Channels. The client event handler layer stays the same; swap the transport.


## Typed API Layer and Error Handling

- Create ui_src/api/client.ts with a configured axios instance and helpers returning typed results:
```ts
import axios from 'axios';
export const api = axios.create({ baseURL: '' });
api.defaults.xsrfCookieName = 'csrftoken';
api.defaults.xsrfHeaderName = 'X-CSRFTOKEN';

export type ApiResult<T> = { ok: true; data: T } | { ok: false; status: number; error: string };

export async function getJson<T>(url: string): Promise<ApiResult<T>> {
  try { const r = await api.get<T>(url); return { ok: true, data: r.data }; }
  catch (e: any) { return { ok: false, status: e?.response?.status ?? 0, error: e?.message ?? 'Network error' }; }
}
// Similarly: postJson, putJson, patchJson, deleteJson
```
- Refactor ui_src/plan_visualiser_api.ts functions to return data instead of mutating window.
- Add domain types in ui_src/types.ts: PlanActivity, VisualActivity, Swimlane, Timeline, VisualSettings.
- Add an axios interceptor (you already have manage_messages.ts) for toasts and optional retry/backoff for transient 5xx.


## Minimal Store and Event Bus (Vanilla TS)

- Introduce ui_src/state/store.ts: a lightweight observable store without external deps.
```ts
// store.ts
export type Listener<T> = (state: T) => void;
export class Store<T extends object> {
  private state: T; private listeners = new Set<Listener<T>>();
  constructor(initial: T) { this.state = initial; }
  get(): Readonly<T> { return this.state; }
  set(partial: Partial<T>) { this.state = { ...this.state, ...partial }; this.emit(); }
  update(updater: (s: T) => T) { this.state = updater(this.state); this.emit(); }
  subscribe(fn: Listener<T>): () => void { this.listeners.add(fn); fn(this.state); return () => this.listeners.delete(fn); }
  private emit() { for (const fn of this.listeners) fn(this.state); }
}
```
- AppState shape (example):
```ts
// app_state.ts
export interface AppState {
  visualId?: number;
  planActivities: PlanActivity[];
  visualActivitiesById: Record<string, VisualActivity>;
  swimlanes: Swimlane[];
  timelines: Timeline[];
  visualSettings?: VisualSettings;
  selectedActivityId?: string;
  lastSyncAt?: number; // epoch ms
}
export const defaultState: AppState = { planActivities: [], visualActivitiesById: {}, swimlanes: [], timelines: [] };
```
- Create one store instance and expose a top-level App singleton (you started this in application/application.ts). Replace window.* globals gradually with store accessors.


## Optimistic Mutation Patterns

- Example: move activity to another swimlane
```ts
async function moveActivity(uniqueId: string, swimlaneId: number) {
  const prev = selectActivity(uniqueId);
  // 1) optimistic local update
  store.update(s => ({ ...s, visualActivitiesById: { ...s.visualActivitiesById, [uniqueId]: { ...s.visualActivitiesById[uniqueId], swimlane_id: swimlaneId } } }));
  // 2) async persist
  const res = await update_visual_activity_swimlane(s.visualId!, uniqueId, swimlaneId);
  // 3) reconcile
  if (!res.ok) {
    toastError(`Failed to move: ${res.status}`);
    // revert
    store.update(s => ({ ...s, visualActivitiesById: { ...s.visualActivitiesById, [uniqueId]: prev } }));
  } else {
    // optional narrow revalidation of the activity or swimlane
    revalidateActivity(uniqueId);
  }
}
```
- Similar for add/remove: update cache, re-render, call PUT/DELETE, revert on failure with toast.
- For compress/sort: either simulate locally (if deterministic and you have enough data), or show progress overlay and then replace the swimlane’s activity order with server response. Always show a toast summarizing changes per your preference.


## Responsive Layout Strategy

- Use Bootstrap grid already present, but refine breakpoints and utility classes around the top control row. For the canvas area:
  - Make the canvas container flex: 1 with min-width: 800px and horizontal scrolling on smaller screens rather than squashing the diagram.
  - Debounce window resize; recompute canvas dimensions based on visualSettings and container width.
  - Provide a “Fit to width” toggle that recalculates scale while maintaining readable text.
- Table/card panels: use CSS clamp for text sizes and `text-overflow: ellipsis` with tooltips for truncated names.
- Virtualize potentially long lists (1000 activities) only when actually needed (lazy adoption):
  - For the plan Activities list, consider simple windowing (render ~50 visible rows) using a small custom implementation to avoid big deps.

Example CSS utilities to add:
```css
/* css/utilities.css */
.canvas-shell { display: flex; min-width: 800px; overflow-x: auto; }
.panel-scroll { max-height: 45vh; overflow: auto; }
@media (max-width: 992px) { /* tablet */
  #top-row-controls .col-4 { flex: 1 1 100%; max-width: 100%; }
}
```


## Rendering Controllers (Separation of Concerns)

- Create small controllers that subscribe to the store and update just their region:
  - PlanTreeController: builds and updates the plan tree; listens to planActivities and selectedActivityId.
  - ActivityPanelController: updates the activity properties table when selection changes.
  - SwimlanePanelController: renders swimlane order and responds to sorting/compress triggers.
  - CanvasController: plots the visual; listens to visualActivitiesById, swimlanes, timelines, visualSettings; offers incremental update APIs.
- These controllers replace implicit coupling via window.* and make testing easier.


## Error Handling, Retry, and Toaster

- Keep the axios message interceptor (manage_messages.ts) to surface toasts.
- Add a retry policy for transient 5xx: 2 retries with exponential backoff (e.g., 200ms, 800ms). Only for idempotent GET/PUT.
- For non-retryable errors (4xx), immediately show a descriptive toast and revert optimistic changes.
- Consider capturing failed mutations in a small queue to allow “Retry” action from the toast for critical operations.


## Testing and Observability

- Unit tests (where you have a harness) for store reducers and mutation helpers.
- Add a debug panel (dev only) that shows the current AppState JSON and lastSyncAt.
- Add structured debug logs behind NODE_ENV check; reduce console noise in production.


## Suggested File/Folder Structure (ui_src)

- api/
  - client.ts (axios instance + helpers)
  - model.ts (typed calls formerly in plan_visualiser_api.ts)
- state/
  - store.ts (lightweight Store)
  - app_state.ts (interfaces + defaults)
  - selectors.ts (derived data helpers)
- controllers/
  - plan_tree_controller.ts
  - activity_panel_controller.ts
  - swimlane_controller.ts
  - canvas_controller.ts
- services/
  - refresh_visual.ts (centralized refresh logic)
  - resize.ts (debounced resize + scale calculations)
  - logger.ts (dev/prod gating)
- ui/
  - dom.ts (safe getters, ids map)
  - widgets.ts (dropdown creation, etc.)
  - css/utilities.css (new utility styles)
- index.ts (bootstrap; expose window.App minimally if templates need it)

This structure is compatible with your current vanilla TS approach and can be adopted gradually.


## Incremental Migration Plan (Low Risk)

1. Centralized API + types (no behavior change)
- Add api/client.ts; refactor plan_visualiser_api.ts to use it and return typed data. Keep existing function names and re-export them to avoid breaking callers.
- Create ui_src/types.ts and adopt in the API layer.

2. Introduce Store and AppState (no behavior change at first)
- Add state/store.ts and app_state.ts. Replace window.* globals in a couple of modules (e.g., swimlanes + timelines) as a pilot.
- Add a tiny window.App bridge only where templates need access, pointing to well-defined functions.

3. Refresh service and DOM guards
- Add services/refresh_visual.ts to centralize refetch-and-replot sequences.
- Add ui/dom.ts guarded getters; remove non-null assertions.

4. Optimistic mutations for the priority actions
- Implement optimistic flows for add, remove, move, and compress/sort swimlane.
- Add toasts on reconcile and failures.

5. Responsiveness pass
- Add css/utilities.css; apply responsive classes in visual_main_ui_25.html where safe.
- Debounced resize + canvas scale behavior.

6. Polling; later SSE
- Start with 20–30s polling of revision timestamps.
- Add SSE endpoint on the backend when ready; wire EventSource in the client behind a feature flag.

7. Performance tuning (as needed)
- Introduce simple list virtualization when activity lists exceed ~300 items.
- Consider partial canvas repaints for single-activity changes.


## Example: Event Contracts

Client ← Server (SSE events):
- visual-activity-updated: { id, swimlane_id, track, enabled, style_id, updated_at }
- swimlane-updated: { id, sequence, title, updated_at }
- timeline-updated: { id, labels, granularity, updated_at }
- visual-settings-updated: { width, height, options, updated_at }

Client → Server (REST):
- Move activity: PATCH /api/v1/model/visuals/activities/{visualId}/{uniqueId}/{swimlaneId}/
- Add activity: PUT /api/v1/model/visuals/activities/{visualId}/{uniqueId}/{swimlaneSeq}/
- Remove activity: DELETE /api/v1/model/visuals/activities/{visualId}/{uniqueId}/
- Compress/Sort swimlane: POST /api/v1/model/visuals/swimlanes/(compress|autolayout)/{visualId}/{swimlaneSeq}/


## What stays the same (non-breaking intent)
- Current URLs and server contracts remain.
- Existing pages continue to bootstrap via visual_main_ui_25.html.
- Functions can continue to be exposed on window during transition, but sourced from the new modules.


## Quick Wins (apply immediately)
- Replace direct window.* state writes with a small App singleton proxy that uses the store internally.
- Centralize axios configuration; add error handling in plan_visualiser_api.ts; return typed results.
- Add a refreshVisual helper to remove repeated get_* + settings + plot sequences.
- Add basic responsiveness CSS utilities and apply max-height scrolling to the top-row panels.


With this plan, you’ll get immediate UI responsiveness improvements (optimistic updates and centralized refresh), a path to real-time reconciliation via SSE, and a modular, typed TypeScript architecture that aligns with your current stack and constraints.