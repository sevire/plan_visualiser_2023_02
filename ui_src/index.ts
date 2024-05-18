import {initialise_canvas} from "./drawing";
import {checkKey, get_activities_from_server} from "./visual";
import {get_plan_activity_data, get_visual_activity_data} from "./plan_visualiser_api";
import {createPlanTree} from "./manage_visual";
import {plot_visual} from "./plot_visual";
import {addStylesheetToDOM} from "./utilities";

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
