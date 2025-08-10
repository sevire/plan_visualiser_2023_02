// Functionality to manage the main edit visual page of the app.
// The id of the visual is set to the id of the body element in the page by the Django app.
// The edit visual page is purely Ajax driven and each element of the page is updated by calling
// the API to the Django app to get the data required to populate the page.

import {
  add_activity_to_visual,
  add_sub_activities_to_visual,
  get_plan_activity_data,
  get_visual_activity_data, get_visual_settings,
  remove_activity_from_visual,
  update_visual_activities
} from "./plan_visualiser_api";
import {toggle_expansion} from "./manage_plan_panel";
import {highlight_activity, plot_visual} from "./plot_visual";
import {update_swimlane_for_activity_handler} from "./manage_swimlanes";
import {update_style_for_activity_handler} from "./manage_styles";
import {update_shape_for_activity_handler} from "./manage_shapes";
import {clearElement, createDropdown, populateDropdown} from "./widgets";

function add_add_sub_activities_event_handler(plan_tree_root: Element) {
  // Add event handler to icon button for adding all sub-activities of the currently selected
  // activity.
  const add_sub_activities_button = document.getElementById("add-subtask-button")
  add_sub_activities_button?.addEventListener('click', async function() {
    // Get id of the currently selected plan activity and use api to add all direct sub-activities for that activity.
    const selected = plan_tree_root.getElementsByClassName('current')
    if (selected.length != 1) {
      console.log(`Error: add-subtask-button clicked but unique activity not selected ${selected}`)
    } else {
      const visual_id = (window as any).visual_id
      const swimlane_seq_num = (window as any).default_swimlane_seq_num
      const unique_id = selected[0].id
      console.log(`About to add sub-activities for visual_id ${visual_id}, unique_id ${unique_id}, swimlane, ${swimlane_seq_num}`)

      await add_sub_activities_to_visual(visual_id, unique_id, swimlane_seq_num)

      await get_plan_activity_data(visual_id)
      await get_visual_activity_data(visual_id)
      const response = await get_visual_settings((window as any).visual_id);
      (window as any).visual_settings = response.data

      plot_visual()
    }
  })
}

