import {get_plan_activity} from "./manage_visual";
import {update_visual_activities} from "./plan_visualiser_api";
import {plot_visual} from "./plot_visual";

export async function update_shape_for_activity_handler(unique_id:string, shape_id:number) {
  // This is a handler function which will be passed to the Dropdown class for the style dropdown in the activity
  // panel.  It will update the style for the indicated activity to the one with the style name supplied.
  const activity = get_plan_activity(unique_id)
  console.log(`Updating style id to ${shape_id}`)

  const data = [
  {
    id: activity.visual_data.id,
    plotable_shape: shape_id
  }
]
await update_visual_activities(activity.visual_data.visual.id, data)
plot_visual()
}
