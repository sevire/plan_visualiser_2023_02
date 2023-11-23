export function initialise_canvas(settings) {
    let canvas = document.getElementById("visual");
    console.log("Canvas = " + canvas);
    const res = canvas.getContext('2d');
    if (!res || !(res instanceof CanvasRenderingContext2D)) {
        throw new Error('Failed to get 2D context');
    }
    const context = res;
    console.log("context = " + context);
    let baseCanvasWidth = settings.canvas_width;
    let baseCanvasHeight = settings.canvas_height;
    canvas.style.width = baseCanvasWidth + "px";
    canvas.style.height = baseCanvasHeight + "px";
    canvas.width = Math.floor(baseCanvasWidth * window.devicePixelRatio);
    canvas.height = Math.floor(baseCanvasHeight * window.devicePixelRatio);
    context.scale(window.devicePixelRatio, window.devicePixelRatio);
    console.log("devicePixelRation: " + window.devicePixelRatio);
    console.log("After scaling... canvas.width:" + canvas.width + " canvas.height" + canvas.height);
    context.fillStyle = "rgb(244, 244, 244)";
    context.strokeStyle = "rgb(166, 166, 166)";
    context.lineWidth = 3;
    context.rect(0, 0, canvas.width, canvas.height);
    context.fill();
    context.stroke();
    // context.fillRect(0, 0, canvas.width, canvas.height)
    // context.strokeRect(0, 0, canvas.width, canvas.height)
    return context;
}