export async function createPlanTree() {
  // We are going to create a tree of elements to represent the hierarchical plan structure.  We will iterate through
  // all the plan activities in the order they appear in the plan and use the level to work out where each activity
  // sits compared to the previous (child, sibling, sibling of parent etc.)
  let topLevelUL = document.createElement('ul');
  topLevelUL.classList.add("bg-primary-subtle")
  let topLevelElements = [topLevelUL]
  topLevelElements[0].setAttribute("id", "plan-activities");

  // Level sequence may vary depending upon how the plan has been structured and which app the plan was created in.
  // But we want the lowest level to be 1 as various things depend on it (including color-coding).
  // So adjust level for each activity as we go to ensure that the lowest level to be 1.
  // We assume that the level for the first activity will be the lowest in the plan.
  const level_adjust = 1 - (window as any).plan_activity_data[0].plan_data.level
  let previousLevel = 1;

  // Before building the plan activity tree, add the event handler for plan activity buttons, such as
  // button to add sub-activities for current activity.
  add_add_sub_activities_event_handler(topLevelElements[0])

  // We are going to store the element we use to represent the first activity in the plan as we are going to return it
  // so it can be used as the current selected element once the page has been built.
  let initial_selected_activity_div: HTMLDivElement | any

  // Note using for rather than forEach as need to do business logic depending upon where we are
  // in the sequence.  May be a better way of doing this!
  for (let i = 0; i < (window as any).plan_activity_data.length; i++) {

    // Get activity for this index
    const activity = (window as any).plan_activity_data[i];
    const level = activity.plan_data.level + level_adjust

    console.log("(New) Processing activity: " + activity.plan_data.activity_name + ", level: " + level)
    const activity_text = activity.plan_data.activity_name
    const level_class = "level-" + level
    const li = document.createElement('li');

    // Put activity text into a div under the li to help style independently of ul/li structure.
    const activityDiv = document.createElement("div")
    console.log(activityDiv)
    activityDiv.setAttribute('class', level_class)
    activityDiv.id = activity.plan_data.unique_sticky_activity_id
    if (activity.visual_data && activity.visual_data.enabled) {
      activityDiv.classList.add('in-visual')
    }

    // Add event listener for clicking
    activityDiv.addEventListener('click', async function() {
      await manage_plan_activity_click(activity, activityDiv, topLevelElements)
    })

    if (i < (window as any).plan_activity_data.length - 1) {
      if ((window as any).plan_activity_data[i + 1].plan_data.level + level_adjust > level) {
        // This is the last at this level before we drop a level so need to add an expand icon and expand class
        const expandIcon = document.createElement('i');
        li.setAttribute('class', 'expandNode');

        expandIcon.setAttribute('class', 'bi bi-plus-circle-fill');
        // expandIcon.textContent = "+";  // Temp for when can't access CDN for icons.

        console.log("Adding event listener on icon" + expandIcon);
        expandIcon.addEventListener('click', function(event) {
          event.stopPropagation();
          toggle_expansion(li);
        });

        // Need to include expansion icon as this element has children
        activityDiv.appendChild(expandIcon);
      }
    }

    const textNode = document.createTextNode(activity_text)
    activityDiv.appendChild(textNode);

    li.appendChild(activityDiv)

    const levelChange = level - previousLevel;

    if (levelChange > 0) {
      const newTree = document.createElement('ul');
      const length = topLevelElements.length
      const entry = topLevelElements[length - 1]
      const lastChild = entry.lastChild
      lastChild?.appendChild(newTree)
      topLevelElements.push(newTree);

    } else if (levelChange < 0) {
      console.log("Down one or more levels")
      // If we went down one or more levels, we need to take that many trees off the list.
      topLevelElements.splice(topLevelElements.length + levelChange);
    } else {
      console.log("Same level, adding text node")
    }
    // Regardless of level change, append new activity to the current tree.
    topLevelElements[topLevelElements.length - 1].appendChild(li);

    previousLevel = level;
    console.log("topLevelElements", topLevelElements)

    // If this is the first activity in the plan then save the div as we need to return it
    // so that we can simulate a click after the pages has been built to pre-select the first
    // activity in the plan within the plan activity panel.
    if (i == 0) {
      console.log(`Saving first activity div so can click later ${activityDiv}`);
      initial_selected_activity_div = activityDiv;
    }
  }

  console.log("topLevelElements before return", topLevelElements);
  return [topLevelElements[0], initial_selected_activity_div];
}

async function add_to_visual(activity_id: string, swimlane_seq_number:number) {
  await add_activity_to_visual((window as any).visual_id, activity_id, swimlane_seq_number)
  console.log("Added activity to visual: " + activity_id);
  const activity = get_plan_activity(activity_id)
  activity.enabled = true;
}

async function remove_from_visual(activity_id: string) {
  await remove_activity_from_visual((window as any).visual_id, activity_id)
  console.log("Removed activity from visual: " + activity_id);
  const activity = get_plan_activity(activity_id)
  activity.enabled = false;
}

export function get_plan_activity(activity_id:string) {
  // Find activity in stored list of all plan activities by iterating through and checking each one.
  // ToDo: Review the logic of getting activity data as may be a more efficient way of doing it

  let found_value: any
  (window as any).plan_activity_data.forEach((activity: any) => {
    if (typeof found_value === 'undefined') {
      if (activity.plan_data.unique_sticky_activity_id === activity_id) {
        found_value = activity
      }
    }
  })
  return found_value
}

async function add_move_track_event_handler(direction: string, activity: any) {
  console.log(`Track number ${direction} clicked`)
  console.log(`Activity is ${activity}`)
  await update_activity_track(activity.visual_data.unique_id_from_plan, direction)
  await get_plan_activity_data((window as any).visual_id)
  await get_visual_activity_data((window as any).visual_id)

  // Need visual settings as it included visual height which is needed to plot.
  const response = await get_visual_settings((window as any).visual_id);
  (window as any).visual_settings = response.data

  plot_visual()
}

