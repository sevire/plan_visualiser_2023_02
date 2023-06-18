import {BoxShapeDimensions, ShapeName, ShapesData} from "./shapes";
import get_activity_data from "./visual";

const scale_factor:number = 1.0;  // to ensure that visual works on screen (may tweak value)

interface PlotFunctionData {
    ctx: CanvasRenderingContext2D;
    shape_data: any;
}

function plot_rectangle(plot_data: PlotFunctionData) {
    console.log("Plotting rectangle...");
    console.log("left:" + plot_data.shape_data.left + ", top:" + plot_data.shape_data.top)
    console.log("width:" + plot_data.shape_data.width + ", height:" + plot_data.shape_data.height)
    plot_data.ctx.fillStyle = "blue";
    plot_data.ctx.strokeStyle = "white";
    plot_data.ctx.lineWidth = 1;
    plot_data.ctx.fillRect(
        plot_data.shape_data.left,
        plot_data.shape_data.top,
        plot_data.shape_data.width,
        plot_data.shape_data.height);
    plot_data.ctx.strokeRect(
        plot_data.shape_data.left,
        plot_data.shape_data.top,
        plot_data.shape_data.width,
        plot_data.shape_data.height);
}

function plot_diamond(plot_data: PlotFunctionData) {
    const width_height_ratio = 0.7;
    const context = plot_data.ctx;
    const shape_data = plot_data.shape_data;
    context.beginPath();
    context.moveTo(shape_data.left, shape_data.top);

    // top left edge
    context.lineTo(shape_data.left - (shape_data.width * width_height_ratio) / 2, shape_data.top + shape_data.height / 2);

    // bottom left edge
    context.lineTo(shape_data.left, shape_data.top + shape_data.height);

    // bottom right edge
    context.lineTo(shape_data.left + (shape_data.width * width_height_ratio) / 2, shape_data.top + shape_data.height / 2);

    // closing the path automatically creates
    // the top right edge
    context.closePath();

    context.fillStyle = "red";
    context.fill();
}

function plot_text(context:CanvasRenderingContext2D, text:string) {

}

const dispatch_table = {
    "RECTANGLE": plot_rectangle,
    "DIAMOND": plot_diamond,
}
type DispatchTableType = typeof dispatch_table

export function plot_visual(ctx:CanvasRenderingContext2D, shapes: any, settings: any) {
    for (let shape of shapes) {
        const shape_details = shape.shape_details
        const shape_name: ShapeName = shape_details.shape_name as keyof typeof dispatch_table;
        let shape_plot_dims:BoxShapeDimensions = shape.shape_details.shape_plot_dims

        // Scale all dimensions by scale_factor
        let k: keyof typeof shape_plot_dims
        for (k in shape_plot_dims) {
            shape_plot_dims[k] *= scale_factor
        }

        const plot_function = dispatch_table[shape_name]

        const params:PlotFunctionData = {ctx: ctx, shape_data: shape_plot_dims}
        plot_function(params)

        // Now plot text
        plot_text(ctx, "")
    }
}
