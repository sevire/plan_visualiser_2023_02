
export function plot_visual() {
  // Scale factor is calculated so visual fits to width of available screen
  console.log("Plotting activity shapes...")
  const canvas_info: { [key: string]: CanvasRenderingContext2D | null } = {
    background: (document.getElementById("canvas-background")! as HTMLCanvasElement).getContext("2d"),
    swimlanes: (document.getElementById("canvas-swimlanes")! as HTMLCanvasElement).getContext("2d"),
    timelines: (document.getElementById("canvas-timelines")! as HTMLCanvasElement).getContext("2d"),
    visual_activities: (document.getElementById("canvas-activities")! as HTMLCanvasElement).getContext("2d"),
  }
  const scale_factor = initialise_canvases(canvas_info)
  clear_canvases(canvas_info);

  // There will be a list of plotable objects for different canvases so need to iterate through canvases
  for (let canvas in (window as any).visual_activity_data) {
    const context = canvas_info[canvas];
    const rendered_objects = (window as any).visual_activity_data[canvas]
    // Now iterate through plotables in this canvas
    rendered_objects.forEach((object_to_render: any) => {
      if (object_to_render.shape_type === 'rectangle' && object_to_render.shape_name === 'RECTANGLE') {
        context!.fillStyle = object_to_render.fill_color;
        context!.fillRect(
          object_to_render.shape_plot_dims.left * scale_factor,
          object_to_render.shape_plot_dims.top * scale_factor,
          object_to_render.shape_plot_dims.width * scale_factor,
          object_to_render.shape_plot_dims.height * scale_factor
        );
      } else if (object_to_render.shape_type === 'rectangle' && object_to_render.shape_name === 'DIAMOND') {
        context!.beginPath();
        context!.moveTo(
          object_to_render.shape_plot_dims.left * scale_factor,
          object_to_render.shape_plot_dims.top * scale_factor
        );

        // top left edge
        context!.lineTo(
          (object_to_render.shape_plot_dims.left - object_to_render.shape_plot_dims.width) * scale_factor / 2,
          (object_to_render.shape_plot_dims.top + object_to_render.shape_plot_dims.height) * scale_factor / 2
        );

        // bottom left edge
        context!.lineTo(
          object_to_render.shape_plot_dims.left,
          (object_to_render.shape_plot_dims.top + object_to_render.shape_plot_dims.height) * scale_factor
        );

        // bottom right edge
        context!.lineTo(
          (object_to_render.shape_plot_dims.left + object_to_render.shape_plot_dims.width / 2) * scale_factor,
          (object_to_render.shape_plot_dims.top + object_to_render.shape_plot_dims.height / 2) * scale_factor
        );

        // closing the path automatically creates
        // the top right edge
        context!.closePath();

        context!.fillStyle = object_to_render.fill_color
        context!.fill();
      } else if (object_to_render.shape_type === 'text') {
        context!.textAlign = object_to_render.shape_plot_dims.text_align
        context!.textBaseline = object_to_render.shape_plot_dims.text_baseline
        context!.fillStyle = object_to_render.fill_color
        context!.font = `${Math.ceil(object_to_render.font_size * scale_factor)}px sans-serif`
        console.log(`${object_to_render.font_size} Font = ${context!.font}`)
        context!.fillText(object_to_render.text, object_to_render.shape_plot_dims.x * scale_factor, object_to_render.shape_plot_dims.y * scale_factor)
      }
    });
  }
}

function clear_canvases(canvas_info: { [key: string]: CanvasRenderingContext2D | null }) {
  console.log("Clearing canvases...")
  // Clear canvas before plotting
  for (let key in canvas_info) {
    // Get the context for each canvas
    console.log(`Clearing canvas ${key}`)
    let ctx = canvas_info[key];

    // Fill the entire canvas
    ctx!.clearRect(0, 0, ctx!.canvas.width, ctx!.canvas.height);
  }
}

export function initialise_canvases(canvas_info:{[key: string]: CanvasRenderingContext2D | null}) {
  let scale_factor;
  for (let canvas_id in canvas_info) {
    const canvas_details = canvas_info[canvas_id]
    const canvas = canvas_details!.canvas;

    // Manage canvas element to maintain aspect ratio
    console.log(`canvas.offsetWidth = ${canvas.offsetWidth}`)
    let aspectRatio = 16 / 9; // Example ratio, change this to your desired ratio
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetWidth / aspectRatio;

    // Set to the size of device window
    canvas.style.width = canvas.width + 'px';
    canvas.style.height = canvas.height / aspectRatio + 'px';

    // Increase actual size of canvas for retina display
    let dpi = window.devicePixelRatio;
    let style_height = +getComputedStyle(canvas).getPropertyValue("height").slice(0, -2);
    let style_width = +getComputedStyle(canvas).getPropertyValue("width").slice(0, -2);
    canvas.height = style_height * dpi;
    canvas.width = style_width * dpi;
    console.log(`canvas.width after scaling = ${canvas.width}`)

    const visual_width = (window as any).visual_settings.width;

    if (!scale_factor) {
      // Only need to set first time round - all canvases will be identical dimensions
      scale_factor = canvas.width / visual_width;
      console.log(`Scale factor is ${scale_factor}`)
    }
  }
  return scale_factor || 1;
}

