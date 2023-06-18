import {initialise_canvas} from "./drawing";
import {plot_visual} from "./plot_shapes";
import get_activity_data from "./visual";

window.addEventListener('DOMContentLoaded', () => {
  const visual = get_activity_data()
  const visual_settings = visual['settings']
  const visual_activities = visual['shapes']
  let context = initialise_canvas(visual_settings)
  plot_visual(context, visual_activities, visual_settings)
});