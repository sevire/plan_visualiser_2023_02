import {Colour} from "./shapes";

export default function get_activity_data(): any {
    let json_activities = document.getElementById("json_activities")!
    console.log("json_activities - " + json_activities)
    if (json_activities.textContent == null) {
        return {}
    } else {
        return JSON.parse(json_activities.textContent)
    }
}

interface VisualConfiguration {
    width: number,
    height: number,
    background_colour: Colour,
}

interface VisualData {
    visual_configuration: VisualConfiguration,
    shape_data: []
}
