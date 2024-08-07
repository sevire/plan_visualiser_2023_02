// Functionality to manage the main edit visual page of the app.
// The id of the visual is set to the id of the body element in the page by the Django app.
// The edit visual page is purely Ajax driven and each element of the page is updated by calling
// the API to the Django app to get the data required to populate the page.

import {
  add_activity_to_visual, get_plan_activity_data,
  get_visual_activity_data,
  remove_activity_from_visual, update_visual_activities
} from "./plan_visualiser_api";
import {toggle_expansion} from "./manage_plan_panel";
import {plot_visual} from "./plot_visual";
import {Dropdown} from "./widgets";
import {
  add_arrow_button_to_element,
  update_swimlane_for_activity_handler,
  update_swimlane_order
} from "./manage_swimlanes";
import {update_style_for_activity_handler} from "./manage_styles";
import {update_shape_for_activity_handler} from "./manage_shapes";

export async function createPlanTree() {
  let topLevelUL = document.createElement('ul');
  topLevelUL.classList.add("bg-primary-subtle")
  let topLevelElements = [topLevelUL]
  topLevelElements[0].setAttribute("id", "plan-activities");

  // We want the lowest level to be 1 as various things depend on it (including color-coding)
  const level_adjust = 1 - (window as any).plan_activity_data[0].plan_data.level
  let previousLevel = 1;

  for (let i = 0; i < (window as any).plan_activity_data.length; i++) {
    const activity = (window as any).plan_activity_data[i];
    const level = activity.plan_data.level + level_adjust
    console.log("(New) Processing activity: " + activity.plan_data.activity_name + ", level: " + level)
    const activity_text = activity.plan_data.activity_name + ", Level " + level
    const level_class = "level-" + level
    const li = document.createElement('li');

    // Put activity text into a div under the li to help style independently of ul/li structure.
    const activityDiv = document.createElement("div")
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
  }

  console.log("topLevelElements before return", topLevelElements)
  return topLevelElements[0];
}

async function add_to_visual(activity_id: string) {
  await add_activity_to_visual((window as any).visual_id, activity_id)
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
  console.log(`Track number up clicked`)
  console.log(`Activity is ${activity}`)
  await update_activity_track(activity.visual_data.unique_id_from_plan, direction)
  await get_plan_activity_data((window as any).visual_id)
  await get_visual_activity_data((window as any).visual_id)
  plot_visual()
}

async function add_modify_track_height_event_handler(direction: string, activity: any) {
  console.log(`Track height ${direction} clicked`)
  console.log(`Activity is ${activity}`)
  await update_activity_track_height(activity.visual_data.unique_id_from_plan, direction)
  await get_plan_activity_data((window as any).visual_id)
  await get_visual_activity_data((window as any).visual_id)
  plot_visual()
}

