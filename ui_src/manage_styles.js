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
import { get_visual_settings, update_timeline_records, update_visual_activities } from "./plan_visualiser_api";
import { plot_visual } from "./plot_visual";
export function update_style_for_activity_handler(unique_id, style_id) {
    return __awaiter(this, void 0, void 0, function* () {
        // This is a handler function which will be passed to the Dropdown class for the style dropdown in the activity
        // panel.  It will update the style for the indicated activity to the one with the style name supplied.
        const activity = get_plan_activity(unique_id);
        console.log(`Updating style id to ${style_id}`);
        const data = [
            {
                id: activity.visual_data.id,
                plotable_style: style_id
            }
        ];
        yield update_visual_activities(activity.visual_data.visual.id, data);
        // Need visual settings as it included visual height which is needed to plot.
        const response = yield get_visual_settings(window.visual_id);
        window.visual_settings = response.data;
        plot_visual();
    });
}
export function update_style_for_timeline_handler(visual_id, timeline_id, style_id, odd_flag = false) {
    return __awaiter(this, void 0, void 0, function* () {
        // This is a handler function which will be passed to the Dropdown class for the style dropdown in the activity
        // panel.  It will update the style for the indicated activity to the one with the style name supplied.
        console.log(`Updating style id to ${style_id} for timeline ${timeline_id} in visual ${visual_id}`);
        const data = [
            {
                id: timeline_id,
            }
        ];
        if (odd_flag) {
            data[0].plotable_style_odd = style_id;
        }
        else {
            data[0].plotable_style_even = style_id;
        }
        yield update_timeline_records(visual_id, data);
        // Need visual settings as it included visual height which is needed to plot.
        const response = yield get_visual_settings(window.visual_id);
        window.visual_settings = response.data;
        plot_visual();
    });
}
