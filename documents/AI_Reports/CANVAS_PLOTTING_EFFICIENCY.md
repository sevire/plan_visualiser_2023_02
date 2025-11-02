# Canvas Plotting Efficiency Review and Recommendations (Non‑Breaking, Incremental)

Purpose: Review the current canvas plotting logic and recommend practical ways to make rendering more efficient. This report focuses on your TypeScript UI code under ui_src, especially ui_src/plot_visual.ts, and proposes general best practices plus specific, incremental design changes you can adopt without breaking existing behavior.

Summary of current approach (observed)
- Layered canvases in DOM: background, swimlanes, timelines, visual_activities, highlight.
- Full replot on most changes: plot_visual() clears and redraws all canvases each time, except highlight overlay which is drawn separately on the highlight canvas.
- Scale factor recomputed and canvases reinitialized frequently (initialise_canvases called per plot; capture mode uses a special off‑DOM canvas).
- Rendering per object executes immediate draw commands with per‑frame branching on shape type (rectangle, rounded, diamond, bullet, isosceles, text).
- Logging is very verbose in hot paths.

Issues and their impact
1) Full redraw for small changes
   - Redrawing all layers for a small update (e.g., moving one activity) increases CPU usage and can cause visible flicker on slower devices.
2) Frequent reinitialization of canvases
   - Recreating contexts and resizing canvases on every plot triggers extra work and clears the GPU/bitmap memory, reducing throughput.
3) No dirty region tracking
   - Without tracking what changed, you can’t cheaply limit work to the affected bounds, forcing full‑layer redraws.
4) No caching of drawing instructions
   - All shapes are reinterpreted and re‑issued every time. CPU time grows linearly with number of objects per update.
5) Text rendering overhead
   - fillText with dynamic font sizing and no measurement/Path2D caching is relatively expensive.
6) Device pixel ratio (DPR) handling may be inconsistent
   - If not correctly sizing backing store to DPR, text and lines may blur, and scaling can force extra work or reflow.
7) Logging in tight loops
   - console.log in render loops meaningfully slows rendering and floods logs.

Good practices for high‑performance canvas rendering
- Separate static vs dynamic layers
  - Pre‑render unchanging elements (background grid, static timelines) to offscreen buffers or a static DOM canvas and only composite them each frame.
- Use dirty rectangles for dynamic layers
  - Compute minimal bounding boxes for changed objects; only clear and redraw those regions on the target layer.
- Cache draw instructions
  - Precompute Path2D objects for shapes and reuse them; cache measured text width/lines where wrapping is used.
- Avoid unnecessary state churn
  - Minimize changes to context state (fillStyle, font, textAlign). Group draws by style where possible.
- Coalesce updates with requestAnimationFrame (rAF)
  - Batch multiple mutations within a tick and render once per frame at most.
- Respect devicePixelRatio
  - Size canvas width/height = CSS size * DPR, scale context to DPR once; draw at 1:1 logical units thereafter.
- OffscreenCanvas or in‑memory canvas
  - Where supported, render expensive static layers into OffscreenCanvas; fallback to a hidden in‑memory HTMLCanvasElement.
- Spatial indexing for hit testing and selective redraw
  - Keep a map from object id to its last known screen bounds; optionally use a grid or R‑Tree if counts get high (~1000+ objects).

Specific design recommendations for this app
1) Formalize layers and ownership
   - Keep current five layers but define a small CanvasLayerManager to:
     - Hold DOM canvases/contexts and DPR‑safe sizes.
     - Expose markDirty(rect, layer) + render() that only repaints dirty regions on dynamic layers.
     - Provide getContext(layer) for one‑off operations (e.g., highlight overlay).

2) Static vs dynamic split
   - background: static (render once per visual settings change; cached bitmap)
   - swimlanes: mostly static (repaint only when swimlane layout changes)
   - timelines: mostly static (repaint when timeline config changes)
   - visual_activities: dynamic (repaint on add/move/remove)
   - highlight: dynamic overlay (already isolated; keep as is)
   Implementation: prerender static layers to an offscreen buffer and blit with drawImage, or keep as DOM layers that are repainted only when their data changes.

