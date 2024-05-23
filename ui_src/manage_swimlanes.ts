import {
  get_swimlane_data,
  get_visual_activity_data,
  remove_activity_from_visual,
  update_swimlane_records
} from "./plan_visualiser_api";
import {plot_visual} from "./plot_visual";

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

      let up_arrow = document.createElement('i')
      up_arrow.classList.add("fa-solid")
      up_arrow.classList.add("fa-circle-chevron-up")
      up_arrow.id = swimlane_record.sequence_number
      up_arrow.addEventListener('click', async function() {
        // We want to move this swimlane up.  This means swapping with the one above it.
        await update_swimlane_order(visual_id, swimlane_record, "up")

        // Update swimlane panel with swimlanes for this visual in sequence order
        console.log("Updating swimlane panel (after moving swimlane up...")
        const swimlane_element = document.getElementById("swimlane_data")
        await update_swimlane_data(swimlane_element!, visual_id)

        await get_visual_activity_data(visual_id)
        plot_visual()
      })

      let down_arrow = document.createElement('i')
      down_arrow.classList.add("fa-solid")
      down_arrow.classList.add("fa-circle-chevron-down")
      down_arrow.id = swimlane_record.sequence_number
      down_arrow.addEventListener('click', async function() {
        // We want to move this swimlane down.  This means swapping with the one above it.
        await update_swimlane_order(visual_id, swimlane_record, "down")

        // Update swimlane panel with swimlanes for this visual in sequence order
        console.log("Updating swimlane panel (after moving swimlane down...")
        const swimlane_element = document.getElementById("swimlane_data")
        await update_swimlane_data(swimlane_element!, visual_id)

        await get_visual_activity_data(visual_id)
        plot_visual()
      })

      // Create a cell for arrows
      let arrowCell = document.createElement('td');
      arrowCell.classList.add("arrow")

      arrowCell.appendChild(up_arrow)
      arrowCell.appendChild(down_arrow)

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
