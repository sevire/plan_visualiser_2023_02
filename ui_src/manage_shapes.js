var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { get_plan_activity } from "./manage_visual";
import { update_visual_activities } from "./plan_visualiser_api";
import { plot_visual } from "./plot_visual";
export function update_shape_for_activity_handler(unique_id, shape_id) {
    return __awaiter(this, void 0, void 0, function* () {
        // This is a handler function which will be passed to the Dropdown class for the style dropdown in the activity
        // panel.  It will update the style for the indicated activity to the one with the style name supplied.
        const activity = get_plan_activity(unique_id);
        console.log(`Updating style id to ${shape_id}`);
        const data = [
            {
                id: activity.visual_data.id,
                plotable_shape: shape_id
            }
        ];
        yield update_visual_activities(activity.visual_data.visual.id, data);
        plot_visual();
    });
}
