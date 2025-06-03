import {initialise_canvases, plot_visual} from "./plot_visual";
import {get_visual_activity_data, get_visual_settings} from "./plan_visualiser_api";

export function add_download_image_event_listener() {
  // There is a button on the edit visual screen to download an image of the visual
  // This function will add the event listener to the button to invoke the logic when clicked.
  const download_image_button = document.querySelector("#download-image-button");

  download_image_button!.addEventListener('click', downloadImage);
}


async function renderForImageCreation() {
  // Re-draw visual elements for each canvas but onto a single consolidating canvas.
  console.log(`downloadImage: About to plot to capture canvas`)

  // Need visual settings as it included visual height which is needed to plot.
  const response = await get_visual_settings((window as any).visual_id);
  (window as any).visual_settings = response.data

  plot_visual(true)
}

function getImageUrlForCanvas(canvas: HTMLCanvasElement): string {
  console.log(`Visual thumbnail - canvas is ${canvas}`)
  return canvas.toDataURL("image/png")
}

async function downloadImage() {
  await renderForImageCreation();
  console.log(`Finished plotting, about to convert to image and get url`)
  const dataUrl = getImageUrlForCanvas((window as any).canvas_info.capture.canvas)

  // Now create a link to the url and simulate clicking on it so user just sees download
  let link = document.createElement('a');
  link.download = 'visual.png';
  link.href = dataUrl;

  // The link needs to be part of the document body to be "clickable".
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function captureVisualAsImage(canvas: HTMLCanvasElement): string {
  return getImageUrlForCanvas(canvas)
}

export async function addVisualImages(): Promise<void> {
  console.log(`addVisualImages called`);
  let imgElements: NodeListOf<HTMLImageElement> = document.querySelectorAll('[id^="thumbnail-"]');

  console.log(`Visual elements...`)
  console.dir(imgElements)

  for (let img of imgElements) {
    // Extract the "<xxx>" part and convert to integer
    let visualIdStr = (img.id.split('-')[1]);
    let visualId = parseInt(visualIdStr);
    console.log(`Processing image for visual ${visualId}`)


    // Make sure it's an integer
    if(!isNaN(visualId) && Number.isInteger(visualId)) {
      console.log("About to retrieve visual settings data from manage visual image")
      let response = await get_visual_settings(visualId);
      (window as any).visual_settings = response.data

      let [scale_factor, canvas_info] = initialise_canvases(true);
      console.log(`canvas_info for capture is ${canvas_info}`)
      console.log(`canvas for capture is ${canvas_info.canvas}`)

      // Request data for this visual and wait for it to be returned
      console.log("About to retrieve visual data from manage visual image")
      await get_visual_activity_data(visualId); // Refresh data from server before replotting

      (window as any).scale_factor = scale_factor;
      (window as any).canvas_info = canvas_info;

      plot_visual(true)
      // Update the img's src attribute
      img.src = captureVisualAsImage(canvas_info.capture.canvas);
    }
  }
}

