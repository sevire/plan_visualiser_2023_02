import {get_plan_activity} from "./manage_visual";
import {update_timeline_records, update_visual_activities} from "./plan_visualiser_api";
import {plot_visual} from "./plot_visual";

export async function update_style_for_activity_handler(unique_id:string, style_id:number) {
  // This is a handler function which will be passed to the Dropdown class for the style dropdown in the activity
  // panel.  It will update the style for the indicated activity to the one with the style name supplied.
  const activity = get_plan_activity(unique_id)
  console.log(`Updating style id to ${style_id}`)

  const data = [
  {
    id: activity.visual_data.id,
    plotable_style: style_id
  }
]
await update_visual_activities(activity.visual_data.visual.id, data)
plot_visual()
}

export async function update_style_for_timeline_handler(visual_id: number, timeline_id:number, style_id:number, odd_flag:boolean = false) {
  // This is a handler function which will be passed to the Dropdown class for the style dropdown in the activity
  // panel.  It will update the style for the indicated activity to the one with the style name supplied.
  console.log(`Updating style id to ${style_id} for timeline ${timeline_id} in visual ${visual_id}`)

  const data: any = [
  {
    id: timeline_id,
  }
]
  if (odd_flag) {
    data[0].plotable_style_odd = style_id
  } else {
    data[0].plotable_style_even = style_id
  }
await update_timeline_records(visual_id, data)
plot_visual()
}
