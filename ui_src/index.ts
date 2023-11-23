import {initialise_canvas} from "./drawing";
import {plot_visual} from "./plot_shapes";
import {get_activity_data, checkKey, get_activities_from_server, selectRowByIndex} from "./visual";

window.addEventListener('DOMContentLoaded', () => {
  // const visual = get_activity_data()
  // const visual_settings = visual['settings']
  // const visual_activities = visual['shapes']
  // let context = initialise_canvas(visual_settings);

  // ToDo: Shouldn't automatically plot visual as may not be on the visual page
  // plot_visual(context, visual_activities, visual_settings);
});
(window as any).get_activities_from_server = get_activities_from_server;
(window as any).checkKey = checkKey;
(window as any).get_activity_data = get_activity_data;
(window as any).initialise_canvas = initialise_canvas;
(window as any).plot_visual = plot_visual;