3) Dirty rectangles for visual_activities
   - Maintain a record of last drawn bounds per activity id (logical units pre‑scale).
   - When an activity moves or changes style, compute union of old bounds and new bounds; clear only that rect and redraw just the affected activities intersecting it.
   - For bulk operations (compress/sort/autolayout), prefer a full layer clear once rather than many tiny rects.

4) Cache shape instructions
   - For each component type:
     - Rectangle/Rounded/Bullet/Diamond/Triangle: build a Path2D when layout changes; reuse the same Path2D during redraws.
     - Text: cache computed font string and text metrics/line breaks when either content or scale changes.
   - Store in a per‑object cache: { path: Path2D, fillStyle, strokeStyle, textLayout, bounds }

5) rAF render queue
   - Introduce a small RenderQueue so multiple UI events within a short period schedule a single render pass.
   - The queue aggregates dirty rects and layer flags; on rAF it performs minimal redraws and then clears the queue.

6) Scale/DPR handling
   - Compute scaleFactor from visual settings and CSS size once per resize or settings change.
   - Set canvas.width/height = cssWidth/height * devicePixelRatio; context.scale(devicePixelRatio, devicePixelRatio).
   - Then draw using logical coordinates that match your layout units without repeating the scale factor in every draw call.

7) Reduce logging in hot path
   - Replace console.log in plotting loops with a debug logger guarded by NODE_ENV !== 'production'.

8) Image capture path
   - For export, composite static offscreen + dynamic layer into a single capture canvas. If you already prerendered static layers into offscreen buffers, draw them in z‑order and then the dynamic layer. This avoids replaying all instructions just for export.

Concrete incremental plan
- Step 0: Keep behavior identical; no URL or API changes.
- Step 1: Extract a CanvasLayerManager scaffold
  - Provide init(container, layerIds), sizeTo(containerRect, dpr), getContext(name), clear(name|all). Do not wire into plot_visual yet.
- Step 2: Introduce RenderQueue + DirtyRect utilities
  - Utilities to merge/union rectangles and coalesce work. Not used by plot_visual initially.
- Step 3: Pre‑render static layers (optional, low risk)
  - Add functions to draw background/swimlanes/timelines onto their layers only when their data changes. Call a new drawStaticLayers() from your existing flows that already fetch these data; avoid touching activity rendering for now.
- Step 4: Add per‑activity bounds tracking on the activities layer
  - Track lastDrawnBounds[activityId]. On move or style change, mark union rect dirty and redraw only intersecting objects. For bulk ops, fallback to full clear.
- Step 5: Path2D caching
  - Build and cache Path2D per activity when its geometry changes; reuse in draw.
- Step 6: Switch to DPR‑aware sizing
  - Scale contexts once on init/resize and remove explicit scaleFactor multiplications in draw code gradually.

