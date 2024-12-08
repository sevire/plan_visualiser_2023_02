import {initialise_canvas} from "./drawing";
import {checkKey} from "./visual";
import {
  get_plan_activity_data,
  get_shape_records,
  get_style_records,
  get_visual_activity_data, get_visual_settings
} from "./plan_visualiser_api";
import {createPlanTree} from "./manage_visual";
import {initialise_canvases, plot_visual} from "./plot_visual";
import {addStylesheetToDOM} from "./utilities";
import {update_swimlane_data} from "./manage_swimlanes";
import {update_timeline_panel} from "./manage_timelines";
import {add_download_image_event_listener} from "./manage_visual_image";
import {addVisualImages} from "./manage_visual_image";

window.addEventListener('DOMContentLoaded', () => {
  console.log("DOM Loaded zzzz....")
});
console.log("Executing index.ts");
(window as any).get_plan_activity_data = get_plan_activity_data;
(window as any).get_visual_activity_data = get_visual_activity_data;
(window as any).createPlanTree = createPlanTree;
(window as any).addStylesheetToDOM = addStylesheetToDOM;
(window as any).checkKey = checkKey;
(window as any).initialise_canvas = initialise_canvas;
(window as any).initialise_canvases = initialise_canvases;
(window as any).plot_visual = plot_visual;
(window as any).update_swimlane_data = update_swimlane_data;
(window as any).update_timeline_panel = update_timeline_panel;
(window as any).get_style_records = get_style_records;
(window as any).get_shape_records = get_shape_records;
(window as any).get_visual_settings = get_visual_settings;
(window as any).add_download_image_event_listener = add_download_image_event_listener;
(window as any).addVisualImages = addVisualImages;

