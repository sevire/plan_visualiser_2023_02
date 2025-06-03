export function toggle_expansion(node:HTMLLIElement) {
  // Passed an li element which has child elements encapsulated in a ul.  So when toggled hide or unhide the ul
  // Also need to toggle the icon - for expanded it's a minus, for unexpanded it's a plus.

  const expanded = node.classList.contains('expand')
  if (expanded) {
    // Current icon will be a minus, replace with a plus.
    const oldIcon = node.querySelector('div>i')
    oldIcon?.setAttribute('class', 'bi bi-plus-circle-fill')
    // oldIcon.textContent = "+"; // Temp
  } else {
    // Current icon will be a minus, replace with a plus.
    const oldIcon = node.querySelector('div>i')
    oldIcon?.setAttribute('class', 'bi bi-dash-circle-fill')
    // oldIcon.textContent = "-"; // Temp
  }
  // Now toggle the class
  node.classList.toggle('expand');
}

function get_activity(activity_id: string) {
  let found_value: any;
  (window as any).plan_activity_data.forEach((activity: any) => {
    if (typeof found_value === 'undefined') {
      if (activity.activity_id === activity_id) {
        found_value = activity
      }
    }
  })
  return found_value
}


export function change_track_value(event: Event) {
  // Need to get value from the event target (input) and the activity id from the td (parent)
  const new_track_value = (event.target as HTMLInputElement).value;
  const activity = get_activity((window as any).selected_activity_id)
  if (activity) {
    activity.track = new_track_value;
  } else {
    console.log("Can't find activity");
  }
}
