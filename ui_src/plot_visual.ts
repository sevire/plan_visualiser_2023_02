const HIGHLIGHT_COLOR = 'white';
const HIGHLIGHT_LINE_WIDTH = 5;

function plot_rectangle(context: CanvasRenderingContext2D | null, object_to_render: any, scale_factor: number, highlight_flag: boolean) {
  // if highlight flag is set then we just plot the outline in red to highlight the object.
  let plot_function
  if (highlight_flag) {
    console.log("Highligting...")
    context!.strokeStyle = HIGHLIGHT_COLOR;  // Hard code for now!
    context!.lineWidth = HIGHLIGHT_LINE_WIDTH;
    context!.strokeRect(
      object_to_render.shape_plot_dims.left * scale_factor,
      object_to_render.shape_plot_dims.top * scale_factor,
      object_to_render.shape_plot_dims.width * scale_factor,
      object_to_render.shape_plot_dims.height * scale_factor
    );
  } else {
    context!.fillStyle = object_to_render.fill_color;
    context!.fillRect(
      object_to_render.shape_plot_dims.left * scale_factor,
      object_to_render.shape_plot_dims.top * scale_factor,
      object_to_render.shape_plot_dims.width * scale_factor,
      object_to_render.shape_plot_dims.height * scale_factor
    );
  }
}

function plot_diamond(context: CanvasRenderingContext2D | null, object_to_render: any, scale_factor: number, highlight_flag: boolean) {
  const half_width = object_to_render.shape_plot_dims.width / 2;
  const half_height = object_to_render.shape_plot_dims.height / 2;
  context!.beginPath();
  context!.moveTo(
    (object_to_render.shape_plot_dims.left  + half_width) * scale_factor,
    object_to_render.shape_plot_dims.top * scale_factor
  );

  // top left edge
  context!.lineTo(
    (object_to_render.shape_plot_dims.left) * scale_factor,
    (object_to_render.shape_plot_dims.top + half_height) * scale_factor
  );

  // bottom left edge
  context!.lineTo(
    (object_to_render.shape_plot_dims.left + half_width) * scale_factor,
    (object_to_render.shape_plot_dims.top + object_to_render.shape_plot_dims.height) * scale_factor
  );

  // bottom right edge
  context!.lineTo(
    (object_to_render.shape_plot_dims.left + object_to_render.shape_plot_dims.width) * scale_factor,
    (object_to_render.shape_plot_dims.top + half_height) * scale_factor
  );

  // closing the path automatically creates
  // the top right edge
  context!.closePath();

  if (highlight_flag) {
    context!.strokeStyle = HIGHLIGHT_COLOR;  // Hard code for now!
    context!.lineWidth = HIGHLIGHT_LINE_WIDTH;
    context!.stroke()
  } else {
    context!.fillStyle = object_to_render.fill_color
    context!.fill();
  }
}

function plot_bullet(context: CanvasRenderingContext2D | null, object_to_render: any, scale_factor: number, highlight_flag: boolean) {
  context!.beginPath();

  let cornerRadius = (object_to_render.shape_plot_dims.height / 2) * scale_factor;
  context!.beginPath();

  const left = object_to_render.shape_plot_dims.left * scale_factor
  const top = object_to_render.shape_plot_dims.top * scale_factor
  const width = object_to_render.shape_plot_dims.width * scale_factor
  const height = object_to_render.shape_plot_dims.height * scale_factor

  context!.roundRect(
    left,
    top,
    width,
    height,
    cornerRadius
  )

  context!.closePath();

  if (highlight_flag) {
    context!.strokeStyle = HIGHLIGHT_COLOR;  // Hard code for now!
    context!.lineWidth = HIGHLIGHT_LINE_WIDTH;
    context!.stroke()
  } else {
    context!.fillStyle = object_to_render.fill_color
    context!.fill();
  }
}

