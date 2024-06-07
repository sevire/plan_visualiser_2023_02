import {get_visual_activity_data} from "./plan_visualiser_api";
import {plot_visual} from "./plot_visual";

export class Dropdown {
    // General class which creates a dropdown for use in the activity panel to handle changes to attributes such as
    // swimlane, style, shape etc for a given visual activity.
    // Handles the creation of a dropdown widget and then calls the passed in callback function when one of the options
    // is selected.
    activity_unique_id: string;
    element: HTMLElement | null;
    options: [[string, number]]; // [0] is text for dropdown, [1] is id to use for option HTML element
    selectedOption: string;

    // Select handler will take the unique id of the activity and the selected value.  The passed in function should use
    // this to send an update to the activity, and when that is complete the common handler in this class will get
    // updated canvas data and re-plot the visual.
    select_handler: (unique_id: string, selected_value: number) => void;

    constructor(id: string, activity_unique_id: string, options: [[string, number]], select_handler: (unique_id:string, selected_id: number) => void) {
        this.activity_unique_id = activity_unique_id;
        this.options = options;
        this.element = document.getElementById(id);
        this.selectedOption = this.options[0][0];
        this.select_handler = select_handler;

        this.generate();
    }

    async generate() {
        const select = document.createElement('select');
        select.id = "select_element"
        this.options.forEach(option => {
            const option_text = option[0];
            const option_id = option[1]
            const optElement = document.createElement('option');
            optElement.text = option_text;
            optElement.value = option_text;
            optElement.id = option_id.toString();
            select.add(optElement);
        })

        select.addEventListener('change', async (event) => {
            const targetSelectedElement = event.target as HTMLSelectElement;
            const targetOptionElement: HTMLOptionElement = targetSelectedElement.options[targetSelectedElement.selectedIndex];
            const swimlane_id = parseInt(targetOptionElement.id);
            console.log(`Swimlane selected: text:${this.selectedOption}, id:${swimlane_id}`);

            await this.select_handler(this.activity_unique_id, swimlane_id);
            await get_visual_activity_data((window as any).visual_id)
            plot_visual()

        })

        if(this.element) {
            this.element.appendChild(select);
        }
    }
}