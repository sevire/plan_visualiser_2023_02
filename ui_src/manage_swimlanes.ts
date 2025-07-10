import {
  compress_swimlane, get_plan_activity_data,
  get_swimlane_data,
  get_visual_activity_data, get_visual_settings,
  update_swimlane_records,
  update_visual_activities, update_visual_activity_swimlane
} from "./plan_visualiser_api";
import {plot_visual} from "./plot_visual";
import {get_plan_activity} from "./manage_visual";
import {add_tooltip, create_button_with_icon} from "./widgets";

async function manage_arrow_click(
  panel_element: HTMLElement,
  visual_id:number,
  data_record: any,
  direction: "up"|"down",
  update_order_func: ((arg0: number, arg1: any, arg2: string) => any) | undefined,
  update_panel_func: ((arg0: HTMLElement, arg1: number) => any) | undefined
) {
  await update_order_func!(visual_id, data_record, direction)

  // Update swimlane panel with swimlanes for this visual in sequence order
  console.log(`Updating panel (after moving item ${direction}...`)
  await update_panel_func!(panel_element!, visual_id)

  await get_visual_activity_data(visual_id)

  // Need visual settings as it included visual height which is needed to plot.
  const response = await get_visual_settings((window as any).visual_id);
  (window as any).visual_settings = response.data

  plot_visual()
}

export async function add_arrow_button_to_element(
  panel_element:HTMLElement,
  arrow_element:HTMLElement,
  direction: "up"|"down",
  id:string,
  visual_id:number,
  data_record:any,
  update_order_func: ((arg0: number, arg1: any, arg2: string) => any) | undefined,
  update_panel_func: ((arg0: HTMLElement, arg1: number) => any) | undefined
){
  // Add button and appropriate arrow icon to supplied element.
  let button = document.createElement("button")
  button.classList.add("btn", "btn-secondary")
  arrow_element.appendChild(button)

  let arrow = document.createElement('i')
  arrow.classList.add("bi", "bi-caret-" + direction + "-fill")
  arrow.id = id + "-" + direction  // Need to ensure the id is unique so add direction to swimlane_id
  arrow.addEventListener('click', async function() {
    manage_arrow_click(panel_element, visual_id, data_record, direction, update_order_func, update_panel_func)
  })
  button.appendChild(arrow)
}