function select_for_edit(activity_id:string, clear=false) {
  // Populates activity edit panel with values for supplied activity

  console.log("Selected activity for edit: " + activity_id);

  // Populate each element with value for this activity
  const edit_activity_td_elements = document.querySelectorAll('#layout-activity tbody td')
  if (clear) {
    // Clear all the visual related values (because this activity is in the plan but not in the visual).
    (window as any).selected_activity_id = undefined;
    edit_activity_td_elements.forEach(element => {
      if (element.classList.contains('visual')) {
        const key = element.id
        element.textContent = '';
      }
    });
  }

  // Set the values to appropriate plan or activity value.  If clear is set then we are only setting the plan values
  // For visual activity values - the cell needs to be editable.

  // Modify stored value of currently selected activity to allow processing of further clicks etc.
  (window as any).selected_activity_id = activity_id;

  // Find entry for the selected activity in the list.
  const activity = get_plan_activity(activity_id)
  console.log("Found entry for activity ", activity_id)

  // Each element in edit_activity_elements will have an id which corresponds to a key in this activity.
  edit_activity_td_elements.forEach(td_element => {
    console.log(`Updating fields ${edit_activity_td_elements}`)
    const key = td_element.id;

    // Some fields are part of the plan data, others part of visual data. Indicated by class of visual or plan.  So
    // work out which and extract field value for this activity accordingly.
    let source = undefined
    if (td_element.classList.contains('visual')) {
      source = 'visual';
    } else if (td_element.classList.contains('plan')) {
      source = 'plan';
    }

    // Always update plan values, only update visual values if we are not clearing - otherwise we will have cleared them
    if (source === "plan" || !clear) {
      let activity_field_val
      if (source === 'visual') {
        activity_field_val = activity.visual_data[key]
      } else {
        activity_field_val = activity.plan_data[key];
      }
      console.log("Edit activity elements - id = " + key + ", value is " + activity_field_val)

      // For certain values we need to tweak the logic to populate the value, either because
      // - The field is an object which needs further decoding to extract value
      // - The field is editable so we need to update the input html element value, not the td directly.

      // Track number: Set the value of the spinner
      if (key === "vertical_positioning_value") {
        // Start by clearing the element.
        td_element.textContent = '';

        // Add up and down arrows to the td element and add click event handler which updates activity vertical position.
        const buttonGroup = document.createElement("div");
        buttonGroup.classList.add("btn-group", "btn-group-sm", "up-down-control", "me-1");
        buttonGroup.setAttribute('role', 'group');
        buttonGroup.setAttribute('aria-label', 'Activity Vertical Position Control');
        td_element.appendChild(buttonGroup)

        let direction: string
        for (let i = 0; i < 2; i++) {
          if (i == 0) {
            direction = "up"
          } else {
            direction = "down"
          }
          // Add button and appropriate arrow icon to supplied element.
          let button = document.createElement("button")
          button.classList.add("btn", "btn-secondary")
          buttonGroup.appendChild(button)

          let arrow = document.createElement('i')
          arrow.classList.add("bi", "bi-caret-" + direction + "-fill")
          arrow.id = `${activity.visual_data.unique_id_from_plan}-[${direction}]`
          if (direction == "up") {
            arrow.addEventListener('click', async function() {
              add_move_track_event_handler("up", activity)
            })
          } else {
            arrow.addEventListener('click', async function() {
              add_move_track_event_handler("down", activity)
            })
          }
          button.appendChild(arrow)
        }
      } else if (key === "height_in_tracks") {
        // Start by clearing the element.
        td_element.textContent = '';

        // Add up and down arrows to the td element and add click event handler which modifies height of activity.
        const buttonGroup = document.createElement("div");
        buttonGroup.classList.add("btn-group", "btn-group-sm", "height-control", "me-1");
        buttonGroup.setAttribute('role', 'group');
        buttonGroup.setAttribute('aria-label', 'Activity Height Control');
        td_element.appendChild(buttonGroup)

        let direction: string;
        for (let i = 0; i < 2; i++) {
          if (i == 0) {
            direction = "up"
          } else {
            direction = "down"
          }
          // Add button and appropriate arrow icon to supplied element.
          let button = document.createElement("button")
          button.classList.add("btn", "btn-secondary")
          buttonGroup.appendChild(button)

          let arrow = document.createElement('i')
          arrow.classList.add("bi", "bi-caret-" + direction + "-fill")
          arrow.id = `${activity.visual_data.unique_id_from_plan}-[${direction}]`
          if (direction == "up") {
            arrow.addEventListener('click', async function () {
              add_modify_track_height_event_handler("increase", activity)
            })
          } else {
            arrow.addEventListener('click', async function () {
              add_modify_track_height_event_handler("decrease", activity)
            })
          }
          button.appendChild(arrow)
        }
      } else if (key === "plotable_shape") {
        // Start by clearing the element before updating it for this activity.
        td_element.textContent = '';

        let shape_names: [[string, number]] = (window as any).shape_data.map((obj:any) => [obj.name, obj.id]);
        // Add div for Bootstrap Dropdown
        const dropdownDiv = document.createElement("div")
        dropdownDiv.classList.add("dropdown")
        td_element.appendChild(dropdownDiv)

        // Add button to Dropdown
        const dropdownButton = document.createElement("button")
        dropdownButton.setAttribute("type", "button")
        dropdownButton.setAttribute("data-bs-toggle", "dropdown")
        dropdownButton.setAttribute("aria-expanded", "false")
        dropdownButton.classList.add("btn", "btn-sm", "btn-secondary", "dropdown-toggle")
        dropdownButton.textContent = "Change Shape"
        dropdownDiv.appendChild(dropdownButton)

        // Add dropdown menu to Dropdown
        const dropdownMenu = document.createElement("ul")
        dropdownMenu.classList.add("dropdown-menu")
        dropdownDiv.appendChild(dropdownMenu)

        // Add dropdown entry for each swimlane associated with this visual
        shape_names.forEach((shape_name: [string, number]) => {
          const shapeEntry = document.createElement('li');
          shapeEntry.classList.add("dropdown-item")
          shapeEntry.setAttribute("href", "#")
          shapeEntry.setAttribute("id", String(shape_name[1]))
          shapeEntry.textContent = shape_name[0];

          shapeEntry.addEventListener('click', async function (event) {
            console.log(`New shape selected for element, ${event.target}`)
            const targetSelectedElement = event.target as HTMLLIElement;
            const shape_id = parseInt(targetSelectedElement.id);
            console.log(`Shape selected: text:${targetSelectedElement.textContent}, id:${shape_id}`);

            await update_shape_for_activity_handler(activity_id, shape_id);
            await get_visual_activity_data((window as any).visual_id)
            plot_visual()
          })
          dropdownMenu.appendChild(shapeEntry);
        });
      } else if (key === "plotable_style") {
        // Start by clearing the element before updating it for this activity.
        td_element.textContent = '';

        let style_names: [[string, number]] = (window as any).style_data.map((obj:any) => [obj.style_name, obj.id]);

        // Add div for Bootstrap Dropdown
        const dropdownDiv = document.createElement("div")
        dropdownDiv.classList.add("dropdown")
        td_element.appendChild(dropdownDiv)

        // Add button to Dropdown
        const dropdownButton = document.createElement("button")
        dropdownButton.setAttribute("type", "button")
        dropdownButton.setAttribute("data-bs-toggle", "dropdown")
        dropdownButton.setAttribute("aria-expanded", "false")
        dropdownButton.classList.add("btn", "btn-sm", "btn-secondary", "dropdown-toggle")
        dropdownButton.textContent = "Change Style"
        dropdownDiv.appendChild(dropdownButton)

        // Add dropdown menu to Dropdown
        const dropdownMenu = document.createElement("ul")
        dropdownMenu.classList.add("dropdown-menu")
        dropdownDiv.appendChild(dropdownMenu)

        // Add dropdown entry for each swimlane associated with this visual
        console.log(`Adding style names in change style dropdown ${style_names}`)
        style_names.forEach((style_name: [string, number]) => {
          console.log(`Adding dropdown item for ${style_name}`)

          const styleEntry = document.createElement('li');
          styleEntry.classList.add("dropdown-item")
          styleEntry.setAttribute("href", "#")
          styleEntry.setAttribute("id", String(style_name[1]))
          styleEntry.textContent = style_name[0];

          styleEntry.addEventListener('click', async function (event) {
            console.log(`New style selected for element, ${event.target}`)
            const targetSelectedElement = event.target as HTMLLIElement;
            const style_id = parseInt(targetSelectedElement.id);
            console.log(`Shape selected: text:${targetSelectedElement.textContent}, id:${style_id}`);

            await update_style_for_activity_handler(activity_id, style_id);
            await get_visual_activity_data((window as any).visual_id)
            plot_visual()
          })
          dropdownMenu.appendChild(styleEntry);
        });
      } else if (key === "swimlane") {
        // Start by clearing the element before updating it for this activity.
        td_element.textContent = "";

        let swimlane_names: [[string, number]] = (window as any).swimlane_data.map((obj:any) => [obj.swim_lane_name, obj.id]);
        // Add div for Bootstrap Dropdown
        const dropdownDiv = document.createElement("div")
        dropdownDiv.classList.add("dropdown")
        td_element.appendChild(dropdownDiv)

        // Add button to Dropdown
        const dropdownButton = document.createElement("button")
        dropdownButton.setAttribute("type", "button")
        dropdownButton.setAttribute("data-bs-toggle", "dropdown")
        dropdownButton.setAttribute("aria-expanded", "false")
        dropdownButton.classList.add("btn", "btn-sm", "btn-secondary", "dropdown-toggle")
        dropdownButton.textContent = "Change Swimlane"
        dropdownDiv.appendChild(dropdownButton)

        // Add dropdown menu to Dropdown
        const dropdownMenu = document.createElement("ul")
        dropdownMenu.classList.add("dropdown-menu")
        dropdownDiv.appendChild(dropdownMenu)

        // Add dropdown entry for each swimlane associated with this visual
        swimlane_names.forEach((swimlane_name: [string, number]) => {
          const swimlaneEntry = document.createElement('li');
          swimlaneEntry.classList.add("dropdown-item")
          swimlaneEntry.setAttribute("href", "#")
          swimlaneEntry.setAttribute("id", String(swimlane_name[1]))
          swimlaneEntry.textContent = swimlane_name[0];

          swimlaneEntry.addEventListener('click', async function (event) {
            console.log(`New swimlane selected for element, ${event.target}`)
            const targetSelectedElement = event.target as HTMLLIElement;
            const swimlane_id = parseInt(targetSelectedElement.id);
            console.log(`Swimlane selected: text:${targetSelectedElement.textContent}, id:${swimlane_id}`);

            await update_swimlane_for_activity_handler(activity_id, swimlane_id);
            await get_visual_activity_data((window as any).visual_id)
            plot_visual()
          })
          dropdownMenu.appendChild(swimlaneEntry);
        });
      } else {
        td_element.textContent = activity_field_val;
      }
    }
  });

  // Need to redraw as different element needs to be marked as selected
  plot_visual()
}

async function manage_plan_activity_click(activity: any, activityDiv: HTMLDivElement, topLevelElements: any) {
      // If this element isn't already the current one, then make it the current one.
      // If it is already the current one, then this click will toggle its inclusion in the visual.
      if (activityDiv.classList.contains('current')) {
        console.log("Toggle inclusion in visual: " + activity.plan_data.unique_sticky_activity_id);
        const inVisual = activityDiv.classList.toggle('in-visual')
        if (inVisual) {
          // Means we have just toggled it to in so need to add it
          await add_to_visual(activity.plan_data.unique_sticky_activity_id)
          await get_visual_activity_data((window as any).visual_id)  // Refresh data from server before replotting

          plot_visual()

          // Now it is in the visual and current activity we should select it for edit.
          select_for_edit(activity.plan_data.unique_sticky_activity_id)
        } else {
          // Means we have just toggled it to not in so need to remove it
          await remove_from_visual(activity.plan_data.unique_sticky_activity_id)
          await get_visual_activity_data((window as any).visual_id)  // Refresh data from server before replotting

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
