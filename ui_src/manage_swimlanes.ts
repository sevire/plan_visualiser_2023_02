import {get_swimlane_data, remove_activity_from_visual} from "./plan_visualiser_api";

export async function update_swimlane_data(swimlane_html_panel:HTMLElement, visual_id: number) {
  await get_swimlane_data(visual_id)

  // Find the tbody element within the swimlane table, then add a row for each swimlane.
  const tbody = swimlane_html_panel.querySelector("table tbody");
  (window as any).swimlane_data.forEach((swimlane_record: any) => {
    // Add row to tbody with two td's, one for an up and down arrow and one for swimlane name
          // Create a new row
      let row = document.createElement('tr');

      // Create a cell for arrows
      let arrowCell = document.createElement('td');
      arrowCell.classList.add("arrow")
      arrowCell.innerHTML = '<i class="fa-solid fa-circle-chevron-up"></i><i class="fa-solid fa-circle-chevron-down"></i>';
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