import {
  get_timeline_data,
  get_visual_activity_data,
  update_timeline_records, update_visual_activities
} from "./plan_visualiser_api";
import {plot_visual} from "./plot_visual";
import {get_plan_activity} from "./manage_visual";
import {
  add_arrow_button_to_element,
} from "./manage_swimlanes";
import {create_button_with_icon, createDropdown, populateDropdown} from "./widgets";
import {update_style_for_timeline_handler} from "./manage_styles";

async function manage_arrow_click(visual_id:number, timeline_record: any, direction: "up"|"down") {
  await update_timeline_order(visual_id, timeline_record, direction)

  // Update swimlane panel with swimlanes for this visual in sequence order
  console.log(`Updating timeline panel (after moving timeline ${direction}...`)
  const timeline_element = document.getElementById("timeline_data")
  await update_timeline_panel(timeline_element!, visual_id)

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

function createAndPopulateDropdown(
  dropdownParent: HTMLElement,
  styleName: string,
  styleData: Array<{ style_name: string, id: number }>,
  visualId: number,
  timelineRecordId: number,
  isOdd: boolean
): HTMLButtonElement {
  let dropDownButton: HTMLButtonElement = createDropdown(dropdownParent, styleName);

  populateDropdown(
    dropDownButton,
    styleData.map(obj => [obj.style_name, obj.id]),
    async (style_id: number) => {
      await update_style_for_timeline_handler(visualId, timelineRecordId, style_id, isOdd);
      await get_visual_activity_data((window as any).visual_id)
      plot_visual()
    }
  );

  return dropDownButton;
}

export async function update_timeline_panel(timeline_html_panel:HTMLElement, visual_id: number) {
  console.log("Adding timelines to timeline panel...")
  await get_timeline_data(visual_id)

  // Find the tbody element within the swimlane table, then add a row for each timeline.
  const tbody = timeline_html_panel.querySelector("table tbody");

  // Clear tbody for case where we are updating panel rather than loading page
  tbody!.innerHTML = "";

  (window as any).timeline_data.forEach((timeline_record: any) => {
    console.log(`Adding timeline row to timeline panel for ${timeline_record.timeline_name}`)

    let row = document.createElement('tr');
    tbody!.appendChild(row)

    let timelineNameTD = document.createElement('td');
    timelineNameTD.style.width = "20%"
    row.appendChild(timelineNameTD)

    let timelineNameDiv = document.createElement("div")
    timelineNameDiv.classList.add("text-truncate")
    timelineNameDiv.textContent = timeline_record.timeline_name

    timelineNameTD.appendChild(timelineNameDiv)

    const styleDropdownTD = document.createElement("td")
    styleDropdownTD.style.width = "40%"
    styleDropdownTD.classList.add("text-end")
    row.appendChild(styleDropdownTD)

    // Add two dropdowns, for odd and even styling for timeline labels

// Usage
    let timelineStyleOddButton = createAndPopulateDropdown(
      styleDropdownTD,
      timeline_record.plotable_style_odd.style_name,
      (window as any).style_data as Array<{ style_name: string, id: number }>,
      visual_id,
      timeline_record.id,
      true
    );

    let timelineStyleEvenButton = createAndPopulateDropdown(
      styleDropdownTD,
      timeline_record.plotable_style_even.style_name,
      (window as any).style_data as Array<{ style_name: string, id: number }>,
      visual_id,
      timeline_record.id,
      false
    );
    // Add td, toggle button, button group and two buttons for the up and down arrow
    const controlTD = document.createElement("td")
    controlTD.style.width = "40%"
    row.appendChild(controlTD)

    const buttonGroup1 = document.createElement("div")
    buttonGroup1.classList.add("btn-group", "btn-group-sm", "up-down-control", "me-1")
    buttonGroup1.setAttribute('role', 'group')
    buttonGroup1.setAttribute('aria-label', 'Basic Example')
    controlTD.appendChild(buttonGroup1)

    add_arrow_button_to_element(timeline_html_panel, buttonGroup1, "up", timeline_record.sequence_number, visual_id, timeline_record, update_timeline_order, update_timeline_panel)
    add_arrow_button_to_element(timeline_html_panel, buttonGroup1, "down", timeline_record.sequence_number, visual_id, timeline_record, update_timeline_order, update_timeline_panel)

    const buttonGroup2 = document.createElement("div")
    buttonGroup2.classList.add("btn-group", "btn-group-sm", "up-down-control", "me-1")
    buttonGroup2.setAttribute('role', 'group')
    buttonGroup2.setAttribute('aria-label', 'Basic Example')
    controlTD.appendChild(buttonGroup1)

    let timelineToggleButton: HTMLButtonElement
    if (timeline_record.enabled) {
      timelineToggleButton = create_button_with_icon("bi-check2")
      timelineToggleButton.classList.add("active")
    } else {
      timelineToggleButton = create_button_with_icon("bi-x-lg")
    }
    timelineToggleButton.addEventListener('click', async () => {
      const data: any = [
        {
          id: timeline_record.id,
          enabled: !timeline_record.enabled
        }
      ]
      await update_timeline_records(visual_id, data)
      await update_timeline_panel(timeline_html_panel, visual_id)
      await get_visual_activity_data(visual_id)
      plot_visual()
    })
    buttonGroup2.appendChild(timelineToggleButton)
    controlTD.appendChild(buttonGroup2)
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