function plot_rounded_rectangle(context: CanvasRenderingContext2D | null, object_to_render: any, scale_factor: number, highlight_flag: boolean) {
  let cornerRadius = ((object_to_render.shape_plot_dims.height / 2) * 0.6) * scale_factor;
  context!.beginPath();

  const left = object_to_render.shape_plot_dims.left * scale_factor
  const top = object_to_render.shape_plot_dims.top * scale_factor
  const width = object_to_render.shape_plot_dims.width * scale_factor
  const height = object_to_render.shape_plot_dims.height * scale_factor

  context!.roundRect(
    left,
    top,
    width,
    height,
    cornerRadius
  )

  context!.closePath();

  if (highlight_flag) {
    context!.strokeStyle = HIGHLIGHT_COLOR;  // Hard code for now!
    context!.lineWidth = HIGHLIGHT_LINE_WIDTH;
    context!.stroke()
  } else {
    context!.fillStyle = object_to_render.fill_color
    context!.fill();
  }
}

function plot_isosceles_triangle(context: CanvasRenderingContext2D | null, object_to_render: any, scale_factor: number, highlight_flag: boolean) {
  const left: number = object_to_render.shape_plot_dims.left * scale_factor
  const top: number = object_to_render.shape_plot_dims.top * scale_factor
  const width: number = object_to_render.shape_plot_dims.width * scale_factor
  const height: number = object_to_render.shape_plot_dims.height * scale_factor

  context!.beginPath();

  // Define a start point
  context!.moveTo(left + width / 2, top);

  // Define points
  context!.lineTo(left + width,top + height);
  context!.lineTo(left,top + height);

  context!.closePath();

  if (highlight_flag) {
    context!.strokeStyle = HIGHLIGHT_COLOR;  // Hard code for now!
    context!.lineWidth = HIGHLIGHT_LINE_WIDTH;
    context!.stroke()
  } else {
    context!.fillStyle = object_to_render.fill_color
    context!.fill();
  }
}

function plot_text(context: CanvasRenderingContext2D | null, object_to_render: any, scale_factor: number, highlight_flag: boolean) {
  // Note for text we are ignoring highlight flag as it doesn't mean anything for text so just plot text anyway.
  console.log(`About to plot text for ${object_to_render.text}, textAlign is ${object_to_render.shape_plot_dims.text_align}`)
  console.log(`About to plot text for ${object_to_render.text}, x is ${object_to_render.shape_plot_dims.x}`)
  context!.textAlign = object_to_render.shape_plot_dims.text_align
  context!.textBaseline = object_to_render.shape_plot_dims.text_baseline
  context!.fillStyle = object_to_render.fill_color
  context!.font = `${Math.ceil(object_to_render.font_size * scale_factor)}px sans-serif`
  console.log(`${object_to_render.font_size} Font = ${context!.font}`)
  context!.fillText(object_to_render.text, object_to_render.shape_plot_dims.x * scale_factor, object_to_render.shape_plot_dims.y * scale_factor)
}

function plot_shape(object_to_render: any, context: CanvasRenderingContext2D | null, scale_factor: number, highlight_flag: boolean=false) {
  let action
  if (highlight_flag) action = "HIGHLIGHTING"; else action = "PLOTTING"
  console.log(`${action} shape ${object_to_render.shape_name}, context is ${context}`)
  if (object_to_render.shape_type === 'rectangle' && object_to_render.shape_name === 'RECTANGLE') {
    plot_rectangle(context, object_to_render, scale_factor, highlight_flag);
  } else if (object_to_render.shape_type === 'rectangle' && object_to_render.shape_name === 'DIAMOND') {
    plot_diamond(context, object_to_render, scale_factor, highlight_flag);
  } else if (object_to_render.shape_type === 'rectangle' && object_to_render.shape_name === 'ROUNDED_RECTANGLE') {
    plot_rounded_rectangle(context, object_to_render, scale_factor, highlight_flag);
  } else if (object_to_render.shape_type === 'rectangle' && object_to_render.shape_name === 'BULLET') {
    plot_bullet(context, object_to_render, scale_factor, highlight_flag);
  } else if (object_to_render.shape_type === 'rectangle' && object_to_render.shape_name === 'ISOSCELES') {
    plot_isosceles_triangle(context, object_to_render, scale_factor, highlight_flag);
  } else if (object_to_render.shape_type === 'text') {
    plot_text(context, object_to_render, scale_factor, highlight_flag);
  }
}

