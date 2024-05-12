
export function plot_visual() {
  console.log("Plotting activity shapes...")
  const canvas_info: { [key: string]: CanvasRenderingContext2D | null } = {
    background: (document.getElementById("background")! as HTMLCanvasElement).getContext("2d"),
    swimlanes: (document.getElementById("swimlanes")! as HTMLCanvasElement).getContext("2d"),
    timelines: (document.getElementById("timelines")! as HTMLCanvasElement).getContext("2d"),
    visual_activities: (document.getElementById("activities")! as HTMLCanvasElement).getContext("2d"),
  }
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
  // Clear canvas before plotting
  for (let key in canvas_info) {
    // Get the context for each canvas
    let ctx = canvas_info[key];

    // Fill the entire canvas
    ctx!.clearRect(0, 0, ctx!.canvas.width, ctx!.canvas.height);
  }
}

