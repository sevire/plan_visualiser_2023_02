# TypeScript UI Code Review and Recommendations

This document reviews the TypeScript application code under `ui_src` and calls out serious issues as well as general recommendations to tighten structure and improve reuse. The guidance aims to be actionable, incremental, and low‑risk.

Scope examined:
- ui_src/index.ts
- ui_src/plan_visualiser_api.ts
- ui_src/manage_visual.ts
- ui_src/manage_swimlanes.ts
- ui_src/manage_timelines.ts
- ui_src/manage_styles.ts
- ui_src/manage_shapes.ts
- ui_src/manage_plan_panel.ts
- ui_src/manage_visual_image.ts
- ui_src/plot_visual.ts
- ui_src/widgets.ts
- ui_src/drawing.ts
- ui_src/shapes.ts


## Top Priority (P1): Correctness, robustness, and API hygiene

1. Global state via `window as any` and function exposure
   - Widespread use of `window` to store and share application state (e.g., `visual_id`, `plan_activity_data`, `visual_activity_data`, `canvas_info`, `selected_activity_id`, `default_swimlane_seq_num`).
   - Functions are attached directly to `window` (index.ts), polluting the global namespace and making runtime coupling implicit and fragile.
   - Risks: hard‑to‑track data flow, name collisions, order‑of‑initialization bugs, reduced testability.
   - Recommendation:
     - Introduce a minimal state module (singleton) that encapsulates app state with typed getters/setters.
     - Export functions from modules and call them from a dedicated bootstrap instead of attaching to `window`.
     - If globals must remain for template bindings, wrap them under a single namespace: `window.App = { get_plan_activity_data, ... }`.

2. Missing error handling and inconsistent HTTP method semantics
   - Most API calls don’t handle errors (no try/catch or `.catch` in async/await flow). Failures will silently break UI state.
   - In `plan_visualiser_api.ts` comments and methods are inconsistent:
     - `compress_swimlane` and `autolayout_swimlane` comments state PUT semantics but they POST.
   - Recommendation:
     - Standardize API helpers to always return a typed result `{ ok, status, data, error }` and handle errors at callsites with toasts or inline messages.
     - Align HTTP methods to server semantics (PUT for idempotent updates, POST for operations).

3. Duplicated and conflicting function names
   - `manage_timelines.ts` exports an `update_swimlane_for_activity_handler` function (lines ~217-231) that duplicates in purpose with `manage_swimlanes.ts.update_swimlane_for_activity_handler` but with different payload shapes.
   - This creates ambiguity and import hazards; only the `manage_swimlanes` version appears to be used in the UI.
   - Recommendation:
     - Remove the duplicate from `manage_timelines.ts` or rename to a timeline‑specific name if actually needed.

4. DOM safety and null checks
   - Widespread use of non‑null assertions (`!`) and assumptions about DOM elements existing. For example: canvases in `plot_visual.ts`, `download_image_button!` in `manage_visual_image.ts`.
   - Risk: runtime exceptions when templates change or load order differs.
   - Recommendation: add guarded retrieval helpers: `getEl('#id')` that throws a descriptive error or no‑ops gracefully; use strict null checks.

5. Canvas context assumptions and repeated reinitialization
   - `plot_visual.ts` reinitializes canvases frequently; null assertions on contexts without guards; capture canvas size is hardcoded (2000x2000) which may distort output.
   - Recommendation:
     - Centralize canvas initialization logic and contexts in a CanvasService; ensure contexts are validated; compute capture canvas height from aspect ratio (avoid hardcoding height).


## High Priority (P2): Structure, reuse, and maintainability

6. Monolithic modules with UI logic + state + side effects
   - `manage_visual.ts` is ~600+ lines combining tree building, event wiring, state management, and mutations.
   - Recommendation: split into smaller modules:
     - PlanTreeView (builds and manages the plan tree DOM)
     - ActivityPanel (renders and updates the activity details panel)
     - ActivityActions (API mutation handlers)
     - Selection/Highlight service (current selection and visual highlighting)

7. API layer consolidation and typing
   - `plan_visualiser_api.ts` duplicates axios setup each call; `base_url` duplicated as `""`; repeated CSRF defaults; unused locals (`ret_response`).
   - Recommendation:
     - Create a single configured axios instance with interceptors in `api/client.ts`.
     - Export typed functions with precise request/response interfaces. Example types: `VisualSettings`, `VisualActivity`, `Swimlane`, `Timeline`.
     - Ensure all functions consistently `await` calls and return data.

8. Widgets and dropdown patterns
   - Two different dropdown patterns exist: a `Dropdown` class and a newer functional pair `createDropdown` + `populateDropdown`.
   - Recommendation: settle on one approach (prefer the smaller functional approach) and remove the unused pattern. Ensure the selection event uses `change` rather than `click` for `<select>`.

9. DRY up repeated refresh logic
   - Many handlers do: mutate -> refetch several resources -> reread visual settings -> plot.
   - Recommendation:
     - Extract a `refreshVisual({ settings?: boolean, plan?: boolean, activities?: boolean })` helper to centralize and de‑duplicate the sequence; include error handling and optional spinners.

