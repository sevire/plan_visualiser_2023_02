import {initialise_canvas} from "./drawing";
import {checkKey} from "./visual";
import {
  get_plan_activity_data,
  get_shape_records,
  get_style_records,
  get_visual_activity_data
} from "./plan_visualiser_api";
import {createPlanTree} from "./manage_visual";
import {plot_visual} from "./plot_visual";
import {addStylesheetToDOM} from "./utilities";
import {update_swimlane_data} from "./manage_swimlanes";

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
(window as any).plot_visual = plot_visual;
(window as any).update_swimlane_data = update_swimlane_data;
(window as any).get_style_records = get_style_records;
(window as any).get_shape_records = get_shape_records;
