// Functionality to manage the main edit visual page of the app.
// The id of the visual is set to the id of the body element in the page by the Django app.
// The edit visual page is purely Ajax driven and each element of the page is updated by calling
// the API to the Django app to get the data required to populate the page.

import {add_activity_to_visual, get_visual_activity_data, remove_activity_from_visual} from "./plan_visualiser_api";
import {toggle_expansion} from "./manage_plan_panel";
import {plot_visual} from "./plot_visual";

export async function createPlanTree() {
  let topLevelElements = [document.createElement('ul')]
  topLevelElements[0].setAttribute("id", "plan-activities");

  // We want lowest level to be 1 as various things depend on it (including color-coding)
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
      // If this element isn't already the current one, then make it the current one.
      // If it is already the current one, then this click will toggle its inclusion in the visual.
      if (activityDiv.classList.contains('current')) {
        console.log("Toggle inclusion in visual: " + activity.plan_data.unique_sticky_activity_id);
        const inVisual = activityDiv.classList.toggle('in-visual')
        if (inVisual) {
          // Means we have just toggled it to in so need to add it
          add_to_visual(activity.plan_data.unique_sticky_activity_id)
          await get_visual_activity_data((window as any).visual_id)  // Refresh data from server before replotting
          plot_visual()

          // Now it is in the visual and current activity we should select it for edit.
          select_for_edit(activity.plan_data.unique_sticky_activity_id)
        } else {
          // Means we have just toggled it to not in so need to remove it
          remove_from_visual(activity.plan_data.unique_sticky_activity_id)
          await get_visual_activity_data((window as any).visual_id)  // Refresh data from server before replotting

          // As not in visual we can't edit it so need to clear out activity edit panel
          select_for_edit(activity.plan_data.unique_sticky_activity_id, true)

          plot_visual()
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
    })

    if (i < (window as any).plan_activity_data.length - 1) {
      if ((window as any).plan_activity_data[i + 1].plan_data.level + level_adjust > level) {
        // This is the last at this level before we drop a level so need to add an expand icon and expand class
        const expandIcon = document.createElement('i');
        li.setAttribute('class', 'expandNode');

        expandIcon.setAttribute('class', 'fa-solid fa-circle-plus');
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

function add_to_visual(activity_id: string) {
  add_activity_to_visual((window as any).visual_id, activity_id)
  console.log("Added activity to visual: " + activity_id);
  const activity = get_activity(activity_id)
  activity.enabled = true;
}

function remove_from_visual(activity_id: string) {
  remove_activity_from_visual((window as any).visual_id, activity_id)
  console.log("Removed activity from visual: " + activity_id);
  const activity = get_activity(activity_id)
  activity.enabled = false;
}

function get_activity(activity_id:string) {
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

function select_for_edit(activity_id:string, clear=false) {
  // Populates activity edit panel with values for supplied activity

  console.log("Selected activity for edit: " + activity_id);

  // Populate each element with value for this activity
  const edit_activity_elements = document.querySelectorAll('#layout-activity tbody td')
  // If clear flag is set we just clear all the values.
  if (clear) {
    (window as any).selected_activity_id = undefined;
    edit_activity_elements.forEach(element => {
      const key = element.id
      if (key === "track") {
        console.log("Element is track - setting input value to blank")
        const input_element = element.getElementsByTagName('input')[0]
        input_element.value = "0";
      } else {
        element.textContent = '';
      }
    });
  } else {
    (window as any).selected_activity_id = activity_id;
    const activity = get_activity(activity_id)
    console.log("Found html element for activity ", activity_id)

    // Each element in edit_activity_elements will have an id which corresponds to a key in this activity.
    edit_activity_elements.forEach(element => {
      const key = element.id;

      // Some fields are part of the plan data, others part of visual data. Indicated by class of visual or plan.  So
      // work out which and extract field value for this activity accordingly.
      let source = undefined
      if (element.classList.contains('visual')) {
        source = 'visual';
      } else if (element.classList.contains('plan')) {
        source = 'plan';
      }

      let activity_field_val = undefined
      if (source === 'visual') {
        activity_field_val = activity.visual_data[key]
      } else {
        activity_field_val = activity.plan_data[key];
      }
      console.log("Edit activity elements - id = " + key + ", value is " + activity_field_val)
      // If this is track number then set the value of the spinner, otherwise text content.
      if (key === "vertical_positioning_value") {
        console.log("Element is track - setting input value to " + activity_field_val)
        const input_element = element.getElementsByTagName('input')[0]
        input_element.value = activity_field_val;
      } else if (key === "swimlane") {
        element.textContent = activity_field_val.swim_lane_name
      } else {
        element.textContent = activity_field_val;
      }
    });
  }
  // Need to redraw as different element needs to be marked as selected
  plot_visual()
}