10. Magic strings for DOM ids/classes
   - IDs like `#plan-activities`, `#download-image-button`, canvas ids, CSS class names are scattered.
   - Recommendation: create a `dom_ids.ts` constants module or a typed map, and reference constants to reduce typos and ease template changes.


## Medium Priority (P3): Type safety, readability, event semantics

11. Excessive `any` and implicit data shapes
   - Many functions accept/return `any`, especially for activity, swimlane, and API data. This loses compile‑time safety.
   - Recommendation: define interfaces for the core domain objects (PlanActivityData, VisualActivityData, SwimlaneRecord, TimelineRecord, VisualSettings) and use them across the code.

12. Event handling semantics
   - In `widgets.ts`, dropdown uses `click` instead of `change`; in several places event targets are typed loosely or cast without checks.
   - Recommendation: use proper event types and `change` events; narrow types with guards.

13. Console logging noise
   - Extensive console logs across modules overwhelm debugging and leak info to users.
   - Recommendation: introduce a minimal logger utility with levels and enable verbose logs only in development.

14. Naming and clarity
   - Inconsistencies like `unique_id` vs `unique_activity_id`, `swimlane_id` vs `sequence_number` (UI mirrors server confusion). Keep UI naming aligned with clarified API semantics.


## Lower Priority (P4): Performance and UX polish

15. Rendering and reflow
   - After each change, the UI often refetches large payloads and reinitializes canvas. Consider incremental updates or caching where practical.

16. Accessibility and semantics
   - Ensure interactive icons have appropriate ARIA labels/roles where not already set; keyboard navigation for dropdowns and controls.

17. Build and linting
   - Leverage ESLint + Prettier + TypeScript strict mode to catch many issues automatically.


## Suggested Micro‑Refactors (safe to adopt incrementally)

A. Centralized axios client
```ts
// ui_src/api/client.ts
import axios from 'axios';

export const api = axios.create({ baseURL: '' });
api.defaults.xsrfCookieName = 'csrftoken';
api.defaults.xsrfHeaderName = 'X-CSRFTOKEN';

export async function get<T>(url: string) {
  const res = await api.get<T>(url);
  return res.data;
}
// Similar post/put/patch/delete helpers returning data or throwing
```
Then rewrite `plan_visualiser_api.ts` to use `api` helpers and add return types.

B. Introduce a minimal AppState
```ts
// ui_src/state.ts
export interface AppState {
  visualId?: number;
  planActivities: any[];
  visualActivityData: Record<string, any[]>; // shape per canvas
  visualSettings?: { width: number; visual_height: number };
  selectedActivityId?: string;
  defaultSwimlaneSeq?: number;
}
export const state: AppState = { planActivities: [], visualActivityData: {} };
```
Replace `(window as any).xyz` reads/writes with `state.xyz` gradually. Optionally expose `window.App = { state }` for templates.

C. Guarded DOM helpers
```ts
// ui_src/dom.ts
export function getEl<T extends HTMLElement>(selector: string): T {
  const el = document.querySelector(selector) as T | null;
  if (!el) throw new Error(`Missing element: ${selector}`);
  return el;
}
```
Use in places currently using non‑null assertions.

D. Fix dropdown semantics
- In `widgets.ts`, use `change` event for selects; for custom dropdowns keep event on `li` click but ensure ARIA attributes.

E. Remove duplicate update_swimlane_for_activity_handler
- Delete or rename the version in `manage_timelines.ts` to avoid confusion; rely on the swimlane module’s handler.

F. Tighten types for core data
- Add interfaces in `ui_src/types.ts` for activity, visual activity, swimlane, timeline, settings and adopt them in function signatures progressively.

G. Reduce logging
- Create a tiny logger module `log.ts` with `debug/info/warn/error` and guard with `process.env.NODE_ENV`.


## Noted Specifics and Quick Wins

- `index.ts`: remove global attachments or encapsulate under `window.App`. Remove the stray console log in DOMContentLoaded and keep a single bootstrap.
- `plan_visualiser_api.ts`: remove unused locals, unify axios setup, ensure all functions return typed data rather than writing to `window`. Add try/catch and propagate errors.
- `plot_visual.ts`: compute capture canvas height from aspect ratio instead of `2000` hardcode; add guards for contexts; consider layering order explicitly when capturing.
- `manage_visual.ts`: extract ActivityPanel field renderers into a set of small functions; replace repeated sequences (fetch+settings+plot) with a `refreshVisual` helper.
- `widgets.ts`: Prefer the functional dropdown creators; remove or deprecate the `Dropdown` class if unused.
- `manage_plan_panel.ts`: the helper `get_activity` uses a different data key (`activity.activity_id`) vs the rest of the app (`unique_sticky_activity_id`); verify and align.


## Proposed Sequencing

1. Centralize API client and reduce globals via AppState (no UI behavior change). 
2. Add types for core data structures and adopt in API and key modules.
3. Introduce DOM guards and logger utility; clean up excessive logging. 
4. Split `manage_visual.ts` into smaller modules; add `refreshVisual` helper. 
5. Address dropdown/event semantics and remove duplicate functions.

Each step can be applied incrementally and tested on the affected UI flows.
