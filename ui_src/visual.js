import axios from 'axios';
import { plot_visual } from "./plot_shapes";
import { initialise_canvas } from "./drawing";
var return_data;
export function get_activity_data() {
    let json_activities = document.getElementById("json_activities");
    console.log("json_activities - " + json_activities);
    if (json_activities.textContent == null) {
        return {};
    }
    else {
        return JSON.parse(json_activities.textContent);
    }
}
export function get_activities_from_server(visual_id) {
    axios.defaults.xsrfCookieName = 'csrftoken';
    axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
    var url_string = `/api/v1/visual_activities/${visual_id}/`;
    axios.get(url_string)
        .then((response) => {
        return_data = response.data;
        load_activities(JSON.parse(return_data));
    })
        .catch(error => {
        console.log("Error...");
        console.log(error);
    });
}
export function get_activity(visual_id, unique_activity_id) {
    axios.defaults.xsrfCookieName = 'csrftoken';
    axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
    var url_string = `/api/v1/visual_activities/${visual_id}/${unique_activity_id}`;
    axios.get(url_string)
        .then((response) => {
        return_data = response.data;
        loadActivity(JSON.parse(return_data));
    })
        .catch(error => {
        console.log("Error...");
        console.log(error);
    });
}
export function load_activities(activities) {
    console.log("loading activities");
    // Gets activities for the visual from server and loads them into activities table on the page
    console.log(activities);
    let activities_table = document.getElementById("activities_table");
    activities_table.innerHTML = "";
    for (let activity of activities) {
        let row = activities_table.insertRow();
        row.onclick = (e) => {
            let element = e.target;
            let row_element = element.closest("tr");
            console.log("element clicked...");
            console.log(row_element);
            selectRow(row_element);
        };
        let cell = row.insertCell();
        cell.innerHTML = activity.activity_name;
        cell = row.insertCell();
        cell.innerHTML = activity.unique_id_from_plan;
        cell.hidden = true;
        cell.classList.add("unique_id");
    }
    // Select first row
    selectRowByIndex(1);
}
export function loadActivity(activity_data) {
    // Passed in activity data (obtained from server) and update activity information on this page
    let activities_table = document.getElementById("layout_activities");
    activities_table.innerHTML = "";
    for (const key in activity_data) {
        // Key will be the field name, value will be the field value
        console.log(`Adding row for ${key}:${activity_data[key]}`);
        let row = activities_table.insertRow();
        let field_cell = row.insertCell();
        field_cell.innerHTML = key;
        let value_cell = row.insertCell();
        // If this is the vertical positioning value then make it editable and update activity when it changes
        if (key === "vertical_positioning_value") {
            let input_element = document.createElement("input");
            input_element.value = activity_data[key];
            input_element.type = "number";
            value_cell.appendChild(input_element);
            const visual_id = document.getElementsByTagName("body")[0].id;
            input_element.onchange = (e) => {
                let vertical_position_element = e.target;
                console.log(`vertical_position_element: ${vertical_position_element}`);
                let vertical_position = +vertical_position_element.value;
                console.log(`vertical_position: ${vertical_position}`);
                let data = {
                    "vertical_positioning_value": vertical_position
                };
                console.log(`data: ${data}`);
                console.log(`id from body is ${visual_id}`);
                let url_string = `/api/v1/visual_activities/update/${visual_id}/${activity_data.unique_id_from_plan}/`;
                axios.patch(url_string, data)
                    .then((response) => {
                    const visual = get_rendered_visual(+visual_id);
                })
                    .catch(error => {
                    console.log("Error...");
                    console.log(error);
                });
            };
        }
        else {
            value_cell.innerHTML = activity_data[key];
        }
    }
    // Plot visual
    const visual_id = document.getElementsByTagName("body")[0].id;
    get_rendered_visual(+visual_id);
}
export function selectRow(tr) {
    // Need to find which row is currently selected and deselect it.
    // Then select the new row.
    console.log("selectRow called...");
    console.log(tr);
    let layout_table = document.getElementById("activities_table");
    console.log("layout_table: " + layout_table);
    let currentRow = layout_table.getElementsByClassName("selected")[0];
    console.log("currentRow: " + currentRow);
    if (currentRow !== undefined) {
        currentRow.classList.remove("selected");
    }
    tr.classList.add("selected");
    updateActivity(tr.rowIndex);
}
export function selectRowByIndex(row_index) {
    // Set row at row_index as selected
    console.log("selectRowByIndex called...");
    console.log(row_index);
    let layout_table = document.getElementById("activities_table");
    console.log("layout_table: " + layout_table);
    let indexed_row = layout_table.rows[row_index - 1];
    return selectRow(indexed_row);
}
export function move(direction) {
    // Move the selected activity in the specified direction
    console.log("move called with direction: " + direction);
    let layout_table = document.getElementById("activities_table");
    let selectedRowList = layout_table.getElementsByClassName("selected");
    let selectedRow;
    let newRow;
    if (selectedRowList.length === 0) {
        // No row is currently selected so select the first row
        newRow = layout_table.firstChild;
        newRow.classList.add("selected");
    }
    else {
        selectedRow = selectedRowList[0];
        selectedRow.classList.remove("selected");
        let selectedRowIndex = selectedRow.rowIndex;
        if (direction === "up") {
            if (selectedRowIndex === 0) {
                newRow = layout_table.rows[0];
            }
            else {
                newRow = selectedRow.previousSibling;
            }
            newRow.classList.add("selected");
            console.log("newRow: " + newRow);
            updateActivity(newRow.rowIndex);
        }
        else if (direction === "down") {
            if (selectedRowIndex === layout_table.rows.length - 1) {
                newRow = layout_table.rows[layout_table.rows.length - 1];
            }
            else {
                newRow = selectedRow.nextSibling;
            }
            newRow.classList.add("selected");
            console.log("newRow: " + newRow);
            updateActivity(newRow.rowIndex);
        }
    }
}
export function getIdFromRowIndex(row_index) {
    let layout_table = document.getElementById("activities_table");
    let activity_row = layout_table.rows[row_index];
    return activity_row.getElementsByClassName("unique_id")[0].innerHTML;
}
export function updateActivity(row_index) {
    console.log(`UpdateActivity called for activity row ${row_index}`);
    let activity_id = getIdFromRowIndex(row_index);
    console.log(`UpdateActivity called for activity id ${activity_id}`);
    let visual_id = document.getElementsByTagName("body")[0].id;
    get_activity(visual_id, activity_id);
}
export function checkKey(event) {
    let layout_table;
    let currentRow;
    let newRow;
    if (event.keyCode === 38) {
        // up arrow
        move("up");
    }
    else if (event.keyCode === 40) {
        // down arrow
        move("down");
    }
}
export function update_server_visual_activity(visual_id, activity_id, activity_data) {
    axios.defaults.xsrfCookieName = 'csrftoken';
    axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
    var url_string = `/api/v1/visual_activities/${visual_id}/${activity_id}`;
    axios.put(url_string, activity_data)
        .then((response) => {
        return_data = response.data;
        loadActivity(JSON.parse(return_data));
    })
        .catch(error => {
        console.log("Error...");
        console.log(error);
    });
}
export function get_rendered_visual(visual_id) {
    axios.defaults.xsrfCookieName = 'csrftoken';
    axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
    var url_string = `/api/v1/visual_activities/rendered/${visual_id}/`;
    axios.get(url_string)
        .then((response) => {
        let visual = JSON.parse(response.data);
        console.log("visual: " + visual);
        let visual_settings = visual.settings;
        console.log("visual_settings: " + visual_settings);
        const visual_activities = visual['shapes'];
        console.log("visual_activities: " + visual_activities);
        let context = initialise_canvas(visual_settings);
        plot_visual(context, visual_activities, visual_settings);
    })
        .catch(error => {
        console.log("Error...");
        console.log(error);
    });
}
