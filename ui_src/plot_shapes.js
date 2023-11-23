const scale_factor = 1.0; // to ensure that visual works on screen (may tweak value)
// Text flow values - correspond exactly to choices in VisualActivity table in Django database
const FLOW_TO_LEFT = "FLOW_TO_LEFT";
const FLOW_TO_RIGHT = "FLOW_TO_RIGHT";
const FLOW_WITHIN_SHAPE = "FLOW_WITHIN_SHAPE";
const FLOW_CLIPPED = "FLOW_CLIPPED";
const FLOW_CENTRE = "FLOW_CENTRE";
function color_to_fill_style(color) {
    const red = color[0];
    const green = color[1];
    const blue = color[2];
    return `rgb(${red}, ${green}, ${blue})`;
}
function set_formatting(plot_data) {
    const fill_color_string = color_to_fill_style(plot_data.shape_format.fill_style.fill_color);
    const line_color_string = color_to_fill_style(plot_data.shape_format.line_style.line_color);
    plot_data.ctx.fillStyle = fill_color_string;
    plot_data.ctx.strokeStyle = line_color_string;
    plot_data.ctx.lineWidth = 1;
}
function plot_rectangle(plot_data) {
    console.log("Plotting rectangle...");
    console.log("left:" + plot_data.shape_data.left + ", top:" + plot_data.shape_data.top);
    console.log("width:" + plot_data.shape_data.width + ", height:" + plot_data.shape_data.height);
    console.log("incoming colour: " + plot_data.shape_format.fill_style.fill_color);
    set_formatting(plot_data);
    plot_data.ctx.fillRect(plot_data.shape_data.left, plot_data.shape_data.top, plot_data.shape_data.width, plot_data.shape_data.height);
    plot_data.ctx.strokeRect(plot_data.shape_data.left, plot_data.shape_data.top, plot_data.shape_data.width, plot_data.shape_data.height);
    plot_text(plot_data);
}
function plot_diamond(plot_data) {
    // const width_height_ratio = 0.7;
    const shape_data = plot_data.shape_data;
    plot_data.ctx.beginPath();
    const half_width = shape_data.width / 2;
    plot_data.ctx.moveTo(shape_data.left + half_width, shape_data.top);
    // top left edge
    plot_data.ctx.lineTo(shape_data.left, shape_data.top + shape_data.height / 2);
    // bottom left edge
    plot_data.ctx.lineTo(shape_data.left + half_width, shape_data.top + shape_data.height);
    // bottom right edge
    plot_data.ctx.lineTo(shape_data.left + shape_data.width, shape_data.top + shape_data.height / 2);
    // closing the path automatically creates
    // the top right edge
    plot_data.ctx.closePath();
    set_formatting(plot_data);
    plot_data.ctx.fill();
    plot_text(plot_data);
}
function plot_text(data) {
    // ToDo: Replace with appropriate font color from layout
    const text_color = data.shape_format.text_format.text_color;
    console.log(`Font color for ${data.text} is ${text_color}`);
    const font_string = `${data.shape_format.text_format.font_size}px ${data.shape_format.text_format.font}`;
    console.log(`Font string for ${data.text} is ${font_string}`);
    data.ctx.font = font_string;
    data.ctx.fillStyle = color_to_fill_style(text_color);
    const v_align = data.shape_format.text_format.vertical_align;
    const text_flow = data.shape_format.text_format.text_flow;
    console.log(`Text flow is ${text_flow}`);
    let text_v_position;
    console.log(`v_align = ${v_align}`);
    switch (v_align) {
        case "TOP":
            text_v_position = data.shape_data.top;
            data.ctx.textBaseline = "top";
            break;
        case "MIDDLE":
            text_v_position = data.shape_data.top + data.shape_data.height / 2;
            data.ctx.textBaseline = "middle";
            break;
        case "BOTTOM":
            text_v_position = data.shape_data.top + data.shape_data.height;
            data.ctx.textBaseline = "bottom";
    }
    const margin = 5; // Manually adjusted for now.
    let x_val = data.shape_data.left; // Initial/default value
    const external_flag = data.shape_format.text_format.external_text_flag;
    console.log(`External flag for ${data.text} is ${external_flag}`);
    switch (text_flow) {
        case FLOW_TO_RIGHT:
        case FLOW_WITHIN_SHAPE:
        case FLOW_CLIPPED:
            // For flow within shape and clipped default to flow right for now
            data.ctx.textAlign = "left";
            if (external_flag) {
                // Need to begin the plot outside the right edge of the shape
                x_val = data.shape_data.left + data.shape_data.width + margin;
            }
            else {
                x_val = data.shape_data.left + margin;
            }
            break;
        case FLOW_TO_LEFT:
            data.ctx.textAlign = "right";
            if (external_flag) {
                // Need to begin the plot outside the left edge of the shape
                x_val = data.shape_data.left - margin;
            }
            else {
                x_val = data.shape_data.left + data.shape_data.width - margin;
            }
            break;
        case FLOW_CENTRE:
            x_val = data.shape_data.left + data.shape_data.width / 2;
            data.ctx.textAlign = "center";
            break;
    }
    console.log(`About to plot text for ${data.text}, x=${x_val}, y=${text_v_position}`);
    data.ctx.fillText(data.text, x_val, text_v_position);
}
const dispatch_table = {
    "RECTANGLE": plot_rectangle,
    "DIAMOND": plot_diamond,
};
export function plot_visual(ctx, shapes, settings) {
    for (let shape of shapes) {
        const shape_details = shape.shape_details;
        const shape_name = shape_details.shape_name;
        let shape_plot_dims = shape.shape_details.shape_plot_dims;
        const shape_format = shape.shape_details.shape_format;
        const text = shape_details.text;
        // Scale all dimensions by scale_factor
        let k;
        for (k in shape_plot_dims) {
            shape_plot_dims[k] *= scale_factor;
        }
        const plot_function = dispatch_table[shape_name];
        const params = { ctx: ctx, shape_data: shape_plot_dims, shape_format: shape_format, text: text };
        plot_function(params);
    }
}