async function add_modify_track_height_event_handler(direction: string, activity: any) {
  console.log(`Track height ${direction} clicked`)
  console.log(`Activity is ${activity}`)
  let api_direction: string
  if (direction == "up") {
    api_direction = "increase"
  } else if (direction == "down") {
    api_direction = "decrease"
  } else {
    throw new Error(`Invalid value for direction = ${direction}`)
  }

  await update_activity_track_height(activity.visual_data.unique_id_from_plan, api_direction)
  await get_plan_activity_data((window as any).visual_id)
  await get_visual_activity_data((window as any).visual_id)

  // Need visual settings as it included visual height which is needed to plot.
    const response = await get_visual_settings((window as any).visual_id);
    (window as any).visual_settings = response.data

  plot_visual()
}

async function add_modify_text_flow_event_handler(flow_direction: string, activity: any) {
  console.log(`Text flow handler ${flow_direction} clicked`)
  console.log(`Activity is ${activity}`)

  await update_activity_text_flow(activity.visual_data.unique_id_from_plan, flow_direction)
  await get_plan_activity_data((window as any).visual_id)
  await get_visual_activity_data((window as any).visual_id)

  // Need visual settings as it included visual height which is needed to plot.
  const response = await get_visual_settings((window as any).visual_id);
  (window as any).visual_settings = response.data

  plot_visual()
}

// ====================================================================================================
// Below are functions need for dispatch table to set values for each field in the activity data panel
// ====================================================================================================
function set_boolean_value(TdRef: HTMLTableCellElement, value:boolean): void {
  // Set to tick for true and cross for false.
  TdRef.textContent = '';
  const iElement = document.createElement('i');
  if (value) {
    iElement.className = 'bi bi-check';
  } else {
    iElement.className = 'bi bi-x';
  }
  TdRef.appendChild(iElement);
}

function set_text_field(tdRef: HTMLTableCellElement, value: string): void {
  // It's just a text field so set text-truncate and set value
  tdRef.classList.add("text-truncate")
  tdRef.textContent = value
}

// Dispatch table used to set values of different types for each activity field
// NOTE: This is work in progress
const NonEditableDispatchTable: Record<string, Function> = {
  'milestone_flag': set_boolean_value,
  'activity_name': set_text_field,
  'unique_sticky_activity_id': set_text_field
};

function add_button_group(td_element: Element, aria_label: string) {
  // Add up and down arrows to the td element and add click event handler which updates activity vertical position.
  const buttonGroup = document.createElement("div");
  buttonGroup.classList.add("btn-group", "btn-group-sm", "up-down-control", "me-1");
  buttonGroup.setAttribute('role', 'group');
  buttonGroup.setAttribute('aria-label', aria_label);
  td_element.appendChild(buttonGroup)
  return buttonGroup;
}

function add_two_arrow_buttons(buttonGroup: HTMLDivElement, activity: any, labels:string[], event_handler: (direction:string, activity:any) => void) {
  let direction: string
  for (let i = 0; i < 2; i++) {
    if (i == 0) {
      direction = labels[0]
    } else {
      direction = labels[1]
    }
    // Add button and appropriate arrow icon to supplied element.
    let button = document.createElement("button")
    button.classList.add("btn", "btn-secondary")
    buttonGroup.appendChild(button)

    let arrow = document.createElement('i')
    arrow.classList.add("bi", "bi-caret-" + direction + "-fill")
    arrow.id = `${activity.visual_data.unique_id_from_plan}-[${direction}]`
    arrow.addEventListener('click', async function () {
      event_handler(labels[i], activity)
    })
    button.appendChild(arrow)
  }
}
function add_three_buttons(buttonGroup: HTMLDivElement, activity: any, event_handler: (direction:string, activity:any) => void) {
  // ToDo: Refactor two arrow and three arrow button groups to be single method
  // This is to support text flow functionality so need specific icons for that - not arrows
  const labels: [string, string][] = [
    ["RFLOW", "arrow-bar-right"],
    ["CENTRE", "arrows"],
    ["LFLOW", "arrow-bar-left"]  // These values correspond to value in database so can't change.
  ]

  for (let i = 0; i < 3; i++) {
    const [flow_direction, icon_name] = labels[i]
    console.log(`Adding button for flow control ${flow_direction}, icon ${icon_name}`)

    // Add button and appropriate arrow icon to supplied element.
    let button = document.createElement("button")
    button.classList.add("btn", "btn-secondary")
    if (activity.visual_data.text_flow == flow_direction) {
      button.classList.add("active")
    }
    buttonGroup.appendChild(button)

    let icon = document.createElement('i')
    icon.classList.add("bi", "bi-"+icon_name)
    icon.id = `${activity.visual_data.unique_id_from_plan}-[${flow_direction}]`
    icon.addEventListener('click', async function (e) {
      let btns = buttonGroup.querySelectorAll('.btn');
      btns.forEach((b) => {
        b.classList.remove('active')
      });

      // Add 'active' class to the clicked button
      const target_element: HTMLElement = e.target as HTMLElement
      const parent_target_element: HTMLElement = target_element.parentElement as HTMLButtonElement
      console.log(`Updating active button for text flow for ${parent_target_element}`)
      parent_target_element.classList.add('active');
      event_handler(flow_direction, activity)
    })
    button.appendChild(icon)
  }
}

