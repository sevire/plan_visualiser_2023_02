import {
  get_swimlane_data, get_timeline_data,
  get_visual_activity_data,
  update_swimlane_records, update_timeline_records, update_visual_activities
} from "./plan_visualiser_api";
import {plot_visual} from "./plot_visual";
import {get_plan_activity} from "./manage_visual";

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
    let arrowCell = document.createElement('td');
    arrowCell.classList.add("arrow")

    // ToDo: Correct code to add arrows for swimlane so Id not same for both arrows as this is not legal HTML
    add_arrow_to_element(arrowCell, "up", timeline_record.sequence_number, visual_id, timeline_record)
    add_arrow_to_element(arrowCell, "down", timeline_record.sequence_number, visual_id, timeline_record)

    row.appendChild(arrowCell);

    // Create a cell for swimlane name
    let nameCell = document.createElement('td');
    nameCell.classList.add("name")
    nameCell.textContent = timeline_record.timeline_name;
    row.appendChild(nameCell);

    // Add row to tbody
    tbody!.appendChild(row);

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
