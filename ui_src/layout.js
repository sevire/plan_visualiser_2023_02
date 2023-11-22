async function initialise_layout() {
  // Populates the layout section with the activities in the layout.
  // This is called when the page is loaded, and when the layout is changed.
  console.log("initialise_layout called")

  let layout_table = document.getElementById("layout_table")

  const response = await fetch("js/visual_data.json");
  const visual_data = await response.json();

  console.log("visual_data: " + visual_data)
  let shape_data = visual_data.shape_data
  let shape;
  for (let i = 0; i < shape_data.length; i++) {
    // Create a row for each activity with a td for the activity name and a hidden td for the activity id.
    shape = shape_data[i]
    let activity_name = shape.activity_name
    let table_row = layout_table.appendChild(document.createElement("tr"))
    table_row.onclick = function () {
      selectRow(this)
    }

    let activity_id_cell = table_row.appendChild(document.createElement("td"))
    activity_id_cell.classList.add("activity_id")
    activity_id_cell.hidden = true
    activity_id_cell.id = shape.id

    let activity_name_cell = table_row.appendChild(document.createElement("td"))
    activity_name_cell.classList.add("activity_name")
    activity_name_cell.innerHTML = activity_name

    if (i === 0) {
      table_row.className = "selected"
    }
  }
  updateActivity(0)
}


function selectRow(tr) {
  // Need to find which row is currently selected and deselect it.
  // Then select the new row.
  console.log("selectRow called")
  let layout_table = document.getElementById("layout_table")
  console.log("layout_table: " + layout_table)
  let currentRow = layout_table.getElementsByClassName("selected")[0]
  console.log("currentRow: " + currentRow)
  currentRow.classList.remove("selected")

  tr.classList.add("selected")
  updateActivity(tr.rowIndex)

}

function move(direction) {
  // Move the selected activity in the specified direction
  console.log("move called with direction: " + direction)
  let layout_table = document.getElementById("layout_table")
  let selectedRowList = layout_table.getElementsByClassName("selected")
  let newRow;
  if (selectedRowList.length === 0) {
    // No row is currently selected so select the first row
    newRow = layout_table.firstChild
  } else {
    selectedRow = selectedRowList[0]
    let selectedRowIndex = selectedRow.rowIndex
    if (direction === "up") {
      if (selectedRowIndex === 0) {
        newRow = layout_table.rows[0]
      } else {
        newRow = selectedRow.previousSibling
      }
    } else if (direction === "down") {
      if (selectedRowIndex === layout_table.rows.length - 1) {
        newRow = layout_table.rows[layout_table.rows.length - 1]
      } else {
        newRow = selectedRow.nextSibling
      }
    }
  }
  console.log("newRow: " + newRow)
  selectedRow.classList.remove("selected")
  newRow.classList.add("selected")
  updateActivity(newRow.rowIndex)

}

function checkKey(event) {
  let layout_table;
  let currentRow;
  let newRow;
  if (event.keyCode === 38) {
    // up arrow
    move("up")
  } else if (event.keyCode === 40) {
    // down arrow
    move("down")
  }
}

function updateActivity(activity_index) {
  if (selected_shape_index === -1) {
    // First time a shape has been selected, simply update the activity to the new shape.
    selected_shape_index = activity_index
  }
  if (selected_shape_index !== activity_index) {
    selected_shape_index = activity_index
  }
  // Get the id from the current activity row, then use that to get the visual activity data for this activity and
  // update it on the screen.
  let layout_table = document.getElementById("layout_table")

  currentRow = layout_table.rows[selected_shape_index]
  activity_id = currentRow.getElementsByClassName("activity_id")[0].id
  console.log("activity_id: " + activity_id)

  activity_data = get_activity_data(activity_id)
  console.log("activity_data: " + JSON.stringify(activity_data))

  let activity_table = document.getElementById("layout_activities")
  let field;
  let value;
  let field_row;
  let field_cell;
  for (var key in activity_data) {
    console.log("looking for row for field: " + key)
    if (activity_data.hasOwnProperty(key)) {
      field = key
      value = activity_data[key]
      console.log("field: " + field + " value: " + value)

      field_row = activity_table.getElementsByClassName(field)[0]
      console.log("field_row: " + field_row)

      // Find cell where we will place the field value
      cells_list = field_row.cells
      console.log("cells_list: " + cells_list)
      console.log("cells_list.length: " + cells_list.length)

      field_cell = undefined
      for (let i = 0; i < cells_list.length; i++) {
        class_list = field_row.cells[i].classList
        console.log("class_list: " + class_list)
        if (class_list.contains("value")) {
          field_cell = field_row.cells[i]
          break
        }
      }
      console.log("field_cell: " + field_cell)
      // If it's the style field, then we need to create a select element and populate it with the style options.
      if (field === "style") {
        field_cell.innerHTML = ""
        console.log("field is style")
        let select = document.createElement("select")
        select.setAttribute("id", "style_option")
        select.setAttribute("name", "style_option")
        for (let i = 0; i < value.length; i++) {
          let option = document.createElement("option")
          option_value = value[i][0]
          option_text = value[i][1]

          console.log("option_value: " + option_value)
          console.log("option_text: " + option_text)

          option.setAttribute("value", option_value)
          option.text = option_text
          select.appendChild(option)
        }
        console.log("select: " + select)
        console.log("field_cell: " + field_cell)
        console.log("options: " + select.options)
        for (let i = 0; i < select.options.length; i++) {
          let option_check_value = select.options[i].value
          let option_check_text = select.options[i].text
          let option_check = option_check_value + " " + option_check_text
          console.log("option_check: " + option_check)
        }

        field_cell.appendChild(select)
      } else {
        console.log("field is not style")
        field_cell.innerHTML = value
        console.log(key + " -> " + value);
      }
    }
  }
}

function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}

function get_activity_data(activity_id) {
  return {
    "activity_id": activity_id,
    "activity_name": "Activity 1",
    "duration": "12",
    "milestone": "true",
    "start_date": "2020-01-01",
    "end_date": "2020-01-10",
    "style": [["1", "Style 1"],["2", "Style 2"],["3", "Style 3"]],
    "track_number": getRandomInt(10),
  }
}

function get_activities(visual_id) {
  axios.defaults.xsrfCookieName = 'csrftoken'
  axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

  var url_string = "/api/v1/visual_activities/{{ visual.id }}/"

  axios.get(url_string)
    .then((response) => {
        console.log(response)
        return response.data
      },
      (error) => {
        console.log(error)
      }
    );
}

document.onkeydown = checkKey
let selected_shape_index = -1  // No shape is currently selected