Design sketch (TypeScript interfaces)
```ts
// ui_src/canvas/layers.ts (scaffold)
export type LayerName = 'background' | 'swimlanes' | 'timelines' | 'visual_activities' | 'highlight';

export interface CanvasLayer {
  name: LayerName;
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
}

export interface CanvasLayerManagerOptions {
  container: HTMLElement;
  layerIds: Record<LayerName, string>; // mapping from name -> DOM id
}

export class CanvasLayerManager {
  private layers: Map<LayerName, CanvasLayer> = new Map();
  private dpr = 1;

  constructor(private opts: CanvasLayerManagerOptions) {}

  init(): this {
    this.dpr = window.devicePixelRatio || 1;
    for (const name of Object.keys(this.opts.layerIds) as LayerName[]) {
      const id = this.opts.layerIds[name];
      const canvas = document.getElementById(id) as HTMLCanvasElement | null;
      if (!canvas) throw new Error(`Missing canvas #${id}`);
      const ctx = canvas.getContext('2d');
      if (!ctx) throw new Error(`No 2D context for #${id}`);
      this.layers.set(name, { name, canvas, ctx });
    }
    this.resize();
    return this;
  }

  resize(): void {
    const rect = this.opts.container.getBoundingClientRect();
    const width = Math.max(1, Math.floor(rect.width));
    const height = Math.max(1, Math.floor(rect.height));
    for (const { canvas, ctx } of this.layers.values()) {
      canvas.width = Math.floor(width * this.dpr);
      canvas.height = Math.floor(height * this.dpr);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0); // scale once
    }
  }

  get(name: LayerName): CanvasRenderingContext2D {
    const layer = this.layers.get(name);
    if (!layer) throw new Error(`Unknown layer ${name}`);
    return layer.ctx;
  }

  clear(name?: LayerName): void {
    if (name) {
      const { canvas, ctx } = this.layers.get(name)!;
      ctx.clearRect(0, 0, canvas.width / this.dpr, canvas.height / this.dpr);
      return;
    }
    for (const { canvas, ctx } of this.layers.values()) {
      ctx.clearRect(0, 0, canvas.width / this.dpr, canvas.height / this.dpr);
    }
  }
}
```

```ts
// ui_src/canvas/dirty.ts (scaffold)
export interface Rect { x: number; y: number; w: number; h: number }
export function union(a: Rect, b: Rect): Rect {
  const x1 = Math.min(a.x, b.x);
  const y1 = Math.min(a.y, b.y);
  const x2 = Math.max(a.x + a.w, b.x + b.w);
  const y2 = Math.max(a.y + a.h, b.y + b.h);
  return { x: x1, y: y1, w: x2 - x1, h: y2 - y1 };
}
export function intersects(a: Rect, b: Rect): boolean {
  return !(a.x > b.x + b.w || a.x + a.w < b.x || a.y > b.y + b.h || a.y + a.h < b.y);
}
export class DirtySet {
  private rects: Rect[] = [];
  mark(r: Rect) { this.rects.push(r); }
  take(): Rect[] {
    const out = this.rects; this.rects = []; return out;
  }
}
```

How this fits your current code
- plot_visual.ts already separates layers in get_canvas_info(). The CanvasLayerManager preserves that design but consolidates sizing and DPR handling, and provides a path to stop passing scaleFactor around.
- You can keep plot_shape as is initially. Later, migrate to Path2D caching and remove repeated scale multipliers after switching to DPR‑scaled contexts.
- Highlight remains an isolated overlay; no changes needed except to obtain the context from the manager when you adopt it.

Migration guidance (low risk)
- Phase A: Adopt CanvasLayerManager for initialization only, still full redraw per change (zero behavior change). Measure baseline FPS/CPU.
- Phase B: Pre‑render static layers when their inputs change and avoid clearing them on activity changes.
- Phase C: Introduce DirtySet for the activities layer only. Update move/add/remove code paths to mark dirty rects; in the render pass clear and redraw only the affected region(s).
- Phase D: Add Path2D/text layout caching for activities to reduce CPU on redraw.
- Phase E: Optional: OffscreenCanvas for static layers and export composition, plus basic spatial index for hit testing if needed at 1000+ activities.

Measurement suggestions
- Use Performance API marks/measure around plot_visual to compare before/after.
- Track counts: number of objects drawn, number of rects cleared per update, time to paint.
- Add a simple FPS meter in dev mode and a query param (?perf=1) to enable verbose metrics.

Potential pitfalls and mitigations
- Over‑fragmented dirty rects: Merge adjacent/overlapping rects or fall back to full clear above a threshold.
- Text blur: Ensure DPR scaling is applied once; avoid fractional transforms that cause blurry text.
- Z‑order consistency: When redrawing only a region, ensure draw order within that region matches global order.
- Bulk operations: For compress/autolayout, full layer redraw is often cheaper than many disjoint rects—detect this and switch strategy.

Conclusion
By formalizing layers, caching, and adopting dirty rectangles and DPR‑aware initialization, you can reduce work per update dramatically while keeping your current architecture and without changing URLs or server responses. The scaffolding provided gives you a safe, incremental path: start with no behavioral changes, then progressively add partial repainting to the activities layer, which is where the biggest wins lie.
