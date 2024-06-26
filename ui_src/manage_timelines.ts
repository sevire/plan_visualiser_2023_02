import {
  get_swimlane_data, get_timeline_data,
  get_visual_activity_data,
  update_swimlane_records, update_timeline_records, update_visual_activities
} from "./plan_visualiser_api";
import {plot_visual} from "./plot_visual";
import {get_plan_activity} from "./manage_visual";
import {
  add_arrow_button_to_element,
  add_tooltip,
  create_button_with_icon,
  update_swimlane_order
} from "./manage_swimlanes";

async function manage_arrow_click(visual_id:number, timeline_record: any, direction: "up"|"down") {
  await update_timeline_order(visual_id, timeline_record, direction)

  // Update swimlane panel with swimlanes for this visual in sequence order
  console.log(`Updating swimlane panel (after moving swimlane ${direction}...`)
  const timeline_element = document.getElementById("timeline_data")
  await update_timeline_data(timeline_element!, visual_id)

  await get_visual_activity_data(visual_id)
  plot_visual()
}

export async function add_arrow_to_element(element:HTMLElement, direction: "up"|"down", id:string, visual_id:number, timeline_record:any) {
  let arrow = document.createElement('i')
  arrow.classList.add("fa-solid")
  arrow.classList.add("fa-circle-chevron-"+direction)
  arrow.id = id
  arrow.addEventListener('click', async function() {
    manage_arrow_click(visual_id, timeline_record, direction)
  })
  element.appendChild(arrow)
}

export async function update_timeline_data(timeline_html_panel:HTMLElement, visual_id: number) {
  await get_timeline_data(visual_id)

  // Find the tbody element within the swimlane table, then add a row for each swimlane.
  const tbody = timeline_html_panel.querySelector("table tbody");

  // Clear tbody for case where we are updating panel rather than loading page
  tbody!.innerHTML = "";
  (window as any).timeline_data.forEach((timeline_record: any) => {
    // Add row to tbody with two td's, one for an up and down arrow and one for swimlane name
    // Create a new row
    let row = document.createElement('tr');
    tbody!.appendChild(row)

    // Add td and div with swimlane name to row.  We need the dive for the text-truncate to work.
    let timelineNameTD = document.createElement('td');
    timelineNameTD.classList.add("label")
    row.appendChild(timelineNameTD);

    let timelineNameDiv = document.createElement("div")
    timelineNameDiv.classList.add("text-truncate")
    timelineNameDiv.textContent = timeline_record.timeline_name
    timelineNameTD.appendChild(timelineNameDiv)

    // Add td, button group and two buttons for the up and down arrow
    const controlTD = document.createElement("td")
    controlTD.classList.add("text-end")
    row.appendChild(controlTD)

    const buttonGroup1 = document.createElement("div")
    buttonGroup1.classList.add("btn-group", "btn-group-sm", "up-down-control", "me-1")
    buttonGroup1.setAttribute('role', 'group')
    buttonGroup1.setAttribute('aria-label', 'Basic Example')
    controlTD.appendChild(buttonGroup1)

    add_arrow_button_to_element(timeline_html_panel, buttonGroup1, "up", timeline_record.sequence_number, visual_id, timeline_record, update_timeline_order, update_timeline_data)
    add_arrow_button_to_element(timeline_html_panel, buttonGroup1, "down", timeline_record.sequence_number, visual_id, timeline_record, update_timeline_order, update_timeline_data)

  });
}

export async function update_timeline_order(visual_id: number, this_timeline_object:any, direction:string) {
  // To move this timeline up, we find the timeline record with the previous sequence number for this visual,
  // and swap sequence numbers with current one.
  const this_sequence_number = this_timeline_object.sequence_number;
  let timeline_update_object: any;
  if (direction == "up") {
    if (this_timeline_object.sequence_number == 1) {
      console.log("Timeline already at top of list, can't move up")
    } else {
      // Timelines are in sequence number order and sequence numbers are contiguous and start from 1.
      // So find previous timeline record, which we are going to swap with to move this one up.
      const previous_sequence_number = this_sequence_number - 1
      const previous_timeline_object = (window as any).timeline_data[previous_sequence_number-1]
      timeline_update_object = [
        {
          id: this_timeline_object.id,
          sequence_number: previous_sequence_number
        },
        {
          id: previous_timeline_object.id,
          sequence_number: this_sequence_number
        }
      ]
    }
  } else if (direction == "down") {
    if (this_timeline_object.sequence_number == (window as any).timeline_data.length) {
      console.log("Timeline already at bottom of list, can't move down")
    } else {
      // Timelines are in sequence number order and sequence numbers are contiguous and start from 1.
      // So find previous timeline record, which we are going to swap with to move this one up.
      const next_sequence_number = this_sequence_number + 1
      const next_timeline_object = (window as any).timeline_data[next_sequence_number-1]
      timeline_update_object = [
        {
          id: this_timeline_object.id,
          sequence_number: next_sequence_number
        },
        {
          id: next_timeline_object.id,
          sequence_number: this_sequence_number
        }
      ]
    }
  }
  await update_timeline_records(visual_id, timeline_update_object)
  }

  export async function update_swimlane_for_activity_handler(unique_id:string, swimlane_id:number) {
    // This is a handler function which will be passed to the Dropdown class for the swimlane dropdown in the activity
    // panel.  It will update the swimlane for the indicated activity to the one with the swimlane name supplied.
    const activity = get_plan_activity(unique_id)
    console.log(`Updating swimlane id to ${swimlane_id}`)

    const data = [
    {
      id: activity.visual_data.id,
      swimlane: swimlane_id
    }
  ]
  await update_visual_activities(activity.visual_data.visual.id, data)
  }
