import {
  get_swimlane_data,
  get_visual_activity_data,
  remove_activity_from_visual,
  update_swimlane_records
} from "./plan_visualiser_api";
import {plot_visual} from "./plot_visual";

async function manage_arrow_click(visual_id:number, swimlane_record: any, direction: "up"|"down") {
  await update_swimlane_order(visual_id, swimlane_record, "up")

  // Update swimlane panel with swimlanes for this visual in sequence order
  console.log(`Updating swimlane panel (after moving swimlane ${direction}...`)
  const swimlane_element = document.getElementById("swimlane_data")
  await update_swimlane_data(swimlane_element!, visual_id)

  await get_visual_activity_data(visual_id)
  plot_visual()
}

export async function add_arrow_to_element(element:HTMLElement, direction: "up"|"down", id:string, visual_id:number, swimlane_record:any) {
  let arrow = document.createElement('i')
  arrow.classList.add("fa-solid")
  arrow.classList.add("fa-circle-chevron-"+direction)
  arrow.id = id
  arrow.addEventListener('click', async function() {
    manage_arrow_click(visual_id, swimlane_record, direction)
  })
  element.appendChild(arrow)
}

export async function update_swimlane_data(swimlane_html_panel:HTMLElement, visual_id: number) {
  await get_swimlane_data(visual_id)

  // Find the tbody element within the swimlane table, then add a row for each swimlane.
  const tbody = swimlane_html_panel.querySelector("table tbody");

  // Clear tbody for case where we are updating panel rather than loading page
  tbody!.innerHTML = "";
  (window as any).swimlane_data.forEach((swimlane_record: any) => {
    // Add row to tbody with two td's, one for an up and down arrow and one for swimlane name
    // Create a new row
    let row = document.createElement('tr');
    let arrowCell = document.createElement('td');
    arrowCell.classList.add("arrow")

    // ToDo: Correct code to add arrows for swimlane so Id not same for both arrows as this is not legal HTML
    add_arrow_to_element(arrowCell, "up", swimlane_record.sequence_number, visual_id, swimlane_record)
    add_arrow_to_element(arrowCell, "down", swimlane_record.sequence_number, visual_id, swimlane_record)

    row.appendChild(arrowCell);

    // Create a cell for swimlane name
    let nameCell = document.createElement('td');
    nameCell.classList.add("name")
    nameCell.textContent = swimlane_record.swim_lane_name;
    row.appendChild(nameCell);

    // Add row to tbody
    tbody!.appendChild(row);

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