function set_up_down_button(td_element: Element, activity:any, aria_label: string, labels: string[], event_handler: (direction: string, activity: any) => void) {
  // Start by clearing the element.
  td_element.textContent = '';
  
  const buttonGroup = add_button_group(td_element, aria_label);
  add_two_arrow_buttons(buttonGroup, activity, labels, event_handler);
}

function add_text_flow_buttons(td_element: Element, activity: any, aria_label: string) {
  // Start by clearing the element.
  td_element.textContent = '';

  const buttonGroup = add_button_group(td_element, aria_label);
  add_three_buttons(buttonGroup, activity, add_modify_text_flow_event_handler)

}

function select_for_edit(activity_id:string, clear=false) {
  // Populates activity edit panel with values for supplied activity
  // The table where the fields for the activity are stored has a row for each value and a th and td for the name of the
  // field and value respectively.  The TD element has an id equal to the text name which matches the name of the field
  // in the structure where the data is stored.
  //
  // Also the top part of the table is for plan data (non-editable) and the lower part of the table is for visual data
  // which is editable.  So the two region as stored under separate tbody elements and treated slightly differently.
  //
  // Also highlights selected element on the visual

  console.log("Selected activity for edit: " + activity_id);

  // Populate each element with value for this activity
  const edit_plan_activity_td_elements = document.querySelectorAll('#layout-activity tbody#plan-activity-properties td')
  const edit_visual_activity_td_elements = document.querySelectorAll('#layout-activity tbody#visual-activity-properties td')

  // If clear is set then this usually means the user has selected an activity which is not currently in the visual so
  // the visual portion of the activity data panel needs to be cleared.
  if (clear) {
    // Clear all the visual related values (because this activity is in the plan but not in the visual).
    (window as any).selected_activity_id = undefined;
    edit_visual_activity_td_elements.forEach(element => {
      const key = element.id
      element.textContent = '';
    });
  }

  // Modify stored value of currently selected activity to allow processing of further clicks etc.
  (window as any).selected_activity_id = activity_id;

  // Find entry for the selected activity in the list.
  const activity = get_plan_activity(activity_id);
  console.log("Found entry for activity ", activity_id);

  // Populate each of the plan related fields (always do this)
  edit_plan_activity_td_elements.forEach(td_element => {
    const key = td_element.id;
    if (key in NonEditableDispatchTable) {
      NonEditableDispatchTable[key](td_element, activity.plan_data[key])
    } else {
      td_element.textContent = activity.plan_data[key];
    }
  });

  if (clear) {
    console.log("Clear is set - don't update visual fields (as this activity not in visual)")
  } else {
    // Now populate each of the visual related fields (only if activity is in the visual)
    edit_visual_activity_td_elements.forEach(td_element => {
      const key = td_element.id;
      let activity_field_val = activity.visual_data[key];
      console.log("Edit activity elements - id = " + key + ", value is " + activity_field_val)

      // For certain values we need to tweak the logic to populate the value, either because
      // - The field is an object which needs further decoding to extract value
      // - The field is editable so we need to update the input html element value, not the td directly.

      // For fields in the dispatch table call dispatch function which will populate the field.
      // Otherwise old if then else logic applies below.

      // Track number: Set the value of the spinner
      if (key === "vertical_positioning_value") {
        set_up_down_button(td_element, activity, 'Activity Vertical Position Control',["up", "down"], add_move_track_event_handler);
      } else if (key === "height_in_tracks") {
        set_up_down_button(td_element, activity, 'Activity Height Control', ["up", "down"], add_modify_track_height_event_handler)
      } else if (key === "text_flow") {
        add_text_flow_buttons(td_element, activity, 'Text Flow Control')
      } else if (key === "plotable_shape") {
        // Start by clearing the element before updating it for this activity.
        clearElement(td_element as HTMLElement)

        let button: HTMLButtonElement = createDropdown(
          td_element as HTMLElement,
          activity.visual_data[key].value
        );

        populateDropdown(
          button,
          (window as any).shape_data.map((obj: any) => [obj.name, obj.id]),
          async (shape_id: number) => {
            // Lookup shape name from id as that is what needs to be updated in the database
            const shape_name = (window as any).shape_data.find((obj: any) => obj.id === shape_id).name;

            await update_shape_for_activity_handler(activity_id, shape_name);
            await get_visual_activity_data((window as any).visual_id)

            // Need visual settings as it included visual height which is needed to plot.
            const response = await get_visual_settings((window as any).visual_id);
            (window as any).visual_settings = response.data

            plot_visual()
         }
       );
      } else if (key === "plotable_style") {
        // Start by clearing the element before updating it for this activity.
        clearElement(td_element as HTMLElement)

        let button: HTMLButtonElement = createDropdown(
          td_element as HTMLElement,
          activity.visual_data[key].style_name
        );

        populateDropdown(
          button,
          (window as any).style_data.map((obj: any) => [obj.style_name, obj.id]),
          async (style_id: number) => {
                    await update_style_for_activity_handler(activity_id, style_id);
                    await get_visual_activity_data((window as any).visual_id)

                    // Need visual settings as it included visual height which is needed to plot.
                    const response = await get_visual_settings((window as any).visual_id);
                    (window as any).visual_settings = response.data

                    plot_visual()
                 }
       );
      } else if (key === "swimlane") {
        // Start by clearing the element before updating it for this activity.
        clearElement(td_element as HTMLElement)

        let button: HTMLButtonElement = createDropdown(
          td_element as HTMLElement,
          activity.visual_data[key].swim_lane_name
        );

        populateDropdown(
          button,
          (window as any).swimlane_data.map((obj: any) => [obj.swim_lane_name, obj.id]),
          async (swimlane_id: number) => {
                    await update_swimlane_for_activity_handler(activity_id, swimlane_id);
                    await get_plan_activity_data((window as any).visual_id)
                    await get_visual_activity_data((window as any).visual_id)

                    // Need visual settings as it included visual height which is needed to plot.
                    const response = await get_visual_settings((window as any).visual_id);
                    (window as any).visual_settings = response.data

                    plot_visual()
                 }
       );
      } else {
        td_element.textContent = activity_field_val;
      }
    });
    highlight_activity(activity_id)
  }
}