export async function update_swimlane_data(swimlane_html_panel:HTMLElement, visual_id: number) {
  // Populates the swimlane panel on the main edit visual page.
  // Adds a row for each swimlane and adds buttons for compress, move up etc.

  console.log("Adding swimlanes to swimlane panel...")
  await get_swimlane_data(visual_id)

  console.log(`Swimlane data: ${JSON.stringify((window as any).swimlane_data)}`)

  // Find the tbody element within the swimlane table, then add a row for each swimlane.
  const tbody = swimlane_html_panel.querySelector("table tbody");

  // Clear tbody for case where we are updating panel rather than loading page
  tbody!.innerHTML = "";
  let applied_default_swimlane = false;
  (window as any).swimlane_data.forEach((swimlane_record: any) => {
    console.log(`Adding swimlane row to swimlane panel for ${swimlane_record.swim_lane_name}`)
    // Add row to tbody with two td's, one for an up and down arrow and one for swimlane name
    // Create a new row
    let row = document.createElement('tr');
    if (!applied_default_swimlane) {
      console.log(`Adding default swimlane class to swimlane ${swimlane_record.swim_lane_name}`)
      row.classList.add("default-swimlane")
      applied_default_swimlane = true;
    } else {
      console.log(`This swimlane not default, so not adding default swimlane class to swimlane ${swimlane_record.swim_lane_name}`)
    }

    row.addEventListener('click', async function() {
      // Need to
      // - Remove the default-swimlane class from the row where it is currently set
      // - Add default-swimlane class to this row
      // - Update window.default_swimlane to be swimlane_record.sequence_number
      const currentDefaultElement = document.querySelector('div#swimlane_data tr.default-swimlane')
      currentDefaultElement!.classList.remove("default-swimlane")
      row.classList.add('default-swimlane');
      (window as any).default_swimlane_seq_num = swimlane_record.sequence_number;
    })

    tbody!.appendChild(row)

    // Add td and div with swimlane name to row.  We need the div for the text-truncate to work.
    let swimlaneNameTD = document.createElement('td');
    swimlaneNameTD.classList.add("label")

    row.appendChild(swimlaneNameTD);

    let swimlaneNameDiv = document.createElement("div")
    swimlaneNameDiv.classList.add("text-truncate")

    swimlaneNameDiv.textContent = swimlane_record.swim_lane_name
    swimlaneNameTD.appendChild(swimlaneNameDiv)

    // Add td, button group and two buttons for the up and down arrow
    const controlTD = document.createElement("td")
    controlTD.classList.add("text-end")
    row.appendChild(controlTD)

    const buttonGroup1 = document.createElement("div")
    buttonGroup1.classList.add("btn-group", "btn-group-sm", "up-down-control", "me-1")
    buttonGroup1.setAttribute('role', 'group')
    buttonGroup1.setAttribute('aria-label', 'Basic Example')
    controlTD.appendChild(buttonGroup1)

    console.log(`Adding arrow buttons to swimlane panel for ${swimlane_record.swim_lane_name}`)

    add_arrow_button_to_element(swimlane_html_panel, buttonGroup1, "up", swimlane_record.sequence_number, visual_id, swimlane_record, update_swimlane_order, update_swimlane_data)
    add_arrow_button_to_element(swimlane_html_panel, buttonGroup1, "down", swimlane_record.sequence_number, visual_id, swimlane_record, update_swimlane_order, update_swimlane_data)

    const buttonGroup2 = document.createElement("div")
    buttonGroup2.setAttribute('role', 'group')
    buttonGroup2.setAttribute('aria-label', 'Basic Example')
    buttonGroup2.classList.add("btn-group", "btn-group-sm")

    // Add td, button group and two buttons for compress and autolayout

    console.log(`Adding compress and auto buttons to swimlane panel for ${swimlane_record.swim_lane_name}`)

    controlTD.appendChild(buttonGroup2)
    const compressButton = create_button_with_icon("bi-arrows-collapse")
    add_tooltip(compressButton, "Compress - remove blank lines");

    compressButton.addEventListener('click', async () => {
      console.log(`Compressing swimlane ${swimlane_record.swim_lane_name}`);

      // Send api call to compress this swimlane, then re-plot the visual
      await compress_swimlane(visual_id, swimlane_record.sequence_number);
      await get_visual_activity_data(visual_id);
      await get_plan_activity_data(visual_id);

      // Need visual settings as it included visual height which is needed to plot.
      const response = await get_visual_settings((window as any).visual_id);
      (window as any).visual_settings = response.data

      plot_visual();
    })

    const autoButton = create_button_with_icon("bi-aspect-ratio")
    add_tooltip(autoButton, "Auto - Auto layout")

    buttonGroup2.appendChild(compressButton)
    buttonGroup2.appendChild(autoButton)
  });
}

export async function update_swimlane_order(visual_id: number, this_swimlane_object:any, direction:string) {
  // To move this swimlane up, we find the swimlane record with the previous sequence number for this visual,
  // and swap sequence numbers with current one.
  const this_sequence_number = this_swimlane_object.sequence_number;
  let swimlane_update_object: any;
  if (direction == "up") {
    if (this_swimlane_object.sequence_number == 1) {
      console.log("Swimlane already at top of list, can't move up")
    } else {
      // Swimlanes are in sequence number order and sequence numbers are contiguous and start from 1.
      // So find previous swimlane record, which we are going to swap with to move this one up.
      const previous_sequence_number = this_sequence_number - 1
      const previous_swimlane_object = (window as any).swimlane_data[previous_sequence_number-1]
      swimlane_update_object = [
        {
          id: this_swimlane_object.id,
          sequence_number: previous_sequence_number
        },
        {
          id: previous_swimlane_object.id,
          sequence_number: this_sequence_number
        }
      ]
    }
  } else if (direction == "down") {
    if (this_swimlane_object.sequence_number == (window as any).swimlane_data.length) {
      console.log("Swimlane already at bottom of list, can't move down")
    } else {
      // Swimlanes are in sequence number order and sequence numbers are contiguous and start from 1.
      // So find previous swimlane record, which we are going to swap with to move this one up.
      const next_sequence_number = this_sequence_number + 1
      const next_swimlane_object = (window as any).swimlane_data[next_sequence_number-1]
      swimlane_update_object = [
        {
          id: this_swimlane_object.id,
          sequence_number: next_sequence_number
        },
        {
          id: next_swimlane_object.id,
          sequence_number: this_sequence_number
        }
      ]
    }
  }
  await update_swimlane_records(visual_id, swimlane_update_object)
  }

  export async function update_swimlane_for_activity_handler(unique_id:string, swimlane_id:number) {
    // This is a handler function which will be passed to the Dropdown class for the swimlane dropdown in the activity
    // panel.  It will update the swimlane for the indicated activity to the one with the swimlane name supplied.
    const activity = get_plan_activity(unique_id)
    console.log(`Updating swimlane id to ${swimlane_id}`)

    await update_visual_activity_swimlane(activity.visual_data.visual.id, unique_id, swimlane_id)
  }
