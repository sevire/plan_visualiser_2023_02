
export function plot_visual() {
  console.log("Plotting activity shapes...")
  const canvas_info: { [key: string]: CanvasRenderingContext2D | null } = {
    background: (document.getElementById("canvas-background")! as HTMLCanvasElement).getContext("2d"),
    swimlanes: (document.getElementById("canvas-swimlanes")! as HTMLCanvasElement).getContext("2d"),
    timelines: (document.getElementById("canvas-timelines")! as HTMLCanvasElement).getContext("2d"),
    visual_activities: (document.getElementById("canvas-activities")! as HTMLCanvasElement).getContext("2d"),
  }
  initialise_canvases(canvas_info)
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
          object_to_render.shape_plot_dims.left,
          object_to_render.shape_plot_dims.top,
          object_to_render.shape_plot_dims.width,
          object_to_render.shape_plot_dims.height
        );
      } else if (object_to_render.shape_type === 'rectangle' && object_to_render.shape_name === 'DIAMOND') {
        context!.beginPath();
        context!.moveTo(object_to_render.shape_plot_dims.left, object_to_render.shape_plot_dims.top);

        // top left edge
        context!.lineTo(object_to_render.shape_plot_dims.left - object_to_render.shape_plot_dims.width / 2, object_to_render.shape_plot_dims.top + object_to_render.shape_plot_dims.height / 2);

        // bottom left edge
        context!.lineTo(object_to_render.shape_plot_dims.left, object_to_render.shape_plot_dims.top + object_to_render.shape_plot_dims.height);

        // bottom right edge
        context!.lineTo(object_to_render.shape_plot_dims.left + object_to_render.shape_plot_dims.width / 2, object_to_render.shape_plot_dims.top + object_to_render.shape_plot_dims.height / 2);

        // closing the path automatically creates
        // the top right edge
        context!.closePath();

        context!.fillStyle = object_to_render.fill_color
        context!.fill();
      } else if (object_to_render.shape_type === 'text') {
        context!.textAlign = object_to_render.shape_plot_dims.text_align
        context!.textBaseline = object_to_render.shape_plot_dims.text_baseline
        context!.fillStyle = object_to_render.fill_color
        context!.fillText(object_to_render.text, object_to_render.shape_plot_dims.x, object_to_render.shape_plot_dims.y)
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
  for (let canvas_id in canvas_info) {
    const canvas_details = canvas_info[canvas_id]
    const canvas = canvas_details!.canvas;
    // Get the canvas element

    // Manage canvas element to maintain aspect ratio
    let aspectRatio = 16 / 9; // Example ratio, change this to your desired ratio
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetWidth / aspectRatio;

    // Set to the size of device window
    canvas.style.width = window.innerWidth + 'px';
    canvas.style.height = window.innerWidth / aspectRatio + 'px';

    // Increase actual size of canvas for retina display
    let dpi = window.devicePixelRatio;
    let style_height = +getComputedStyle(canvas).getPropertyValue("height").slice(0, -2);
    let style_width = +getComputedStyle(canvas).getPropertyValue("width").slice(0, -2);
    canvas.height = style_height * dpi;
    canvas.width = style_width * dpi;
  }
}

