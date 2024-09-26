import {plot_visual} from "./plot_visual";

export function add_download_image_event_listener() {
  // There is a button on the edit visual screen to download an image of the visual
  // This function will add the event listener to the button to invoke the logic when clicked.
  const download_image_button = document.querySelector("#download-image-button");

  download_image_button!.addEventListener('click', downloadImage
);
}

function downloadImage() {
  const visual = (window as any).visual_id

  // Re-draw visual elements for each canvas but onto a single consolidating canvas.
  console.log(`downloadImage: About to plot to capture canvas`)
  plot_visual(true)
  console.log(`Finished plotting, about to convert to image and get url`)
  let dataUrl: string = (window as any).canvas_info.capture.canvas.toDataURL("image/png");

  // Now create a link to the url and simulate clicking on it so user just sees download
  let link = document.createElement('a');
  link.download = 'visual.png';
  link.href = dataUrl;

  // The link needs to be part of the document body to be "clickable".
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}