function get_canvas_info() {
  const canvas_info: { [key: string]: CanvasRenderingContext2D | null } = {
    background: (document.getElementById("canvas-background")! as HTMLCanvasElement).getContext("2d"),
    swimlanes: (document.getElementById("canvas-swimlanes")! as HTMLCanvasElement).getContext("2d"),
    timelines: (document.getElementById("canvas-timelines")! as HTMLCanvasElement).getContext("2d"),
    visual_activities: (document.getElementById("canvas-activities")! as HTMLCanvasElement).getContext("2d"),
    highlight: (document.getElementById("canvas-highlight")! as HTMLCanvasElement).getContext("2d"),
  }
  return canvas_info;
}

function get_rendered_plotable(plotable_id: string): any {
  // Each plotable object has an id which is unique across all canvasses
  // Iterate through all of them looking for the id we are looking for and return it
  console.log(`Looking for plotable with id ${plotable_id}`)
  let found_object = undefined

  outerLoop: for (let canvas in (window as any).visual_activity_data) {
    console.log(`Looking in canvas ${canvas}...`)
    const plotable_objects_for_canvas = (window as any).visual_activity_data[canvas];
    console.log(plotable_objects_for_canvas)
    for (let i = 0; i < plotable_objects_for_canvas.length; i++) {
      let plotable_object = plotable_objects_for_canvas[i];
      console.log(`Checking plotable_id ${plotable_object}`)
      // When we get to the entry for the passed in plotable_id we plot it as a highlight
      if (plotable_object.plotable_id == plotable_id) {
        console.log("Found plotable")
        console.log(plotable_object)
        found_object = plotable_object;
        break outerLoop;  // this line breaks out of both loops
      }
    }
  }
  return found_object
}

export function highlight_activity(activity_id: string) {
  // Gets plot information for activity shape and just plots outline on top of visual to highlight
  console.log(`Clearing canvas for highlight`)
  clear_canvas("highlight")

  console.log(`Highlighting element ${activity_id}, context is...`)
  const object_to_highlight = get_rendered_plotable(`activity-${activity_id}`)
  console.log(`Found activity to highlight...`)
  console.log(object_to_highlight)

  plot_shape(object_to_highlight, (window as any).canvas_info.highlight, (window as any).scale_factor, true)

}

export function plot_visual() {
  // Scale factor is calculated so visual fits to width of available screen
  console.log("Plotting activity shapes...")
  console.log(`Selected activity id is ${(window as any).selected_activity_id}`)
  clear_canvases();

  // There will be a list of plotable objects for different canvases so need to iterate through canvases
  for (let canvas in (window as any).visual_activity_data) {
    const context = (window as any).canvas_info[canvas];
    const rendered_objects = (window as any).visual_activity_data[canvas]
    // Now iterate through plotables in this canvas
    rendered_objects.forEach((object_to_render: any) => {
      plot_shape(object_to_render, context, (window as any).scale_factor);
      // If this is the current selected element then highlight it
      if (canvas == "visual_activities") {
        // Plotable ids have canvas pre-pended for uniqueness so need to strip it off before checking whethe this
        // is the selected id.
        const activity_id_from_plotable_id = object_to_render.plotable_id.substring(9)
        console.log(`Checking whether this element is selected activity: plotable_id is ${activity_id_from_plotable_id}`)
        if (activity_id_from_plotable_id == (window as any).selected_activity_id) {
          console.log(`Highlighting activity ${object_to_render.plotable_id}`)
          plot_shape(object_to_render, (window as any).canvas_info.highlight, (window as any).scale_factor, true)
        }
      }
    });
  }
}

function clear_canvas(canvas_key: string): void {
  const canvas_ctx = (window as any).canvas_info[canvas_key];
  // Get the context for each canvas
  console.log(`Clearing canvas ${canvas_key}`)

  // Fill the entire canvas
  canvas_ctx!.clearRect(0, 0, canvas_ctx!.canvas.width, canvas_ctx!.canvas.height);
}

function clear_canvases() {
  console.log("Clearing canvases...")
  // Clear canvas before plotting
  for (let key in (window as any).canvas_info) {
    clear_canvas(key)
  }
}

export function initialise_canvases() : [number, any] {
  const canvas_info = get_canvas_info();

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
  return [scale_factor || 1, canvas_info];
}