async function manage_plan_activity_click(activity: any, activityDiv: HTMLDivElement, topLevelElements: any) {
  // If this element isn't already the current one, then make it the current one.
  // If it is already the current one, then this click will toggle its inclusion in the visual.
  if (activityDiv.classList.contains('current')) {
    console.log("Toggle inclusion in visual: " + activity.plan_data.unique_sticky_activity_id);
    const inVisual = activityDiv.classList.toggle('in-visual')
    if (inVisual) {
      // Means we have just toggled it to in so need to add it
      await add_to_visual(activity.plan_data.unique_sticky_activity_id, (window as any).default_swimlane_seq_num)
      await get_visual_activity_data((window as any).visual_id)  // Refresh data from server before replotting
      await get_plan_activity_data((window as any).visual_id)  // Refresh data from server before replotting

      // Need visual settings as it included visual height which is needed to plot.
      const response = await get_visual_settings((window as any).visual_id);
      (window as any).visual_settings = response.data

      plot_visual()

      // Now it is in the visual and current activity we should select it for edit.
      select_for_edit(activity.plan_data.unique_sticky_activity_id)
    } else {
      // Means we have just toggled it to not in so need to remove it
      await remove_from_visual(activity.plan_data.unique_sticky_activity_id)
      await get_visual_activity_data((window as any).visual_id)  // Refresh data from server before replotting

      // Need visual settings as it included visual height which is needed to plot.
      const response = await get_visual_settings((window as any).visual_id);
      (window as any).visual_settings = response.data

      plot_visual()

      // As not in visual we can't edit it so need to clear out the visual elements and update the plan elements
      select_for_edit(activity.plan_data.unique_sticky_activity_id, true)
    }
  } else {
    // We have just selected an activity which wasn't already selected so need to change this one to the current
    // element and, if this activity is in the visual, update the activity panel to details for this activity.
    // If this activity is not in the visual then we need to clear the activity panel
    const selected = topLevelElements[0].getElementsByClassName('current')
    if (selected.length > 0) {
      selected[0].classList.remove('current');
    }
    activityDiv.classList.add('current');

    if (activityDiv.classList.contains('in-visual')) {
      select_for_edit(activity.plan_data.unique_sticky_activity_id)
    } else {
      select_for_edit(activity.plan_data.unique_sticky_activity_id, true)
    }
  }
}

export async function update_activity_track(activity_unique_id: any, direction:string) {
  // Need to get activity from global data - to ensure we get latest version.
  const activity = get_plan_activity(activity_unique_id)

  console.log(`update_activity_track: activity=${activity}, direction=${direction}`)
  console.log(`update_activity_track: activity.visual_data=${activity.visual_data}`)
  console.log(`update_activity_track: activity.visual_data.id=${activity.visual_data.id}`)

  const delta = direction === "down" ? 1 : (direction === "up" ? -1 : 0);
  console.log(`delta: ${delta}`)

  // Calculate new position - but don't allow track number to get below 1
  const new_vertical_position = Math.max(activity.visual_data.vertical_positioning_value + delta, 1)
  console.log(`new vertical value: ${new_vertical_position}`)
  const data = [
    {
      id: activity.visual_data.id,
      vertical_positioning_value: new_vertical_position
    }
  ]
  await update_visual_activities(activity.visual_data.visual.id, data)
}

export async function update_activity_track_height(activity_unique_id:string, direction:string) {
  // Need to get activity from global data - to ensure we get latest version.
  const activity = get_plan_activity(activity_unique_id)

  console.log(`update_activity_track_height: activity=${activity}, direction=${direction}`)
  console.log(`update_activity_track_height: activity.visual_data=${activity.visual_data}`)
  console.log(`update_activity_track_height: activity.visual_data.id=${activity.visual_data.id}`)

  const delta = direction === "increase" ? 1 : (direction === "decrease" ? -1 : 0);
  console.log(`delta: ${delta}`)
  // Calculate new height, but can't be less than 1
  const new_track_height = Math.max(activity.visual_data.height_in_tracks + delta, 1)
  console.log(`new vertical value: ${new_track_height}`)
  const data = [
    {
      id: activity.visual_data.id,
      height_in_tracks: new_track_height
    }
  ]
  await update_visual_activities(activity.visual_data.visual.id, data)
}

export async function update_activity_text_flow(activity_unique_id:string, flow_direction:string) {
  // Need to get activity from global data - to ensure we get latest version.
  const activity = get_plan_activity(activity_unique_id)

  console.log(`update_activity_text_flow: activity=${activity}, direction=${flow_direction}`)
  console.log(`update_activity_text_flow: activity.visual_data=${activity.visual_data}`)
  console.log(`update_activity_text_flow: activity.visual_data.id=${activity.visual_data.id}`)

  const data = [
    {
      id: activity.visual_data.id,
      text_flow: flow_direction
    }
  ]
  await update_visual_activities(activity.visual_data.visual.id, data)
}
