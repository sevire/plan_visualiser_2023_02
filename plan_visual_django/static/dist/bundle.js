/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./ui_src/drawing.ts":
/*!***************************!*\
  !*** ./ui_src/drawing.ts ***!
  \***************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   initialise_canvas: () => (/* binding */ initialise_canvas)
/* harmony export */ });
function initialise_canvas(settings) {
    let canvas = document.getElementById("visual");
    console.log("Canvas = " + canvas);
    const res = canvas.getContext('2d');
    if (!res || !(res instanceof CanvasRenderingContext2D)) {
        throw new Error('Failed to get 2D context');
    }
    const context = res;
    console.log("context = " + context);
    let baseCanvasWidth = settings.canvas_width;
    let baseCanvasHeight = settings.canvas_height;
    canvas.style.width = baseCanvasWidth + "px";
    canvas.style.height = baseCanvasHeight + "px";
    canvas.width = Math.floor(baseCanvasWidth * window.devicePixelRatio);
    canvas.height = Math.floor(baseCanvasHeight * window.devicePixelRatio);
    context.scale(window.devicePixelRatio, window.devicePixelRatio);
    console.log("devicePixelRation: " + window.devicePixelRatio);
    console.log("After scaling... canvas.width:" + canvas.width + " canvas.height" + canvas.height);
    context.fillStyle = "rgb(244, 244, 244)";
    context.strokeStyle = "rgb(166, 166, 166)";
    context.lineWidth = 3;
    context.rect(0, 0, canvas.width, canvas.height);
    context.fill();
    context.stroke();
    // context.fillRect(0, 0, canvas.width, canvas.height)
    // context.strokeRect(0, 0, canvas.width, canvas.height)
    return context;
}


/***/ }),

/***/ "./ui_src/manage_plan_panel.ts":
/*!*************************************!*\
  !*** ./ui_src/manage_plan_panel.ts ***!
  \*************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   change_track_value: () => (/* binding */ change_track_value),
/* harmony export */   toggle_expansion: () => (/* binding */ toggle_expansion)
/* harmony export */ });
function toggle_expansion(node) {
    // Passed an li element which has child elements encapsulated in a ul.  So when toggled hide or unhide the ul
    // Also need to toggle the icon - for expanded it's a minus, for unexpanded it's a plus.
    const expanded = node.classList.contains('expand');
    if (expanded) {
        // Current icon will be a minus, replace with a plus.
        const oldIcon = node.querySelector('div>i');
        oldIcon === null || oldIcon === void 0 ? void 0 : oldIcon.setAttribute('class', 'bi bi-plus-circle-fill');
        // oldIcon.textContent = "+"; // Temp
    }
    else {
        // Current icon will be a minus, replace with a plus.
        const oldIcon = node.querySelector('div>i');
        oldIcon === null || oldIcon === void 0 ? void 0 : oldIcon.setAttribute('class', 'bi bi-dash-circle-fill');
        // oldIcon.textContent = "-"; // Temp
    }
    // Now toggle the class
    node.classList.toggle('expand');
}
function get_activity(activity_id) {
    let found_value;
    window.plan_activity_data.forEach((activity) => {
        if (typeof found_value === 'undefined') {
            if (activity.activity_id === activity_id) {
                found_value = activity;
            }
        }
    });
    return found_value;
}
function change_track_value(event) {
    // Need to get value from the event target (input) and the activity id from the td (parent)
    const new_track_value = event.target.value;
    const activity = get_activity(window.selected_activity_id);
    if (activity) {
        activity.track = new_track_value;
    }
    else {
        console.log("Can't find activity");
    }
}


/***/ }),

/***/ "./ui_src/manage_shapes.ts":
/*!*********************************!*\
  !*** ./ui_src/manage_shapes.ts ***!
  \*********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   update_shape_for_activity_handler: () => (/* binding */ update_shape_for_activity_handler)
/* harmony export */ });
/* harmony import */ var _manage_visual__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./manage_visual */ "./ui_src/manage_visual.ts");
/* harmony import */ var _plan_visualiser_api__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./plan_visualiser_api */ "./ui_src/plan_visualiser_api.ts");
/* harmony import */ var _plot_visual__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./plot_visual */ "./ui_src/plot_visual.ts");
var __awaiter = (undefined && undefined.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};



function update_shape_for_activity_handler(unique_id, shape_id) {
    return __awaiter(this, void 0, void 0, function* () {
        // This is a handler function which will be passed to the Dropdown class for the style dropdown in the activity
        // panel.  It will update the style for the indicated activity to the one with the style name supplied.
        const activity = (0,_manage_visual__WEBPACK_IMPORTED_MODULE_0__.get_plan_activity)(unique_id);
        console.log(`Updating style id to ${shape_id}`);
        const data = [
            {
                id: activity.visual_data.id,
                plotable_shape: shape_id
            }
        ];
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_1__.update_visual_activities)(activity.visual_data.visual.id, data);
        const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_1__.get_visual_settings)(window.visual_id);
        window.visual_settings = response.data;
        (0,_plot_visual__WEBPACK_IMPORTED_MODULE_2__.plot_visual)();
    });
}


/***/ }),

/***/ "./ui_src/manage_styles.ts":
/*!*********************************!*\
  !*** ./ui_src/manage_styles.ts ***!
  \*********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   update_style_for_activity_handler: () => (/* binding */ update_style_for_activity_handler),
/* harmony export */   update_style_for_timeline_handler: () => (/* binding */ update_style_for_timeline_handler)
/* harmony export */ });
/* harmony import */ var _manage_visual__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./manage_visual */ "./ui_src/manage_visual.ts");
/* harmony import */ var _plan_visualiser_api__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./plan_visualiser_api */ "./ui_src/plan_visualiser_api.ts");
/* harmony import */ var _plot_visual__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./plot_visual */ "./ui_src/plot_visual.ts");
var __awaiter = (undefined && undefined.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};



function update_style_for_activity_handler(unique_id, style_id) {
    return __awaiter(this, void 0, void 0, function* () {
        // This is a handler function which will be passed to the Dropdown class for the style dropdown in the activity
        // panel.  It will update the style for the indicated activity to the one with the style name supplied.
        const activity = (0,_manage_visual__WEBPACK_IMPORTED_MODULE_0__.get_plan_activity)(unique_id);
        console.log(`Updating style id to ${style_id}`);
        const data = [
            {
                id: activity.visual_data.id,
                plotable_style: style_id
            }
        ];
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_1__.update_visual_activities)(activity.visual_data.visual.id, data);
        // Need visual settings as it included visual height which is needed to plot.
        const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_1__.get_visual_settings)(window.visual_id);
        window.visual_settings = response.data;
        (0,_plot_visual__WEBPACK_IMPORTED_MODULE_2__.plot_visual)();
    });
}
function update_style_for_timeline_handler(visual_id, timeline_id, style_id, odd_flag = false) {
    return __awaiter(this, void 0, void 0, function* () {
        // This is a handler function which will be passed to the Dropdown class for the style dropdown in the activity
        // panel.  It will update the style for the indicated activity to the one with the style name supplied.
        console.log(`Updating style id to ${style_id} for timeline ${timeline_id} in visual ${visual_id}`);
        const data = [
            {
                id: timeline_id,
            }
        ];
        if (odd_flag) {
            data[0].plotable_style_odd = style_id;
        }
        else {
            data[0].plotable_style_even = style_id;
        }
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_1__.update_timeline_records)(visual_id, data);
        // Need visual settings as it included visual height which is needed to plot.
        const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_1__.get_visual_settings)(window.visual_id);
        window.visual_settings = response.data;
        (0,_plot_visual__WEBPACK_IMPORTED_MODULE_2__.plot_visual)();
    });
}


/***/ }),

/***/ "./ui_src/manage_swimlanes.ts":
/*!************************************!*\
  !*** ./ui_src/manage_swimlanes.ts ***!
  \************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   add_arrow_button_to_element: () => (/* binding */ add_arrow_button_to_element),
/* harmony export */   update_swimlane_data: () => (/* binding */ update_swimlane_data),
/* harmony export */   update_swimlane_for_activity_handler: () => (/* binding */ update_swimlane_for_activity_handler),
/* harmony export */   update_swimlane_order: () => (/* binding */ update_swimlane_order)
/* harmony export */ });
/* harmony import */ var _plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./plan_visualiser_api */ "./ui_src/plan_visualiser_api.ts");
/* harmony import */ var _plot_visual__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./plot_visual */ "./ui_src/plot_visual.ts");
/* harmony import */ var _manage_visual__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./manage_visual */ "./ui_src/manage_visual.ts");
/* harmony import */ var _widgets__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./widgets */ "./ui_src/widgets.ts");
var __awaiter = (undefined && undefined.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};




function manage_arrow_click(panel_element, visual_id, data_record, direction, update_order_func, update_panel_func) {
    return __awaiter(this, void 0, void 0, function* () {
        yield update_order_func(visual_id, data_record, direction);
        // Update swimlane panel with swimlanes for this visual in sequence order
        console.log(`Updating panel (after moving item ${direction}...`);
        yield update_panel_func(panel_element, visual_id);
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_activity_data)(visual_id);
        // Need visual settings as it included visual height which is needed to plot.
        const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_settings)(window.visual_id);
        window.visual_settings = response.data;
        (0,_plot_visual__WEBPACK_IMPORTED_MODULE_1__.plot_visual)();
    });
}
function add_arrow_button_to_element(panel_element, arrow_element, direction, id, visual_id, data_record, update_order_func, update_panel_func) {
    return __awaiter(this, void 0, void 0, function* () {
        // Add button and appropriate arrow icon to supplied element.
        let button = document.createElement("button");
        button.classList.add("btn", "btn-secondary");
        arrow_element.appendChild(button);
        let arrow = document.createElement('i');
        arrow.classList.add("bi", "bi-caret-" + direction + "-fill");
        arrow.id = id + "-" + direction; // Need to ensure the id is unique so add direction to swimlane_id
        arrow.addEventListener('click', function () {
            return __awaiter(this, void 0, void 0, function* () {
                manage_arrow_click(panel_element, visual_id, data_record, direction, update_order_func, update_panel_func);
            });
        });
        button.appendChild(arrow);
    });
}
function update_swimlane_data(swimlane_html_panel, visual_id) {
    return __awaiter(this, void 0, void 0, function* () {
        // Populates the swimlane panel on the main edit visual page.
        // Adds a row for each swimlane and adds buttons for compress, move up etc.
        console.log("Adding swimlanes to swimlane panel...");
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_swimlane_data)(visual_id);
        console.log(`Swimlane data: ${JSON.stringify(window.swimlane_data)}`);
        // Find the tbody element within the swimlane table, then add a row for each swimlane.
        const tbody = swimlane_html_panel.querySelector("table tbody");
        // Clear tbody for case where we are updating panel rather than loading page
        tbody.innerHTML = "";
        let applied_default_swimlane = false;
        window.swimlane_data.forEach((swimlane_record) => {
            console.log(`Adding swimlane row to swimlane panel for ${swimlane_record.swim_lane_name}`);
            // Add row to tbody with two td's, one for an up and down arrow and one for swimlane name
            // Create a new row
            let row = document.createElement('tr');
            if (!applied_default_swimlane) {
                console.log(`Adding default swimlane class to swimlane ${swimlane_record.swim_lane_name}`);
                row.classList.add("default-swimlane");
                applied_default_swimlane = true;
            }
            else {
                console.log(`This swimlane not default, so not adding default swimlane class to swimlane ${swimlane_record.swim_lane_name}`);
            }
            row.addEventListener('click', function () {
                return __awaiter(this, void 0, void 0, function* () {
                    // Need to
                    // - Remove the default-swimlane class from the row where it is currently set
                    // - Add default-swimlane class to this row
                    // - Update window.default_swimlane to be swimlane_record.sequence_number
                    const currentDefaultElement = document.querySelector('div#swimlane_data tr.default-swimlane');
                    currentDefaultElement.classList.remove("default-swimlane");
                    row.classList.add('default-swimlane');
                    window.default_swimlane_seq_num = swimlane_record.sequence_number;
                });
            });
            tbody.appendChild(row);
            // Add td and div with swimlane name to row.  We need the div for the text-truncate to work.
            let swimlaneNameTD = document.createElement('td');
            swimlaneNameTD.classList.add("label");
            row.appendChild(swimlaneNameTD);
            let swimlaneNameDiv = document.createElement("div");
            swimlaneNameDiv.classList.add("text-truncate");
            swimlaneNameDiv.textContent = swimlane_record.swim_lane_name;
            swimlaneNameTD.appendChild(swimlaneNameDiv);
            // Add td, button group and two buttons for the up and down arrow
            const controlTD = document.createElement("td");
            controlTD.classList.add("text-end");
            row.appendChild(controlTD);
            const buttonGroup1 = document.createElement("div");
            buttonGroup1.classList.add("btn-group", "btn-group-sm", "up-down-control", "me-1");
            buttonGroup1.setAttribute('role', 'group');
            buttonGroup1.setAttribute('aria-label', 'Basic Example');
            controlTD.appendChild(buttonGroup1);
            console.log(`Adding arrow buttons to swimlane panel for ${swimlane_record.swim_lane_name}`);
            add_arrow_button_to_element(swimlane_html_panel, buttonGroup1, "up", swimlane_record.sequence_number, visual_id, swimlane_record, update_swimlane_order, update_swimlane_data);
            add_arrow_button_to_element(swimlane_html_panel, buttonGroup1, "down", swimlane_record.sequence_number, visual_id, swimlane_record, update_swimlane_order, update_swimlane_data);
            const buttonGroup2 = document.createElement("div");
            buttonGroup2.setAttribute('role', 'group');
            buttonGroup2.setAttribute('aria-label', 'Basic Example');
            buttonGroup2.classList.add("btn-group", "btn-group-sm");
            // Add td, button group and two buttons for compress and autolayout
            console.log(`Adding compress and auto buttons to swimlane panel for ${swimlane_record.swim_lane_name}`);
            controlTD.appendChild(buttonGroup2);
            const compressButton = (0,_widgets__WEBPACK_IMPORTED_MODULE_3__.create_button_with_icon)("bi-arrows-collapse");
            (0,_widgets__WEBPACK_IMPORTED_MODULE_3__.add_tooltip)(compressButton, "Compress - remove blank lines");
            compressButton.addEventListener('click', () => __awaiter(this, void 0, void 0, function* () {
                console.log(`Compressing swimlane ${swimlane_record.swim_lane_name}`);
                // Send api call to compress this swimlane, then re-plot the visual
                yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.compress_swimlane)(visual_id, swimlane_record.sequence_number);
                yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_activity_data)(visual_id);
                yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_plan_activity_data)(visual_id);
                // Need visual settings as it included visual height which is needed to plot.
                const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_settings)(window.visual_id);
                window.visual_settings = response.data;
                (0,_plot_visual__WEBPACK_IMPORTED_MODULE_1__.plot_visual)();
            }));
            const autoButton = (0,_widgets__WEBPACK_IMPORTED_MODULE_3__.create_button_with_icon)("bi-aspect-ratio");
            (0,_widgets__WEBPACK_IMPORTED_MODULE_3__.add_tooltip)(autoButton, "Auto - Auto layout");
            autoButton.addEventListener('click', () => __awaiter(this, void 0, void 0, function* () {
                console.log(`Autolayout of swimlane ${swimlane_record.swim_lane_name}`);
                // Send api call to compress this swimlane, then re-plot the visual
                yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.autolayout_swimlane)(visual_id, swimlane_record.sequence_number);
                yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_activity_data)(visual_id);
                yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_plan_activity_data)(visual_id);
                // Need visual settings as it included visual height which is needed to plot.
                const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_settings)(window.visual_id);
                window.visual_settings = response.data;
                (0,_plot_visual__WEBPACK_IMPORTED_MODULE_1__.plot_visual)();
            }));
            buttonGroup2.appendChild(compressButton);
            buttonGroup2.appendChild(autoButton);
        });
    });
}
function update_swimlane_order(visual_id, this_swimlane_object, direction) {
    return __awaiter(this, void 0, void 0, function* () {
        // To move this swimlane up, we find the swimlane record with the previous sequence number for this visual,
        // and swap sequence numbers with current one.
        const this_sequence_number = this_swimlane_object.sequence_number;
        let swimlane_update_object;
        if (direction == "up") {
            if (this_swimlane_object.sequence_number == 1) {
                console.log("Swimlane already at top of list, can't move up");
            }
            else {
                // Swimlanes are in sequence number order and sequence numbers are contiguous and start from 1.
                // So find previous swimlane record, which we are going to swap with to move this one up.
                const previous_sequence_number = this_sequence_number - 1;
                const previous_swimlane_object = window.swimlane_data[previous_sequence_number - 1];
                swimlane_update_object = [
                    {
                        id: this_swimlane_object.id,
                        sequence_number: previous_sequence_number
                    },
                    {
                        id: previous_swimlane_object.id,
                        sequence_number: this_sequence_number
                    }
                ];
            }
        }
        else if (direction == "down") {
            if (this_swimlane_object.sequence_number == window.swimlane_data.length) {
                console.log("Swimlane already at bottom of list, can't move down");
            }
            else {
                // Swimlanes are in sequence number order and sequence numbers are contiguous and start from 1.
                // So find previous swimlane record, which we are going to swap with to move this one up.
                const next_sequence_number = this_sequence_number + 1;
                const next_swimlane_object = window.swimlane_data[next_sequence_number - 1];
                swimlane_update_object = [
                    {
                        id: this_swimlane_object.id,
                        sequence_number: next_sequence_number
                    },
                    {
                        id: next_swimlane_object.id,
                        sequence_number: this_sequence_number
                    }
                ];
            }
        }
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.update_swimlane_records)(visual_id, swimlane_update_object);
    });
}
function update_swimlane_for_activity_handler(unique_id, swimlane_id) {
    return __awaiter(this, void 0, void 0, function* () {
        // This is a handler function which will be passed to the Dropdown class for the swimlane dropdown in the activity
        // panel.  It will update the swimlane for the indicated activity to the one with the swimlane name supplied.
        const activity = (0,_manage_visual__WEBPACK_IMPORTED_MODULE_2__.get_plan_activity)(unique_id);
        console.log(`Updating swimlane id to ${swimlane_id}`);
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.update_visual_activity_swimlane)(activity.visual_data.visual.id, unique_id, swimlane_id);
    });
}


/***/ }),

/***/ "./ui_src/manage_timelines.ts":
/*!************************************!*\
  !*** ./ui_src/manage_timelines.ts ***!
  \************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   add_arrow_to_element: () => (/* binding */ add_arrow_to_element),
/* harmony export */   update_swimlane_for_activity_handler: () => (/* binding */ update_swimlane_for_activity_handler),
/* harmony export */   update_timeline_order: () => (/* binding */ update_timeline_order),
/* harmony export */   update_timeline_panel: () => (/* binding */ update_timeline_panel)
/* harmony export */ });
/* harmony import */ var _plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./plan_visualiser_api */ "./ui_src/plan_visualiser_api.ts");
/* harmony import */ var _plot_visual__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./plot_visual */ "./ui_src/plot_visual.ts");
/* harmony import */ var _manage_visual__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./manage_visual */ "./ui_src/manage_visual.ts");
/* harmony import */ var _manage_swimlanes__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./manage_swimlanes */ "./ui_src/manage_swimlanes.ts");
/* harmony import */ var _widgets__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./widgets */ "./ui_src/widgets.ts");
/* harmony import */ var _manage_styles__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./manage_styles */ "./ui_src/manage_styles.ts");
var __awaiter = (undefined && undefined.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};






function manage_arrow_click(visual_id, timeline_record, direction) {
    return __awaiter(this, void 0, void 0, function* () {
        yield update_timeline_order(visual_id, timeline_record, direction);
        // Update swimlane panel with swimlanes for this visual in sequence order
        console.log(`Updating timeline panel (after moving timeline ${direction}...`);
        const timeline_element = document.getElementById("timeline_data");
        yield update_timeline_panel(timeline_element, visual_id);
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_activity_data)(visual_id);
        // Need visual settings as it included visual height which is needed to plot.
        const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_settings)(window.visual_id);
        window.visual_settings = response.data;
        (0,_plot_visual__WEBPACK_IMPORTED_MODULE_1__.plot_visual)();
    });
}
function add_arrow_to_element(element, direction, id, visual_id, timeline_record) {
    return __awaiter(this, void 0, void 0, function* () {
        let arrow = document.createElement('i');
        arrow.classList.add("fa-solid");
        arrow.classList.add("fa-circle-chevron-" + direction);
        arrow.id = id;
        arrow.addEventListener('click', function () {
            return __awaiter(this, void 0, void 0, function* () {
                manage_arrow_click(visual_id, timeline_record, direction);
            });
        });
        element.appendChild(arrow);
    });
}
function createAndPopulateDropdown(dropdownParent, styleName, styleData, visualId, timelineRecordId, isOdd) {
    let dropDownButton = (0,_widgets__WEBPACK_IMPORTED_MODULE_4__.createDropdown)(dropdownParent, styleName);
    (0,_widgets__WEBPACK_IMPORTED_MODULE_4__.populateDropdown)(dropDownButton, styleData.map(obj => [obj.style_name, obj.id]), (style_id) => __awaiter(this, void 0, void 0, function* () {
        yield (0,_manage_styles__WEBPACK_IMPORTED_MODULE_5__.update_style_for_timeline_handler)(visualId, timelineRecordId, style_id, isOdd);
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_activity_data)(window.visual_id);
        // Need visual settings as it includes visual height which is needed to plot.
        const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_settings)(window.visual_id);
        window.visual_settings = response.data;
        (0,_plot_visual__WEBPACK_IMPORTED_MODULE_1__.plot_visual)();
    }));
    return dropDownButton;
}
function update_timeline_panel(timeline_html_panel, visual_id) {
    return __awaiter(this, void 0, void 0, function* () {
        console.log("Adding timelines to timeline panel...");
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_timeline_data)(visual_id);
        // Find the tbody element within the swimlane table, then add a row for each timeline.
        const tbody = timeline_html_panel.querySelector("table tbody");
        // Clear tbody for case where we are updating panel rather than loading page
        tbody.innerHTML = "";
        window.timeline_data.forEach((timeline_record) => {
            console.log(`Adding timeline row to timeline panel for ${timeline_record.timeline_name}`);
            let row = document.createElement('tr');
            tbody.appendChild(row);
            let timelineNameTD = document.createElement('td');
            timelineNameTD.style.width = "20%";
            row.appendChild(timelineNameTD);
            let timelineNameDiv = document.createElement("div");
            timelineNameDiv.classList.add("text-truncate");
            timelineNameDiv.textContent = timeline_record.timeline_name;
            timelineNameTD.appendChild(timelineNameDiv);
            const styleDropdownTD = document.createElement("td");
            styleDropdownTD.style.width = "40%";
            styleDropdownTD.classList.add("text-end");
            row.appendChild(styleDropdownTD);
            // Add two dropdowns, for odd and even styling for timeline labels
            // Usage
            let timelineStyleOddButton = createAndPopulateDropdown(styleDropdownTD, timeline_record.plotable_style_odd.style_name, window.style_data, visual_id, timeline_record.id, true);
            let timelineStyleEvenButton = createAndPopulateDropdown(styleDropdownTD, timeline_record.plotable_style_even.style_name, window.style_data, visual_id, timeline_record.id, false);
            // Add td, toggle button, button group and two buttons for the up and down arrow
            const controlTD = document.createElement("td");
            controlTD.style.width = "40%";
            row.appendChild(controlTD);
            const buttonGroup1 = document.createElement("div");
            buttonGroup1.classList.add("btn-group", "btn-group-sm", "up-down-control", "me-1");
            buttonGroup1.setAttribute('role', 'group');
            buttonGroup1.setAttribute('aria-label', 'Basic Example');
            controlTD.appendChild(buttonGroup1);
            (0,_manage_swimlanes__WEBPACK_IMPORTED_MODULE_3__.add_arrow_button_to_element)(timeline_html_panel, buttonGroup1, "up", timeline_record.sequence_number, visual_id, timeline_record, update_timeline_order, update_timeline_panel);
            (0,_manage_swimlanes__WEBPACK_IMPORTED_MODULE_3__.add_arrow_button_to_element)(timeline_html_panel, buttonGroup1, "down", timeline_record.sequence_number, visual_id, timeline_record, update_timeline_order, update_timeline_panel);
            const buttonGroup2 = document.createElement("div");
            buttonGroup2.classList.add("btn-group", "btn-group-sm", "up-down-control", "me-1");
            buttonGroup2.setAttribute('role', 'group');
            buttonGroup2.setAttribute('aria-label', 'Basic Example');
            controlTD.appendChild(buttonGroup1);
            let timelineToggleButton;
            if (timeline_record.enabled) {
                timelineToggleButton = (0,_widgets__WEBPACK_IMPORTED_MODULE_4__.create_button_with_icon)("bi-check2");
                timelineToggleButton.classList.add("active");
            }
            else {
                timelineToggleButton = (0,_widgets__WEBPACK_IMPORTED_MODULE_4__.create_button_with_icon)("bi-x-lg");
            }
            timelineToggleButton.addEventListener('click', () => __awaiter(this, void 0, void 0, function* () {
                const data = [
                    {
                        id: timeline_record.id,
                        enabled: !timeline_record.enabled
                    }
                ];
                yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.update_timeline_records)(visual_id, data);
                yield update_timeline_panel(timeline_html_panel, visual_id);
                yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_activity_data)(visual_id);
                // Need visual settings as it included visual height which is needed to plot.
                const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_settings)(window.visual_id);
                window.visual_settings = response.data;
                (0,_plot_visual__WEBPACK_IMPORTED_MODULE_1__.plot_visual)();
            }));
            buttonGroup2.appendChild(timelineToggleButton);
            controlTD.appendChild(buttonGroup2);
        });
    });
}
function update_timeline_order(visual_id, this_timeline_object, direction) {
    return __awaiter(this, void 0, void 0, function* () {
        // To move this timeline up, we find the timeline record with the previous sequence number for this visual,
        // and swap sequence numbers with current one.
        const this_sequence_number = this_timeline_object.sequence_number;
        let timeline_update_object;
        if (direction == "up") {
            if (this_timeline_object.sequence_number == 1) {
                console.log("Timeline already at top of list, can't move up");
            }
            else {
                // Timelines are in sequence number order and sequence numbers are contiguous and start from 1.
                // So find previous timeline record, which we are going to swap with to move this one up.
                const previous_sequence_number = this_sequence_number - 1;
                const previous_timeline_object = window.timeline_data[previous_sequence_number - 1];
                timeline_update_object = [
                    {
                        id: this_timeline_object.id,
                        sequence_number: previous_sequence_number
                    },
                    {
                        id: previous_timeline_object.id,
                        sequence_number: this_sequence_number
                    }
                ];
            }
        }
        else if (direction == "down") {
            if (this_timeline_object.sequence_number == window.timeline_data.length) {
                console.log("Timeline already at bottom of list, can't move down");
            }
            else {
                // Timelines are in sequence number order and sequence numbers are contiguous and start from 1.
                // So find previous timeline record, which we are going to swap with to move this one up.
                const next_sequence_number = this_sequence_number + 1;
                const next_timeline_object = window.timeline_data[next_sequence_number - 1];
                timeline_update_object = [
                    {
                        id: this_timeline_object.id,
                        sequence_number: next_sequence_number
                    },
                    {
                        id: next_timeline_object.id,
                        sequence_number: this_sequence_number
                    }
                ];
            }
        }
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.update_timeline_records)(visual_id, timeline_update_object);
    });
}
function update_swimlane_for_activity_handler(unique_id, swimlane_id) {
    return __awaiter(this, void 0, void 0, function* () {
        // This is a handler function which will be passed to the Dropdown class for the swimlane dropdown in the activity
        // panel.  It will update the swimlane for the indicated activity to the one with the swimlane name supplied.
        const activity = (0,_manage_visual__WEBPACK_IMPORTED_MODULE_2__.get_plan_activity)(unique_id);
        console.log(`Updating swimlane id to ${swimlane_id}`);
        const data = [
            {
                id: activity.visual_data.id,
                swimlane: swimlane_id
            }
        ];
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.update_visual_activities)(activity.visual_data.visual.id, data);
    });
}


/***/ }),

/***/ "./ui_src/manage_visual.ts":
/*!*********************************!*\
  !*** ./ui_src/manage_visual.ts ***!
  \*********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   createPlanTree: () => (/* binding */ createPlanTree),
/* harmony export */   get_plan_activity: () => (/* binding */ get_plan_activity),
/* harmony export */   update_activity_text_flow: () => (/* binding */ update_activity_text_flow),
/* harmony export */   update_activity_track: () => (/* binding */ update_activity_track),
/* harmony export */   update_activity_track_height: () => (/* binding */ update_activity_track_height)
/* harmony export */ });
/* harmony import */ var _plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./plan_visualiser_api */ "./ui_src/plan_visualiser_api.ts");
/* harmony import */ var _manage_plan_panel__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./manage_plan_panel */ "./ui_src/manage_plan_panel.ts");
/* harmony import */ var _plot_visual__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./plot_visual */ "./ui_src/plot_visual.ts");
/* harmony import */ var _manage_swimlanes__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./manage_swimlanes */ "./ui_src/manage_swimlanes.ts");
/* harmony import */ var _manage_styles__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./manage_styles */ "./ui_src/manage_styles.ts");
/* harmony import */ var _manage_shapes__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./manage_shapes */ "./ui_src/manage_shapes.ts");
/* harmony import */ var _widgets__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./widgets */ "./ui_src/widgets.ts");
// Functionality to manage the main edit visual page of the app.
// The id of the visual is set to the id of the body element in the page by the Django app.
// The edit visual page is purely Ajax driven and each element of the page is updated by calling
// the API to the Django app to get the data required to populate the page.
var __awaiter = (undefined && undefined.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};







function add_add_sub_activities_event_handler(plan_tree_root) {
    // Add event handler to icon button for adding all sub-activities of the currently selected
    // activity.
    const add_sub_activities_button = document.getElementById("add-subtask-button");
    add_sub_activities_button === null || add_sub_activities_button === void 0 ? void 0 : add_sub_activities_button.addEventListener('click', function () {
        return __awaiter(this, void 0, void 0, function* () {
            // Get id of the currently selected plan activity and use api to add all direct sub-activities for that activity.
            const selected = plan_tree_root.getElementsByClassName('current');
            if (selected.length != 1) {
                console.log(`Error: add-subtask-button clicked but unique activity not selected ${selected}`);
            }
            else {
                const visual_id = window.visual_id;
                const swimlane_seq_num = window.default_swimlane_seq_num;
                const unique_id = selected[0].id;
                console.log(`About to add sub-activities for visual_id ${visual_id}, unique_id ${unique_id}, swimlane, ${swimlane_seq_num}`);
                yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.add_sub_activities_to_visual)(visual_id, unique_id, swimlane_seq_num);
                yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_plan_activity_data)(visual_id);
                yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_activity_data)(visual_id);
                const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_settings)(window.visual_id);
                window.visual_settings = response.data;
                (0,_plot_visual__WEBPACK_IMPORTED_MODULE_2__.plot_visual)();
            }
        });
    });
}
function createPlanTree() {
    return __awaiter(this, void 0, void 0, function* () {
        // We are going to create a tree of elements to represent the hierarchical plan structure.  We will iterate through
        // all the plan activities in the order they appear in the plan and use the level to work out where each activity
        // sits compared to the previous (child, sibling, sibling of parent etc.)
        let topLevelUL = document.createElement('ul');
        topLevelUL.classList.add("bg-primary-subtle");
        let topLevelElements = [topLevelUL];
        topLevelElements[0].setAttribute("id", "plan-activities");
        // Level sequence may vary depending upon how the plan has been structured and which app the plan was created in.
        // But we want the lowest level to be 1 as various things depend on it (including color-coding).
        // So adjust level for each activity as we go to ensure that the lowest level to be 1.
        // We assume that the level for the first activity will be the lowest in the plan.
        const level_adjust = 1 - window.plan_activity_data[0].plan_data.level;
        let previousLevel = 1;
        // Before building the plan activity tree, add the event handler for plan activity buttons, such as
        // button to add sub-activities for current activity.
        add_add_sub_activities_event_handler(topLevelElements[0]);
        // We are going to store the element we use to represent the first activity in the plan as we are going to return it
        // so it can be used as the current selected element once the page has been built.
        let initial_selected_activity_div;
        // Note using for rather than forEach as need to do business logic depending upon where we are
        // in the sequence.  May be a better way of doing this!
        for (let i = 0; i < window.plan_activity_data.length; i++) {
            // Get activity for this index
            const activity = window.plan_activity_data[i];
            const level = activity.plan_data.level + level_adjust;
            console.log("(New) Processing activity: " + activity.plan_data.activity_name + ", level: " + level);
            const activity_text = activity.plan_data.activity_name;
            const level_class = "level-" + level;
            const li = document.createElement('li');
            // Put activity text into a div under the li to help style independently of ul/li structure.
            const activityDiv = document.createElement("div");
            console.log(activityDiv);
            activityDiv.setAttribute('class', level_class);
            activityDiv.id = activity.plan_data.unique_sticky_activity_id;
            if (activity.visual_data && activity.visual_data.enabled) {
                activityDiv.classList.add('in-visual');
            }
            // Add event listener for clicking
            activityDiv.addEventListener('click', function () {
                return __awaiter(this, void 0, void 0, function* () {
                    yield manage_plan_activity_click(activity, activityDiv, topLevelElements);
                });
            });
            if (i < window.plan_activity_data.length - 1) {
                if (window.plan_activity_data[i + 1].plan_data.level + level_adjust > level) {
                    // This is the last at this level before we drop a level so need to add an expand icon and expand class
                    const expandIcon = document.createElement('i');
                    li.setAttribute('class', 'expandNode');
                    expandIcon.setAttribute('class', 'bi bi-plus-circle-fill');
                    // expandIcon.textContent = "+";  // Temp for when can't access CDN for icons.
                    console.log("Adding event listener on icon" + expandIcon);
                    expandIcon.addEventListener('click', function (event) {
                        event.stopPropagation();
                        (0,_manage_plan_panel__WEBPACK_IMPORTED_MODULE_1__.toggle_expansion)(li);
                    });
                    // Need to include expansion icon as this element has children
                    activityDiv.appendChild(expandIcon);
                }
            }
            const textNode = document.createTextNode(activity_text);
            activityDiv.appendChild(textNode);
            li.appendChild(activityDiv);
            const levelChange = level - previousLevel;
            if (levelChange > 0) {
                const newTree = document.createElement('ul');
                const length = topLevelElements.length;
                const entry = topLevelElements[length - 1];
                const lastChild = entry.lastChild;
                lastChild === null || lastChild === void 0 ? void 0 : lastChild.appendChild(newTree);
                topLevelElements.push(newTree);
            }
            else if (levelChange < 0) {
                console.log("Down one or more levels");
                // If we went down one or more levels, we need to take that many trees off the list.
                topLevelElements.splice(topLevelElements.length + levelChange);
            }
            else {
                console.log("Same level, adding text node");
            }
            // Regardless of level change, append new activity to the current tree.
            topLevelElements[topLevelElements.length - 1].appendChild(li);
            previousLevel = level;
            console.log("topLevelElements", topLevelElements);
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
    });
}
function add_to_visual(activity_id, swimlane_seq_number) {
    return __awaiter(this, void 0, void 0, function* () {
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.add_activity_to_visual)(window.visual_id, activity_id, swimlane_seq_number);
        console.log("Added activity to visual: " + activity_id);
        const activity = get_plan_activity(activity_id);
        activity.enabled = true;
    });
}
function remove_from_visual(activity_id) {
    return __awaiter(this, void 0, void 0, function* () {
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.remove_activity_from_visual)(window.visual_id, activity_id);
        console.log("Removed activity from visual: " + activity_id);
        const activity = get_plan_activity(activity_id);
        activity.enabled = false;
    });
}
function get_plan_activity(activity_id) {
    // Find activity in stored list of all plan activities by iterating through and checking each one.
    // ToDo: Review the logic of getting activity data as may be a more efficient way of doing it
    let found_value;
    window.plan_activity_data.forEach((activity) => {
        if (typeof found_value === 'undefined') {
            if (activity.plan_data.unique_sticky_activity_id === activity_id) {
                found_value = activity;
            }
        }
    });
    return found_value;
}
function add_move_track_event_handler(direction, activity) {
    return __awaiter(this, void 0, void 0, function* () {
        console.log(`Track number ${direction} clicked`);
        console.log(`Activity is ${activity}`);
        yield update_activity_track(activity.visual_data.unique_id_from_plan, direction);
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_plan_activity_data)(window.visual_id);
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_activity_data)(window.visual_id);
        // Need visual settings as it included visual height which is needed to plot.
        const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_settings)(window.visual_id);
        window.visual_settings = response.data;
        (0,_plot_visual__WEBPACK_IMPORTED_MODULE_2__.plot_visual)();
    });
}
function add_modify_track_height_event_handler(direction, activity) {
    return __awaiter(this, void 0, void 0, function* () {
        console.log(`Track height ${direction} clicked`);
        console.log(`Activity is ${activity}`);
        let api_direction;
        if (direction == "up") {
            api_direction = "increase";
        }
        else if (direction == "down") {
            api_direction = "decrease";
        }
        else {
            throw new Error(`Invalid value for direction = ${direction}`);
        }
        yield update_activity_track_height(activity.visual_data.unique_id_from_plan, api_direction);
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_plan_activity_data)(window.visual_id);
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_activity_data)(window.visual_id);
        // Need visual settings as it included visual height which is needed to plot.
        const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_settings)(window.visual_id);
        window.visual_settings = response.data;
        (0,_plot_visual__WEBPACK_IMPORTED_MODULE_2__.plot_visual)();
    });
}
function add_modify_text_flow_event_handler(flow_direction, activity) {
    return __awaiter(this, void 0, void 0, function* () {
        console.log(`Text flow handler ${flow_direction} clicked`);
        console.log(`Activity is ${activity}`);
        yield update_activity_text_flow(activity.visual_data.unique_id_from_plan, flow_direction);
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_plan_activity_data)(window.visual_id);
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_activity_data)(window.visual_id);
        // Need visual settings as it included visual height which is needed to plot.
        const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_settings)(window.visual_id);
        window.visual_settings = response.data;
        (0,_plot_visual__WEBPACK_IMPORTED_MODULE_2__.plot_visual)();
    });
}
// ====================================================================================================
// Below are functions need for dispatch table to set values for each field in the activity data panel
// ====================================================================================================
function set_boolean_value(TdRef, value) {
    // Set to tick for true and cross for false.
    TdRef.textContent = '';
    const iElement = document.createElement('i');
    if (value) {
        iElement.className = 'bi bi-check';
    }
    else {
        iElement.className = 'bi bi-x';
    }
    TdRef.appendChild(iElement);
}
function set_text_field(tdRef, value) {
    // It's just a text field so set text-truncate and set value
    tdRef.classList.add("text-truncate");
    tdRef.textContent = value;
}
// Dispatch table used to set values of different types for each activity field
// NOTE: This is work in progress
const NonEditableDispatchTable = {
    'milestone_flag': set_boolean_value,
    'activity_name': set_text_field,
    'unique_sticky_activity_id': set_text_field
};
function add_button_group(td_element, aria_label) {
    // Add up and down arrows to the td element and add click event handler which updates activity vertical position.
    const buttonGroup = document.createElement("div");
    buttonGroup.classList.add("btn-group", "btn-group-sm", "up-down-control", "me-1");
    buttonGroup.setAttribute('role', 'group');
    buttonGroup.setAttribute('aria-label', aria_label);
    td_element.appendChild(buttonGroup);
    return buttonGroup;
}
function add_two_arrow_buttons(buttonGroup, activity, labels, event_handler) {
    let direction;
    for (let i = 0; i < 2; i++) {
        if (i == 0) {
            direction = labels[0];
        }
        else {
            direction = labels[1];
        }
        // Add button and appropriate arrow icon to supplied element.
        let button = document.createElement("button");
        button.classList.add("btn", "btn-secondary");
        buttonGroup.appendChild(button);
        let arrow = document.createElement('i');
        arrow.classList.add("bi", "bi-caret-" + direction + "-fill");
        arrow.id = `${activity.visual_data.unique_id_from_plan}-[${direction}]`;
        arrow.addEventListener('click', function () {
            return __awaiter(this, void 0, void 0, function* () {
                event_handler(labels[i], activity);
            });
        });
        button.appendChild(arrow);
    }
}
function add_three_buttons(buttonGroup, activity, event_handler) {
    // ToDo: Refactor two arrow and three arrow button groups to be single method
    // This is to support text flow functionality so need specific icons for that - not arrows
    const labels = [
        ["RFLOW", "arrow-bar-right"],
        ["CENTRE", "arrows"],
        ["LFLOW", "arrow-bar-left"] // These values correspond to value in database so can't change.
    ];
    for (let i = 0; i < 3; i++) {
        const [flow_direction, icon_name] = labels[i];
        console.log(`Adding button for flow control ${flow_direction}, icon ${icon_name}`);
        // Add button and appropriate arrow icon to supplied element.
        let button = document.createElement("button");
        button.classList.add("btn", "btn-secondary");
        if (activity.visual_data.text_flow == flow_direction) {
            button.classList.add("active");
        }
        buttonGroup.appendChild(button);
        let icon = document.createElement('i');
        icon.classList.add("bi", "bi-" + icon_name);
        icon.id = `${activity.visual_data.unique_id_from_plan}-[${flow_direction}]`;
        icon.addEventListener('click', function (e) {
            return __awaiter(this, void 0, void 0, function* () {
                let btns = buttonGroup.querySelectorAll('.btn');
                btns.forEach((b) => {
                    b.classList.remove('active');
                });
                // Add 'active' class to the clicked button
                const target_element = e.target;
                const parent_target_element = target_element.parentElement;
                console.log(`Updating active button for text flow for ${parent_target_element}`);
                parent_target_element.classList.add('active');
                event_handler(flow_direction, activity);
            });
        });
        button.appendChild(icon);
    }
}
function set_up_down_button(td_element, activity, aria_label, labels, event_handler) {
    // Start by clearing the element.
    td_element.textContent = '';
    const buttonGroup = add_button_group(td_element, aria_label);
    add_two_arrow_buttons(buttonGroup, activity, labels, event_handler);
}
function add_text_flow_buttons(td_element, activity, aria_label) {
    // Start by clearing the element.
    td_element.textContent = '';
    const buttonGroup = add_button_group(td_element, aria_label);
    add_three_buttons(buttonGroup, activity, add_modify_text_flow_event_handler);
}
function select_for_edit(activity_id, clear = false) {
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
    const edit_plan_activity_td_elements = document.querySelectorAll('#layout-activity tbody#plan-activity-properties td');
    const edit_visual_activity_td_elements = document.querySelectorAll('#layout-activity tbody#visual-activity-properties td');
    // If clear is set then this usually means the user has selected an activity which is not currently in the visual so
    // the visual portion of the activity data panel needs to be cleared.
    if (clear) {
        // Clear all the visual related values (because this activity is in the plan but not in the visual).
        window.selected_activity_id = undefined;
        edit_visual_activity_td_elements.forEach(element => {
            const key = element.id;
            element.textContent = '';
        });
    }
    // Modify stored value of currently selected activity to allow processing of further clicks etc.
    window.selected_activity_id = activity_id;
    // Find entry for the selected activity in the list.
    const activity = get_plan_activity(activity_id);
    console.log("Found entry for activity ", activity_id);
    // Populate each of the plan related fields (always do this)
    edit_plan_activity_td_elements.forEach(td_element => {
        const key = td_element.id;
        if (key in NonEditableDispatchTable) {
            NonEditableDispatchTable[key](td_element, activity.plan_data[key]);
        }
        else {
            td_element.textContent = activity.plan_data[key];
        }
    });
    if (clear) {
        console.log("Clear is set - don't update visual fields (as this activity not in visual)");
    }
    else {
        // Now populate each of the visual related fields (only if activity is in the visual)
        edit_visual_activity_td_elements.forEach(td_element => {
            const key = td_element.id;
            let activity_field_val = activity.visual_data[key];
            console.log("Edit activity elements - id = " + key + ", value is " + activity_field_val);
            // For certain values we need to tweak the logic to populate the value, either because
            // - The field is an object which needs further decoding to extract value
            // - The field is editable so we need to update the input html element value, not the td directly.
            // For fields in the dispatch table call dispatch function which will populate the field.
            // Otherwise old if then else logic applies below.
            // Track number: Set the value of the spinner
            if (key === "vertical_positioning_value") {
                set_up_down_button(td_element, activity, 'Activity Vertical Position Control', ["up", "down"], add_move_track_event_handler);
            }
            else if (key === "height_in_tracks") {
                set_up_down_button(td_element, activity, 'Activity Height Control', ["up", "down"], add_modify_track_height_event_handler);
            }
            else if (key === "text_flow") {
                add_text_flow_buttons(td_element, activity, 'Text Flow Control');
            }
            else if (key === "plotable_shape") {
                // Start by clearing the element before updating it for this activity.
                (0,_widgets__WEBPACK_IMPORTED_MODULE_6__.clearElement)(td_element);
                let button = (0,_widgets__WEBPACK_IMPORTED_MODULE_6__.createDropdown)(td_element, activity.visual_data[key].value);
                (0,_widgets__WEBPACK_IMPORTED_MODULE_6__.populateDropdown)(button, window.shape_data.map((obj) => [obj.name, obj.id]), (shape_id) => __awaiter(this, void 0, void 0, function* () {
                    // Lookup shape name from id as that is what needs to be updated in the database
                    const shape_name = window.shape_data.find((obj) => obj.id === shape_id).name;
                    yield (0,_manage_shapes__WEBPACK_IMPORTED_MODULE_5__.update_shape_for_activity_handler)(activity_id, shape_name);
                    yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_activity_data)(window.visual_id);
                    // Need visual settings as it included visual height which is needed to plot.
                    const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_settings)(window.visual_id);
                    window.visual_settings = response.data;
                    (0,_plot_visual__WEBPACK_IMPORTED_MODULE_2__.plot_visual)();
                }));
            }
            else if (key === "plotable_style") {
                // Start by clearing the element before updating it for this activity.
                (0,_widgets__WEBPACK_IMPORTED_MODULE_6__.clearElement)(td_element);
                let button = (0,_widgets__WEBPACK_IMPORTED_MODULE_6__.createDropdown)(td_element, activity.visual_data[key].style_name);
                (0,_widgets__WEBPACK_IMPORTED_MODULE_6__.populateDropdown)(button, window.style_data.map((obj) => [obj.style_name, obj.id]), (style_id) => __awaiter(this, void 0, void 0, function* () {
                    yield (0,_manage_styles__WEBPACK_IMPORTED_MODULE_4__.update_style_for_activity_handler)(activity_id, style_id);
                    yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_activity_data)(window.visual_id);
                    // Need visual settings as it included visual height which is needed to plot.
                    const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_settings)(window.visual_id);
                    window.visual_settings = response.data;
                    (0,_plot_visual__WEBPACK_IMPORTED_MODULE_2__.plot_visual)();
                }));
            }
            else if (key === "swimlane") {
                // Start by clearing the element before updating it for this activity.
                (0,_widgets__WEBPACK_IMPORTED_MODULE_6__.clearElement)(td_element);
                let button = (0,_widgets__WEBPACK_IMPORTED_MODULE_6__.createDropdown)(td_element, activity.visual_data[key].swim_lane_name);
                (0,_widgets__WEBPACK_IMPORTED_MODULE_6__.populateDropdown)(button, window.swimlane_data.map((obj) => [obj.swim_lane_name, obj.id]), (swimlane_id) => __awaiter(this, void 0, void 0, function* () {
                    yield (0,_manage_swimlanes__WEBPACK_IMPORTED_MODULE_3__.update_swimlane_for_activity_handler)(activity_id, swimlane_id);
                    yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_plan_activity_data)(window.visual_id);
                    yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_activity_data)(window.visual_id);
                    // Need visual settings as it included visual height which is needed to plot.
                    const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_settings)(window.visual_id);
                    window.visual_settings = response.data;
                    (0,_plot_visual__WEBPACK_IMPORTED_MODULE_2__.plot_visual)();
                }));
            }
            else {
                td_element.textContent = activity_field_val;
            }
        });
        (0,_plot_visual__WEBPACK_IMPORTED_MODULE_2__.highlight_activity)(activity_id);
    }
}
function manage_plan_activity_click(activity, activityDiv, topLevelElements) {
    return __awaiter(this, void 0, void 0, function* () {
        // If this element isn't already the current one, then make it the current one.
        // If it is already the current one, then this click will toggle its inclusion in the visual.
        if (activityDiv.classList.contains('current')) {
            console.log("Toggle inclusion in visual: " + activity.plan_data.unique_sticky_activity_id);
            const inVisual = activityDiv.classList.toggle('in-visual');
            if (inVisual) {
                // Means we have just toggled it to in so need to add it
                yield add_to_visual(activity.plan_data.unique_sticky_activity_id, window.default_swimlane_seq_num);
                yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_activity_data)(window.visual_id); // Refresh data from server before replotting
                yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_plan_activity_data)(window.visual_id); // Refresh data from server before replotting
                // Need visual settings as it included visual height which is needed to plot.
                const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_settings)(window.visual_id);
                window.visual_settings = response.data;
                (0,_plot_visual__WEBPACK_IMPORTED_MODULE_2__.plot_visual)();
                // Now it is in the visual and current activity we should select it for edit.
                select_for_edit(activity.plan_data.unique_sticky_activity_id);
            }
            else {
                // Means we have just toggled it to not in so need to remove it
                yield remove_from_visual(activity.plan_data.unique_sticky_activity_id);
                yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_activity_data)(window.visual_id); // Refresh data from server before replotting
                // Need visual settings as it included visual height which is needed to plot.
                const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_settings)(window.visual_id);
                window.visual_settings = response.data;
                (0,_plot_visual__WEBPACK_IMPORTED_MODULE_2__.plot_visual)();
                // As not in visual we can't edit it so need to clear out the visual elements and update the plan elements
                select_for_edit(activity.plan_data.unique_sticky_activity_id, true);
            }
        }
        else {
            // We have just selected an activity which wasn't already selected so need to change this one to the current
            // element and, if this activity is in the visual, update the activity panel to details for this activity.
            // If this activity is not in the visual then we need to clear the activity panel
            const selected = topLevelElements[0].getElementsByClassName('current');
            if (selected.length > 0) {
                selected[0].classList.remove('current');
            }
            activityDiv.classList.add('current');
            if (activityDiv.classList.contains('in-visual')) {
                select_for_edit(activity.plan_data.unique_sticky_activity_id);
            }
            else {
                select_for_edit(activity.plan_data.unique_sticky_activity_id, true);
            }
        }
    });
}
function update_activity_track(activity_unique_id, direction) {
    return __awaiter(this, void 0, void 0, function* () {
        // Need to get activity from global data - to ensure we get latest version.
        const activity = get_plan_activity(activity_unique_id);
        console.log(`update_activity_track: activity=${activity}, direction=${direction}`);
        console.log(`update_activity_track: activity.visual_data=${activity.visual_data}`);
        console.log(`update_activity_track: activity.visual_data.id=${activity.visual_data.id}`);
        const delta = direction === "down" ? 1 : (direction === "up" ? -1 : 0);
        console.log(`delta: ${delta}`);
        // Calculate new position - but don't allow track number to get below 1
        const new_vertical_position = Math.max(activity.visual_data.vertical_positioning_value + delta, 1);
        console.log(`new vertical value: ${new_vertical_position}`);
        const data = [
            {
                id: activity.visual_data.id,
                vertical_positioning_value: new_vertical_position
            }
        ];
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.update_visual_activities)(activity.visual_data.visual.id, data);
    });
}
function update_activity_track_height(activity_unique_id, direction) {
    return __awaiter(this, void 0, void 0, function* () {
        // Need to get activity from global data - to ensure we get latest version.
        const activity = get_plan_activity(activity_unique_id);
        console.log(`update_activity_track_height: activity=${activity}, direction=${direction}`);
        console.log(`update_activity_track_height: activity.visual_data=${activity.visual_data}`);
        console.log(`update_activity_track_height: activity.visual_data.id=${activity.visual_data.id}`);
        const delta = direction === "increase" ? 1 : (direction === "decrease" ? -1 : 0);
        console.log(`delta: ${delta}`);
        // Calculate new height, but can't be less than 1
        const new_track_height = Math.max(activity.visual_data.height_in_tracks + delta, 1);
        console.log(`new vertical value: ${new_track_height}`);
        const data = [
            {
                id: activity.visual_data.id,
                height_in_tracks: new_track_height
            }
        ];
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.update_visual_activities)(activity.visual_data.visual.id, data);
    });
}
function update_activity_text_flow(activity_unique_id, flow_direction) {
    return __awaiter(this, void 0, void 0, function* () {
        // Need to get activity from global data - to ensure we get latest version.
        const activity = get_plan_activity(activity_unique_id);
        console.log(`update_activity_text_flow: activity=${activity}, direction=${flow_direction}`);
        console.log(`update_activity_text_flow: activity.visual_data=${activity.visual_data}`);
        console.log(`update_activity_text_flow: activity.visual_data.id=${activity.visual_data.id}`);
        const data = [
            {
                id: activity.visual_data.id,
                text_flow: flow_direction
            }
        ];
        yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.update_visual_activities)(activity.visual_data.visual.id, data);
    });
}


/***/ }),

/***/ "./ui_src/manage_visual_image.ts":
/*!***************************************!*\
  !*** ./ui_src/manage_visual_image.ts ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   addVisualImages: () => (/* binding */ addVisualImages),
/* harmony export */   add_download_image_event_listener: () => (/* binding */ add_download_image_event_listener)
/* harmony export */ });
/* harmony import */ var _plot_visual__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./plot_visual */ "./ui_src/plot_visual.ts");
/* harmony import */ var _plan_visualiser_api__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./plan_visualiser_api */ "./ui_src/plan_visualiser_api.ts");
var __awaiter = (undefined && undefined.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};


function add_download_image_event_listener() {
    // There is a button on the edit visual screen to download an image of the visual
    // This function will add the event listener to the button to invoke the logic when clicked.
    const download_image_button = document.querySelector("#download-image-button");
    download_image_button.addEventListener('click', downloadImage);
}
function renderForImageCreation() {
    return __awaiter(this, void 0, void 0, function* () {
        // Re-draw visual elements for each canvas but onto a single consolidating canvas.
        console.log(`downloadImage: About to plot to capture canvas`);
        // Need visual settings as it included visual height which is needed to plot.
        const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_1__.get_visual_settings)(window.visual_id);
        window.visual_settings = response.data;
        (0,_plot_visual__WEBPACK_IMPORTED_MODULE_0__.plot_visual)(true);
    });
}
function getImageUrlForCanvas(canvas) {
    console.log(`Visual thumbnail - canvas is ${canvas}`);
    return canvas.toDataURL("image/png");
}
function downloadImage() {
    return __awaiter(this, void 0, void 0, function* () {
        yield renderForImageCreation();
        console.log(`Finished plotting, about to convert to image and get url`);
        const dataUrl = getImageUrlForCanvas(window.canvas_info.capture.canvas);
        // Now create a link to the url and simulate clicking on it so user just sees download
        let link = document.createElement('a');
        link.download = 'visual.png';
        link.href = dataUrl;
        // The link needs to be part of the document body to be "clickable".
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
}
function captureVisualAsImage(canvas) {
    return getImageUrlForCanvas(canvas);
}
function addVisualImages() {
    return __awaiter(this, void 0, void 0, function* () {
        console.log(`addVisualImages called`);
        let imgElements = document.querySelectorAll('[id^="thumbnail-"]');
        console.log(`Visual elements...`);
        console.dir(imgElements);
        for (let img of imgElements) {
            // Extract the "<xxx>" part and convert to integer
            let visualIdStr = (img.id.split('-')[1]);
            let visualId = parseInt(visualIdStr);
            console.log(`Processing image for visual ${visualId}`);
            // Make sure it's an integer
            if (!isNaN(visualId) && Number.isInteger(visualId)) {
                console.log("About to retrieve visual settings data from manage visual image");
                let response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_1__.get_visual_settings)(visualId);
                window.visual_settings = response.data;
                let [scale_factor, canvas_info] = (0,_plot_visual__WEBPACK_IMPORTED_MODULE_0__.initialise_canvases)(true);
                console.log(`canvas_info for capture is ${canvas_info}`);
                console.log(`canvas for capture is ${canvas_info.canvas}`);
                // Request data for this visual and wait for it to be returned
                console.log("About to retrieve visual data from manage visual image");
                yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_1__.get_visual_activity_data)(visualId); // Refresh data from server before replotting
                window.scale_factor = scale_factor;
                window.canvas_info = canvas_info;
                (0,_plot_visual__WEBPACK_IMPORTED_MODULE_0__.plot_visual)(true);
                // Update the img's src attribute
                img.src = captureVisualAsImage(canvas_info.capture.canvas);
            }
        }
    });
}


/***/ }),

/***/ "./ui_src/plan_visualiser_api.ts":
/*!***************************************!*\
  !*** ./ui_src/plan_visualiser_api.ts ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   add_activity_to_visual: () => (/* binding */ add_activity_to_visual),
/* harmony export */   add_sub_activities_to_visual: () => (/* binding */ add_sub_activities_to_visual),
/* harmony export */   api_patch: () => (/* binding */ api_patch),
/* harmony export */   api_post: () => (/* binding */ api_post),
/* harmony export */   autolayout_swimlane: () => (/* binding */ autolayout_swimlane),
/* harmony export */   compress_swimlane: () => (/* binding */ compress_swimlane),
/* harmony export */   get_plan_activity_data: () => (/* binding */ get_plan_activity_data),
/* harmony export */   get_shape_records: () => (/* binding */ get_shape_records),
/* harmony export */   get_style_records: () => (/* binding */ get_style_records),
/* harmony export */   get_swimlane_data: () => (/* binding */ get_swimlane_data),
/* harmony export */   get_timeline_data: () => (/* binding */ get_timeline_data),
/* harmony export */   get_visual_activity_data: () => (/* binding */ get_visual_activity_data),
/* harmony export */   get_visual_settings: () => (/* binding */ get_visual_settings),
/* harmony export */   remove_activity_from_visual: () => (/* binding */ remove_activity_from_visual),
/* harmony export */   update_swimlane_records: () => (/* binding */ update_swimlane_records),
/* harmony export */   update_timeline_records: () => (/* binding */ update_timeline_records),
/* harmony export */   update_visual_activities: () => (/* binding */ update_visual_activities),
/* harmony export */   update_visual_activity_swimlane: () => (/* binding */ update_visual_activity_swimlane)
/* harmony export */ });
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! axios */ "./node_modules/axios/lib/axios.js");
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! axios */ "./node_modules/axios/index.js");
// Functions which access API to get data with some simple pre-processing where necessary - no business logic!
var __awaiter = (undefined && undefined.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};

function api_get(url_string) {
    return __awaiter(this, void 0, void 0, function* () {
        const base_url = "";
        axios__WEBPACK_IMPORTED_MODULE_0__["default"].defaults.xsrfCookieName = 'csrftoken';
        axios__WEBPACK_IMPORTED_MODULE_0__["default"].defaults.xsrfHeaderName = "X-CSRFTOKEN";
        let ret_response = undefined;
        return yield axios__WEBPACK_IMPORTED_MODULE_0__["default"].get(base_url + url_string);
    });
}
function api_post(url_string, data) {
    return __awaiter(this, void 0, void 0, function* () {
        const base_url = "";
        axios__WEBPACK_IMPORTED_MODULE_0__["default"].defaults.xsrfCookieName = 'csrftoken';
        axios__WEBPACK_IMPORTED_MODULE_0__["default"].defaults.xsrfHeaderName = "X-CSRFTOKEN";
        let ret_response = undefined;
        return yield axios__WEBPACK_IMPORTED_MODULE_0__["default"].post(base_url + url_string, data);
    });
}
function api_put(url_string, data) {
    return __awaiter(this, void 0, void 0, function* () {
        const base_url = "";
        axios__WEBPACK_IMPORTED_MODULE_0__["default"].defaults.xsrfCookieName = 'csrftoken';
        axios__WEBPACK_IMPORTED_MODULE_0__["default"].defaults.xsrfHeaderName = "X-CSRFTOKEN";
        let ret_response = undefined;
        return axios__WEBPACK_IMPORTED_MODULE_0__["default"].put(base_url + url_string, data);
    });
}
function api_delete(url_string) {
    return __awaiter(this, void 0, void 0, function* () {
        const base_url = "";
        axios__WEBPACK_IMPORTED_MODULE_0__["default"].defaults.xsrfCookieName = 'csrftoken';
        axios__WEBPACK_IMPORTED_MODULE_0__["default"].defaults.xsrfHeaderName = "X-CSRFTOKEN";
        let ret_response = undefined;
        return axios__WEBPACK_IMPORTED_MODULE_0__["default"]["delete"](base_url + url_string);
    });
}
function api_patch(url_string, data) {
    return __awaiter(this, void 0, void 0, function* () {
        const base_url = "";
        const api_data = JSON.stringify(data);
        axios__WEBPACK_IMPORTED_MODULE_0__["default"].defaults.xsrfCookieName = 'csrftoken';
        axios__WEBPACK_IMPORTED_MODULE_0__["default"].defaults.xsrfHeaderName = "X-CSRFTOKEN";
        const config = {
            headers: {
                'Content-Type': 'application/json'
            }
        };
        return axios__WEBPACK_IMPORTED_MODULE_0__["default"].patch(base_url + url_string, api_data, config);
    });
}
function get_plan_activity_data(visual_id) {
    return __awaiter(this, void 0, void 0, function* () {
        // Returns array of activities mirroring the order in the plan.
        // Each activity includes fields from the original uploaded plan, and fields relating to the layout of that activity
        // in the visual, but those fields are only populated if the activity has at some point been in the visual.
        // There is an enabled flag which indicates whether the activity is currently in the visual.
        console.log("get_plan_activity_data: Start");
        const url_string = `/api/v1/model/plans/activities/visuals/${visual_id}/`;
        const response = yield api_get(url_string);
        window.plan_activity_data = response.data;
    });
}
function get_visual_activity_data(visual_id) {
    return __awaiter(this, void 0, void 0, function* () {
        // Returns array of activities mirroring the order in the plan.
        // Each activity includes fields from the original uploaded plan, and fields relating to the layout of that activity
        // in the visual, but those fields are only populated if the activity has at some point been in the visual.
        // There is an enabled flag which indicates whether the activity is currently in the visual.
        console.log(`Requesting activity data for visual ${visual_id}`);
        const url_string = `/api/v1/rendered/canvas/visuals/${visual_id}/`;
        const response = yield api_get(url_string);
        if (response.status === axios__WEBPACK_IMPORTED_MODULE_1__.HttpStatusCode.NoContent) {
            // No activities in visual so use empty object
            console.log(`No activity data returned for visual ${visual_id}`);
            window.visual_activity_data = {};
        }
        else {
            console.log(`Activity data returned for visual ${visual_id}`);
            window.visual_activity_data = response.data;
        }
    });
}
function add_activity_to_visual(visual_id, unique_id, swimlane_seq_num) {
    return __awaiter(this, void 0, void 0, function* () {
        // Adds specified plan activity to the visual with supplied id.
        const url_string = `/api/v1/model/visuals/activities/${visual_id}/${unique_id}/${swimlane_seq_num}/`;
        const response = yield api_put(url_string, undefined);
        console.log(`Status from adding activity to visual is ${response.status}`);
    });
}
function add_sub_activities_to_visual(visual_id, unique_id, swimlane_seq_num) {
    return __awaiter(this, void 0, void 0, function* () {
        // Adds immediate sub-activities of currently selected activity to visual at specified swimlane.
        const url_string = `/api/v1/model/visuals/activities/add-sub-activities/${visual_id}/${unique_id}/${swimlane_seq_num}/`;
        const response = yield api_put(url_string, undefined);
        console.log(`Status from adding sub-activities is ${response.status}`);
    });
}
function remove_activity_from_visual(visual_id, unique_id) {
    return __awaiter(this, void 0, void 0, function* () {
        // Adds specified plan activity to the visual with supplied id.
        const url_string = `/api/v1/model/visuals/activities/${visual_id}/${unique_id}/`;
        const response = yield api_delete(url_string);
        console.log(`Status from removing activity from visual is ${response.status}`);
    });
}
function get_swimlane_data(visual_id) {
    return __awaiter(this, void 0, void 0, function* () {
        const url_string = `/api/v1/model/visuals/swimlanes/${visual_id}/`;
        const response = yield api_get(url_string);
        window.swimlane_data = response.data;
    });
}
function get_timeline_data(visual_id) {
    return __awaiter(this, void 0, void 0, function* () {
        const url_string = `/api/v1/model/visuals/timelines/${visual_id}/`;
        const response = yield api_get(url_string);
        window.timeline_data = response.data;
    });
}
function update_swimlane_records(visual_id, data) {
    return __awaiter(this, void 0, void 0, function* () {
        const url_string = `/api/v1/model/visuals/swimlanes/${visual_id}/`;
        return yield api_patch(url_string, data);
    });
}
function compress_swimlane(visual_id, swimlane_seq_num) {
    return __awaiter(this, void 0, void 0, function* () {
        const url_string = `/api/v1/model/visuals/swimlanes/compress/${visual_id}/${swimlane_seq_num}/`;
        // No payload but it's a put because we update the database
        return yield api_post(url_string, {});
    });
}
function autolayout_swimlane(visual_id, swimlane_seq_num) {
    return __awaiter(this, void 0, void 0, function* () {
        const url_string = `/api/v1/model/visuals/swimlanes/autolayout/${visual_id}/${swimlane_seq_num}/`;
        // No payload but it's a put because we update the database
        return yield api_post(url_string, {});
    });
}
function update_timeline_records(visual_id, data) {
    return __awaiter(this, void 0, void 0, function* () {
        const url_string = `/api/v1/model/visuals/timelines/${visual_id}/`;
        return yield api_patch(url_string, data);
    });
}
function update_visual_activities(visual_id, data) {
    return __awaiter(this, void 0, void 0, function* () {
        const url_string = `/api/v1/model/visuals/activities/${visual_id}/`;
        return yield api_patch(url_string, data);
    });
}
function update_visual_activity_swimlane(visual_id, unique_activity_id, swimlane_id) {
    return __awaiter(this, void 0, void 0, function* () {
        const url_string = `/api/v1/model/visuals/activities/${visual_id}/${unique_activity_id}/${swimlane_id}/`;
        return yield api_patch(url_string, {});
    });
}
function get_style_records() {
    return __awaiter(this, void 0, void 0, function* () {
        console.log("Getting style records...");
        const url_string = "/api/v1/model/visuals/styles/";
        return yield api_get(url_string);
    });
}
function get_shape_records() {
    return __awaiter(this, void 0, void 0, function* () {
        console.log("Getting shape records...");
        const url_string = "/api/v1/model/visuals/shapes/";
        return yield api_get(url_string);
    });
}
function get_visual_settings(visualId) {
    return __awaiter(this, void 0, void 0, function* () {
        console.log("Getting visual settings...");
        const url_string = `/api/v1/model/visuals/${visualId}/`;
        return yield api_get(url_string);
    });
}


/***/ }),

/***/ "./ui_src/plot_visual.ts":
/*!*******************************!*\
  !*** ./ui_src/plot_visual.ts ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   highlight_activity: () => (/* binding */ highlight_activity),
/* harmony export */   initialise_canvases: () => (/* binding */ initialise_canvases),
/* harmony export */   plot_visual: () => (/* binding */ plot_visual)
/* harmony export */ });
const HIGHLIGHT_COLOR = 'white';
const HIGHLIGHT_LINE_WIDTH = 5;
function plot_rectangle(context, object_to_render, scale_factor, highlight_flag) {
    // if highlight flag is set then we just plot the outline in red to highlight the object.
    let plot_function;
    if (highlight_flag) {
        console.log("Highligting...");
        context.strokeStyle = HIGHLIGHT_COLOR; // Hard code for now!
        context.lineWidth = HIGHLIGHT_LINE_WIDTH;
        context.strokeRect(object_to_render.shape_plot_dims.left * scale_factor, object_to_render.shape_plot_dims.top * scale_factor, object_to_render.shape_plot_dims.width * scale_factor, object_to_render.shape_plot_dims.height * scale_factor);
    }
    else {
        context.fillStyle = object_to_render.fill_color;
        context.fillRect(object_to_render.shape_plot_dims.left * scale_factor, object_to_render.shape_plot_dims.top * scale_factor, object_to_render.shape_plot_dims.width * scale_factor, object_to_render.shape_plot_dims.height * scale_factor);
    }
}
function plot_diamond(context, object_to_render, scale_factor, highlight_flag) {
    const half_width = object_to_render.shape_plot_dims.width / 2;
    const half_height = object_to_render.shape_plot_dims.height / 2;
    context.beginPath();
    context.moveTo((object_to_render.shape_plot_dims.left + half_width) * scale_factor, object_to_render.shape_plot_dims.top * scale_factor);
    // top left edge
    context.lineTo((object_to_render.shape_plot_dims.left) * scale_factor, (object_to_render.shape_plot_dims.top + half_height) * scale_factor);
    // bottom left edge
    context.lineTo((object_to_render.shape_plot_dims.left + half_width) * scale_factor, (object_to_render.shape_plot_dims.top + object_to_render.shape_plot_dims.height) * scale_factor);
    // bottom right edge
    context.lineTo((object_to_render.shape_plot_dims.left + object_to_render.shape_plot_dims.width) * scale_factor, (object_to_render.shape_plot_dims.top + half_height) * scale_factor);
    // closing the path automatically creates
    // the top right edge
    context.closePath();
    if (highlight_flag) {
        context.strokeStyle = HIGHLIGHT_COLOR; // Hard code for now!
        context.lineWidth = HIGHLIGHT_LINE_WIDTH;
        context.stroke();
    }
    else {
        context.fillStyle = object_to_render.fill_color;
        context.fill();
    }
}
function plot_bullet(context, object_to_render, scale_factor, highlight_flag) {
    context.beginPath();
    let cornerRadius = (object_to_render.shape_plot_dims.height / 2) * scale_factor;
    context.beginPath();
    const left = object_to_render.shape_plot_dims.left * scale_factor;
    const top = object_to_render.shape_plot_dims.top * scale_factor;
    const width = object_to_render.shape_plot_dims.width * scale_factor;
    const height = object_to_render.shape_plot_dims.height * scale_factor;
    context.roundRect(left, top, width, height, cornerRadius);
    context.closePath();
    if (highlight_flag) {
        context.strokeStyle = HIGHLIGHT_COLOR; // Hard code for now!
        context.lineWidth = HIGHLIGHT_LINE_WIDTH;
        context.stroke();
    }
    else {
        context.fillStyle = object_to_render.fill_color;
        context.fill();
    }
}
function plot_rounded_rectangle(context, object_to_render, scale_factor, highlight_flag) {
    let cornerRadius = ((object_to_render.shape_plot_dims.height / 2) * 0.6) * scale_factor;
    context.beginPath();
    const left = object_to_render.shape_plot_dims.left * scale_factor;
    const top = object_to_render.shape_plot_dims.top * scale_factor;
    const width = object_to_render.shape_plot_dims.width * scale_factor;
    const height = object_to_render.shape_plot_dims.height * scale_factor;
    context.roundRect(left, top, width, height, cornerRadius);
    context.closePath();
    if (highlight_flag) {
        context.strokeStyle = HIGHLIGHT_COLOR; // Hard code for now!
        context.lineWidth = HIGHLIGHT_LINE_WIDTH;
        context.stroke();
    }
    else {
        context.fillStyle = object_to_render.fill_color;
        context.fill();
    }
}
function plot_isosceles_triangle(context, object_to_render, scale_factor, highlight_flag) {
    const left = object_to_render.shape_plot_dims.left * scale_factor;
    const top = object_to_render.shape_plot_dims.top * scale_factor;
    const width = object_to_render.shape_plot_dims.width * scale_factor;
    const height = object_to_render.shape_plot_dims.height * scale_factor;
    context.beginPath();
    // Define a start point
    context.moveTo(left + width / 2, top);
    // Define points
    context.lineTo(left + width, top + height);
    context.lineTo(left, top + height);
    context.closePath();
    if (highlight_flag) {
        context.strokeStyle = HIGHLIGHT_COLOR; // Hard code for now!
        context.lineWidth = HIGHLIGHT_LINE_WIDTH;
        context.stroke();
    }
    else {
        context.fillStyle = object_to_render.fill_color;
        context.fill();
    }
}
function plot_text(context, object_to_render, scale_factor, highlight_flag) {
    // Note for text we are ignoring highlight flag as it doesn't mean anything for text so just plot text anyway.
    console.log(`About to plot text for ${object_to_render.text}, textAlign is ${object_to_render.shape_plot_dims.text_align}`);
    console.log(`About to plot text for ${object_to_render.text}, x is ${object_to_render.shape_plot_dims.x}`);
    context.textAlign = object_to_render.shape_plot_dims.text_align;
    context.textBaseline = object_to_render.shape_plot_dims.text_baseline;
    context.fillStyle = object_to_render.fill_color;
    context.font = `${Math.ceil(object_to_render.font_size * scale_factor)}px sans-serif`;
    console.log(`${object_to_render.font_size} Font = ${context.font}`);
    context.fillText(object_to_render.text, object_to_render.shape_plot_dims.x * scale_factor, object_to_render.shape_plot_dims.y * scale_factor);
}
function plot_shape(object_to_render, context, scale_factor, highlight_flag = false) {
    let action;
    if (highlight_flag)
        action = "HIGHLIGHTING";
    else
        action = "PLOTTING";
    console.log(`${action} shape ${object_to_render.shape_name}, context is ${context}`);
    if (object_to_render.shape_type === 'rectangle' && object_to_render.shape_name === 'RECTANGLE') {
        plot_rectangle(context, object_to_render, scale_factor, highlight_flag);
    }
    else if (object_to_render.shape_type === 'rectangle' && object_to_render.shape_name === 'DIAMOND') {
        plot_diamond(context, object_to_render, scale_factor, highlight_flag);
    }
    else if (object_to_render.shape_type === 'rectangle' && object_to_render.shape_name === 'ROUNDED_RECTANGLE') {
        plot_rounded_rectangle(context, object_to_render, scale_factor, highlight_flag);
    }
    else if (object_to_render.shape_type === 'rectangle' && object_to_render.shape_name === 'BULLET') {
        plot_bullet(context, object_to_render, scale_factor, highlight_flag);
    }
    else if (object_to_render.shape_type === 'rectangle' && object_to_render.shape_name === 'ISOSCELES') {
        plot_isosceles_triangle(context, object_to_render, scale_factor, highlight_flag);
    }
    else if (object_to_render.shape_type === 'text') {
        plot_text(context, object_to_render, scale_factor, highlight_flag);
    }
}
function get_canvas_info() {
    console.log(`get_canvas_info()`);
    const canvas_info = {
        background: document.getElementById("canvas-background").getContext("2d"),
        swimlanes: document.getElementById("canvas-swimlanes").getContext("2d"),
        timelines: document.getElementById("canvas-timelines").getContext("2d"),
        visual_activities: document.getElementById("canvas-activities").getContext("2d"),
        highlight: document.getElementById("canvas-highlight").getContext("2d"),
    };
    return canvas_info;
}
function get_rendered_plotable(plotable_id) {
    // Each plotable object has an id which is unique across all canvasses
    // Iterate through all of them looking for the id we are looking for and return it
    console.log(`Looking for plotable with id ${plotable_id}`);
    let found_object = undefined;
    outerLoop: for (let canvas in window.visual_activity_data) {
        console.log(`Looking in canvas ${canvas}...`);
        const plotable_objects_for_canvas = window.visual_activity_data[canvas];
        console.log(plotable_objects_for_canvas);
        for (let i = 0; i < plotable_objects_for_canvas.length; i++) {
            let plotable_object = plotable_objects_for_canvas[i];
            console.log(`Checking plotable_id ${plotable_object}`);
            // When we get to the entry for the passed in plotable_id we plot it as a highlight
            if (plotable_object.plotable_id == plotable_id) {
                console.log("Found plotable");
                console.log(plotable_object);
                found_object = plotable_object;
                break outerLoop; // this line breaks out of both loops
            }
        }
    }
    return found_object;
}
function highlight_activity(activity_id) {
    // Gets plot information for activity shape and just plots outline on top of visual to highlight
    console.log(`Clearing canvas for highlight`);
    clear_canvas("highlight");
    console.log(`Highlighting element ${activity_id}, context is...`);
    const object_to_highlight = get_rendered_plotable(`activity-${activity_id}`);
    console.log(`Found activity to highlight...`);
    console.log(object_to_highlight);
    plot_shape(object_to_highlight, window.canvas_info.highlight, window.scale_factor, true);
}
function plot_visual(captureImageFlag = false) {
    // If captureImageFlag is set then we are plotting the visual to capture an image of it for download.
    // In that case we need to:
    // - Plot all the elements onto one canvas which isn't part of the DOM.
    // - Don't include highlighting of selected element.
    // - Extract from canvas to an image and return the URL of the image (I think!)
    // Scale factor is calculated so visual fits to width of available screen
    let scaleFactor;
    let canvasInfo = {};
    if (captureImageFlag) {
        console.log(`Capturing visual image`);
        [scaleFactor, canvasInfo] = window.initialise_canvases(true);
        // ToDo: This is a bit of a hack to fix download image bug quickly - come back and fix
        window.canvas_info.capture = canvasInfo.capture;
    }
    else {
        // Since adding dynamic visual height calculation, we need to call initialise_canvases every time we
        // plot the visual.
        [scaleFactor, canvasInfo] = window.initialise_canvases();
    }
    console.log("Plotting activity shapes...");
    console.log(`Selected activity id is ${window.selected_activity_id}`);
    // Don't clear canvases if we are capturing an image of the visual - we don't want to clear the screen.
    if (!captureImageFlag) {
        clear_canvases();
    }
    // Get the div element with id no-activities-alert so we can display or hide it
    const noActivitiesAlert = document.getElementById("no-activities-alert");
    // Check if there are no elements in visual_activity_data
    const hasActivities = Object.values(window.visual_activity_data).some((canvas) => canvas.length > 0);
    if (noActivitiesAlert) {
        // Set display to 'none' if there are activities, otherwise set to 'block'
        if (hasActivities) {
            console.log("Setting 'no-activities-alert' display to 'none'");
            noActivitiesAlert.style.display = "none";
        }
        else {
            console.log("Setting 'no-activities-alert' display to 'block'");
            noActivitiesAlert.style.display = "block";
        }
    }
    // There will be a list of plotable objects for different canvases so need to iterate through canvases
    for (let canvas in window.visual_activity_data) {
        // if we are plotting to capture the image we always use the capture canvas
        // ToDo: Ensure that when rendering for image download we render canvas data from back to front
        let context;
        if (captureImageFlag) {
            context = canvasInfo.capture;
        }
        else {
            context = canvasInfo[canvas];
        }
        const rendered_objects = window.visual_activity_data[canvas];
        // Now iterate through plotables in this canvas
        rendered_objects.forEach((object_to_render) => {
            plot_shape(object_to_render, context, scaleFactor);
            // If this is the current selected element then highlight it unless we are capturing an image of the visual
            if (canvas == "visual_activities" && !captureImageFlag) {
                // Plotable ids have canvas pre-pended for uniqueness so need to strip it off before checking whethe this
                // is the selected id.
                const activity_id_from_plotable_id = object_to_render.plotable_id.substring(9);
                console.log(`Checking whether this element is selected activity: plotable_id is ${activity_id_from_plotable_id}`);
                if (activity_id_from_plotable_id == window.selected_activity_id) {
                    console.log(`Highlighting activity ${object_to_render.plotable_id}`);
                    plot_shape(object_to_render, window.canvas_info.highlight, scaleFactor, true);
                }
            }
        });
    }
}
function clear_canvas(canvas_key) {
    const canvas_ctx = window.canvas_info[canvas_key];
    // Get the context for each canvas
    console.log(`Clearing canvas ${canvas_key}`);
    // Fill the entire canvas
    canvas_ctx.clearRect(0, 0, canvas_ctx.canvas.width, canvas_ctx.canvas.height);
}
function clear_canvases() {
    console.log("Clearing canvases...");
    // Clear canvas before plotting
    for (let key in window.canvas_info) {
        clear_canvas(key);
    }
}
function initialise_canvases(captureOnly = false) {
    // Gets canvases from the DOM to plot the visual on, and sets up the right size both for the HTML element
    // and the canvas element (which will depend upon the DPI for the device).
    // Also adds a canvas called capture which is only used when plotting the visual in order to capture it
    // Either for download or to display a thumbnail (for example).
    // if captureOnly flag is set then we are rendering for image capture so won't need other contexts.
    console.log(`Initialising canvases, capture only flag is ${captureOnly}`);
    // ToDo: Re-factor this or get_canvas_info for when capturing image
    let canvas_info = {};
    if (!captureOnly) {
        canvas_info = get_canvas_info();
    }
    let scale_factor;
    let final_canvas_width = 0;
    let final_canvas_height = 0;
    let initial_canvas_display_width = 0;
    let initial_canvas_display_height = 0;
    let adjusted_canvas_display_height = 0;
    const visual_width = window.visual_settings.width;
    const visual_height = window.visual_settings.visual_height;
    const aspect_ratio = visual_height / visual_width;
    let firstCanvasFlag = true; // Some processing only needed first time round loop so use flag.
    if (!captureOnly) {
        for (let canvas_id in canvas_info) {
            const canvas_details = canvas_info[canvas_id];
            const canvas = canvas_details.canvas;
            if (firstCanvasFlag) {
                // The canvases are all identical so we can use the first one to calculate canvas height and width
                // and calculate the dpi and scale factor and then just apply these to the other canvases
                firstCanvasFlag = false;
                // Manage canvas element to maintain aspect ratio
                console.log(`canvas.offsetWidth = ${canvas.offsetWidth}`);
                // ToDo: Refactor calculation of canvas size to reflect what is being plotted.
                // The canvas will have a width based on the html for the template and the screen it is displayed on
                // We take it and then use that to calculate the resolution of the canvas element to ensure max resolution
                initial_canvas_display_width = canvas.offsetWidth;
                initial_canvas_display_height = canvas.offsetHeight;
                // Increase actual size of canvas for retina display
                let dpi = window.devicePixelRatio;
                console.log(`devicePixelRatio is ${dpi}`);
                // final_canvas_width is the plotable width which will be used when plotting the visual
                final_canvas_width = initial_canvas_display_width * dpi;
                // scale_factor is the factor that dimensions from the rendered visual will need to be multiplied
                // in order to fill the full width of the canvas
                scale_factor = final_canvas_width / visual_width;
                // Now we have the scale_factor we can calculate the true height both of the canvas html element
                // and the plotable height of the canvas so that the visual fits neatly inside the canvas.
                adjusted_canvas_display_height = visual_height / scale_factor;
                final_canvas_height = final_canvas_width * aspect_ratio;
                console.log(`Scale factor is ${scale_factor}`);
            }
            console.log(`Initialise canvas ${canvas_id}: initial_canvas_display_width: ${initial_canvas_display_width}`);
            console.log(`Initialise canvas ${canvas_id}: ajdusted_canvas_display_height: ${adjusted_canvas_display_height}`);
            console.log(`Initialise canvas ${canvas_id}: final_canvas_width:            ${final_canvas_width}`);
            console.log(`Initialise canvas ${canvas_id}: final_canvas_height:           ${final_canvas_height}`);
            canvas.width = final_canvas_width;
            canvas.height = final_canvas_height;
            canvas.style.width = initial_canvas_display_width + "px";
            canvas.style.height = adjusted_canvas_display_height + "px";
        }
    }
    else {
        // Add 'capture' canvas for plotting to download image etc.
        const captureCanvas = document.createElement('canvas');
        captureCanvas.width = 2000; // Hard coding for now
        scale_factor = captureCanvas.width / visual_width;
        captureCanvas.height = 2000; // ToDo: Replace hard coding of canvas width with more sophisticated approach
        canvas_info.capture = captureCanvas.getContext('2d');
    }
    return [scale_factor || 1, canvas_info];
}


/***/ }),

/***/ "./ui_src/utilities.ts":
/*!*****************************!*\
  !*** ./ui_src/utilities.ts ***!
  \*****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   addStylesheetToDOM: () => (/* binding */ addStylesheetToDOM)
/* harmony export */ });
function addStylesheetToDOM(cssFilePath) {
    // Create new link element
    let linkElement = document.createElement('link');
    // Set the relationship to 'stylesheet'
    linkElement.rel = 'stylesheet';
    // Set the href attribute to the given CSS file path
    linkElement.href = cssFilePath;
    // Append the link element to the head of the document
    document.head.appendChild(linkElement);
}


/***/ }),

/***/ "./ui_src/visual.ts":
/*!**************************!*\
  !*** ./ui_src/visual.ts ***!
  \**************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   checkKey: () => (/* binding */ checkKey),
/* harmony export */   getIdFromRowIndex: () => (/* binding */ getIdFromRowIndex),
/* harmony export */   get_activities_from_server: () => (/* binding */ get_activities_from_server),
/* harmony export */   get_activity: () => (/* binding */ get_activity),
/* harmony export */   get_activity_data: () => (/* binding */ get_activity_data),
/* harmony export */   get_rendered_visual: () => (/* binding */ get_rendered_visual),
/* harmony export */   loadActivity: () => (/* binding */ loadActivity),
/* harmony export */   load_activities: () => (/* binding */ load_activities),
/* harmony export */   move: () => (/* binding */ move),
/* harmony export */   selectRow: () => (/* binding */ selectRow),
/* harmony export */   selectRowByIndex: () => (/* binding */ selectRowByIndex),
/* harmony export */   updateActivity: () => (/* binding */ updateActivity),
/* harmony export */   update_server_visual_activity: () => (/* binding */ update_server_visual_activity)
/* harmony export */ });
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! axios */ "./node_modules/axios/lib/axios.js");
/* harmony import */ var _drawing__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./drawing */ "./ui_src/drawing.ts");
/* harmony import */ var _plot_visual__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./plot_visual */ "./ui_src/plot_visual.ts");



var return_data;
function get_activity_data() {
    let json_activities = document.getElementById("json_activities");
    console.log("json_activities - " + json_activities);
    if (json_activities.textContent == null) {
        return {};
    }
    else {
        return JSON.parse(json_activities.textContent);
    }
}
function get_activities_from_server(visual_id) {
    axios__WEBPACK_IMPORTED_MODULE_2__["default"].defaults.xsrfCookieName = 'csrftoken';
    axios__WEBPACK_IMPORTED_MODULE_2__["default"].defaults.xsrfHeaderName = "X-CSRFTOKEN";
    var url_string = `/api/v1/visual_activities/${visual_id}/`;
    axios__WEBPACK_IMPORTED_MODULE_2__["default"].get(url_string)
        .then((response) => {
        return_data = response.data;
        load_activities(JSON.parse(return_data));
    })
        .catch(error => {
        console.log("Error...");
        console.log(error);
    });
}
function get_activity(visual_id, unique_activity_id) {
    axios__WEBPACK_IMPORTED_MODULE_2__["default"].defaults.xsrfCookieName = 'csrftoken';
    axios__WEBPACK_IMPORTED_MODULE_2__["default"].defaults.xsrfHeaderName = "X-CSRFTOKEN";
    var url_string = `/api/v1/visual_activities/${visual_id}/${unique_activity_id}`;
    axios__WEBPACK_IMPORTED_MODULE_2__["default"].get(url_string)
        .then((response) => {
        return_data = response.data;
        loadActivity(JSON.parse(return_data));
    })
        .catch(error => {
        console.log("Error...");
        console.log(error);
    });
}
function load_activities(activities) {
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
function loadActivity(activity_data) {
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
                axios__WEBPACK_IMPORTED_MODULE_2__["default"].patch(url_string, data)
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
function selectRow(tr) {
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
function selectRowByIndex(row_index) {
    // Set row at row_index as selected
    console.log("selectRowByIndex called...");
    console.log(row_index);
    let layout_table = document.getElementById("activities_table");
    console.log("layout_table: " + layout_table);
    let indexed_row = layout_table.rows[row_index - 1];
    return selectRow(indexed_row);
}
function move(direction) {
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
function getIdFromRowIndex(row_index) {
    let layout_table = document.getElementById("activities_table");
    let activity_row = layout_table.rows[row_index];
    return activity_row.getElementsByClassName("unique_id")[0].innerHTML;
}
function updateActivity(row_index) {
    console.log(`UpdateActivity called for activity row ${row_index}`);
    let activity_id = getIdFromRowIndex(row_index);
    console.log(`UpdateActivity called for activity id ${activity_id}`);
    let visual_id = document.getElementsByTagName("body")[0].id;
    get_activity(visual_id, activity_id);
}
function checkKey(event) {
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
function update_server_visual_activity(visual_id, activity_id, activity_data) {
    axios__WEBPACK_IMPORTED_MODULE_2__["default"].defaults.xsrfCookieName = 'csrftoken';
    axios__WEBPACK_IMPORTED_MODULE_2__["default"].defaults.xsrfHeaderName = "X-CSRFTOKEN";
    var url_string = `/api/v1/visual_activities/${visual_id}/${activity_id}`;
    axios__WEBPACK_IMPORTED_MODULE_2__["default"].put(url_string, activity_data)
        .then((response) => {
        return_data = response.data;
        loadActivity(JSON.parse(return_data));
    })
        .catch(error => {
        console.log("Error...");
        console.log(error);
    });
}
function get_rendered_visual(visual_id) {
    axios__WEBPACK_IMPORTED_MODULE_2__["default"].defaults.xsrfCookieName = 'csrftoken';
    axios__WEBPACK_IMPORTED_MODULE_2__["default"].defaults.xsrfHeaderName = "X-CSRFTOKEN";
    var url_string = `/api/v1/visual_activities/rendered/${visual_id}/`;
    axios__WEBPACK_IMPORTED_MODULE_2__["default"].get(url_string)
        .then((response) => {
        let visual = JSON.parse(response.data);
        console.log("visual: " + visual);
        let visual_settings = visual.settings;
        console.log("visual_settings: " + visual_settings);
        const visual_activities = visual['shapes'];
        console.log("visual_activities: " + visual_activities);
        let context = (0,_drawing__WEBPACK_IMPORTED_MODULE_0__.initialise_canvas)(visual_settings);
        (0,_plot_visual__WEBPACK_IMPORTED_MODULE_1__.plot_visual)();
    })
        .catch(error => {
        console.log("Error...");
        console.log(error);
    });
}


/***/ }),

/***/ "./ui_src/widgets.ts":
/*!***************************!*\
  !*** ./ui_src/widgets.ts ***!
  \***************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   Dropdown: () => (/* binding */ Dropdown),
/* harmony export */   add_tooltip: () => (/* binding */ add_tooltip),
/* harmony export */   clearElement: () => (/* binding */ clearElement),
/* harmony export */   createDropdown: () => (/* binding */ createDropdown),
/* harmony export */   create_button_with_icon: () => (/* binding */ create_button_with_icon),
/* harmony export */   populateDropdown: () => (/* binding */ populateDropdown)
/* harmony export */ });
/* harmony import */ var _plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./plan_visualiser_api */ "./ui_src/plan_visualiser_api.ts");
/* harmony import */ var _plot_visual__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./plot_visual */ "./ui_src/plot_visual.ts");
var __awaiter = (undefined && undefined.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};


class Dropdown {
    constructor(id, activity_unique_id, options, select_handler) {
        this.activity_unique_id = activity_unique_id;
        this.options = options;
        this.element = document.getElementById(id);
        this.selectedOption = this.options[0][0];
        this.select_handler = select_handler;
        this.generate();
    }
    generate() {
        return __awaiter(this, void 0, void 0, function* () {
            const select = document.createElement('select');
            select.id = "select_element";
            this.options.forEach(option => {
                const option_text = option[0];
                const option_id = option[1];
                const optElement = document.createElement('option');
                optElement.text = option_text;
                optElement.value = option_text;
                optElement.id = option_id.toString();
                select.add(optElement);
            });
            select.addEventListener('click', (event) => __awaiter(this, void 0, void 0, function* () {
                const targetSelectedElement = event.target;
                const targetOptionElement = targetSelectedElement.options[targetSelectedElement.selectedIndex];
                const swimlane_id = parseInt(targetOptionElement.id);
                console.log(`Swimlane selected: text:${this.selectedOption}, id:${swimlane_id}`);
                yield this.select_handler(this.activity_unique_id, swimlane_id);
                yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_activity_data)(window.visual_id);
                // Need visual settings as it included visual height which is needed to plot.
                const response = yield (0,_plan_visualiser_api__WEBPACK_IMPORTED_MODULE_0__.get_visual_settings)(window.visual_id);
                window.visual_settings = response.data;
                (0,_plot_visual__WEBPACK_IMPORTED_MODULE_1__.plot_visual)();
            }));
            if (this.element) {
                this.element.appendChild(select);
            }
        });
    }
}
function create_button_with_icon(icon_name) {
    const button = document.createElement("button");
    button.classList.add("btn", "btn-primary");
    let iconElement = document.createElement('i');
    iconElement.classList.add("bi", icon_name);
    button.appendChild(iconElement);
    return button;
}
function add_tooltip(element, tooltip_text) {
    return __awaiter(this, void 0, void 0, function* () {
        element.setAttribute("data-bs-toggle", "tooltip");
        element.setAttribute("data-bs-placement", "top");
        element.setAttribute("title", tooltip_text);
    });
}
function clearElement(element) {
    element.textContent = '';
}
function createDropdown(parentElement, buttonLabel, classesToAdd) {
    console.log(`Creating dropdown with initial value ${buttonLabel} under ${parentElement}`);
    const dropdownDiv = document.createElement("div");
    dropdownDiv.classList.add("dropdown");
    parentElement.appendChild(dropdownDiv);
    // Add button to Dropdown
    const dropdownButton = document.createElement("button");
    dropdownButton.style.width = "100%"; // TEMP Proof of concept to get text-truncate working.
    dropdownButton.setAttribute("type", "button");
    dropdownButton.setAttribute("data-bs-toggle", "dropdown");
    dropdownButton.setAttribute("aria-expanded", "false");
    dropdownButton.classList.add("btn", "btn-sm", "btn-secondary", "dropdown-toggle");
    if (classesToAdd) {
        dropdownButton.classList.add(...classesToAdd);
    }
    // Add text for button as a span element to allow .text-truncate to work without removing the button icon
    // NOTE: I'm not exactly sure why this works! Got here by trial and error.
    const spanElement = document.createElement("span");
    spanElement.classList.add("text-truncate");
    const stylingForDropdown = "display: inline-block;" +
        "vertical-align: top;" +
        "width: 90%";
    spanElement.style.cssText = stylingForDropdown;
    spanElement.textContent = buttonLabel;
    dropdownButton.appendChild(spanElement);
    dropdownDiv.appendChild(dropdownButton);
    // Add dropdown menu to Dropdown
    const dropdownMenu = document.createElement("ul");
    dropdownMenu.classList.add("dropdown-menu");
    dropdownDiv.appendChild(dropdownMenu);
    return dropdownButton;
}
function populateDropdown(dropdownButton, names, updateHandler) {
    console.log(`Populating dropdown...`);
    names.forEach((name) => {
        const entry = document.createElement('li');
        entry.classList.add("dropdown-item");
        entry.setAttribute("href", "#");
        entry.setAttribute("id", String(name[1]));
        entry.textContent = name[0];
        entry.addEventListener('click', function (event) {
            return __awaiter(this, void 0, void 0, function* () {
                console.log(`New selection for element, ${event.target}`);
                const targetSelectedElement = event.target;
                const id = parseInt(targetSelectedElement.id);
                console.log(`Selected: text:${targetSelectedElement.textContent}, id:${id}`);
                // Update text for span element to selected option
                const dropdownSpan = dropdownButton.querySelector("span");
                dropdownSpan.textContent = targetSelectedElement.textContent;
                yield updateHandler(id); // Pass update functions as arguments
            });
        });
        dropdownButton.parentElement.querySelector('.dropdown-menu').appendChild(entry);
    });
}


/***/ }),

/***/ "./node_modules/axios/index.js":
/*!*************************************!*\
  !*** ./node_modules/axios/index.js ***!
  \*************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   Axios: () => (/* binding */ Axios),
/* harmony export */   AxiosError: () => (/* binding */ AxiosError),
/* harmony export */   AxiosHeaders: () => (/* binding */ AxiosHeaders),
/* harmony export */   Cancel: () => (/* binding */ Cancel),
/* harmony export */   CancelToken: () => (/* binding */ CancelToken),
/* harmony export */   CanceledError: () => (/* binding */ CanceledError),
/* harmony export */   HttpStatusCode: () => (/* binding */ HttpStatusCode),
/* harmony export */   VERSION: () => (/* binding */ VERSION),
/* harmony export */   all: () => (/* binding */ all),
/* harmony export */   "default": () => (/* reexport safe */ _lib_axios_js__WEBPACK_IMPORTED_MODULE_0__["default"]),
/* harmony export */   formToJSON: () => (/* binding */ formToJSON),
/* harmony export */   getAdapter: () => (/* binding */ getAdapter),
/* harmony export */   isAxiosError: () => (/* binding */ isAxiosError),
/* harmony export */   isCancel: () => (/* binding */ isCancel),
/* harmony export */   mergeConfig: () => (/* binding */ mergeConfig),
/* harmony export */   spread: () => (/* binding */ spread),
/* harmony export */   toFormData: () => (/* binding */ toFormData)
/* harmony export */ });
/* harmony import */ var _lib_axios_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./lib/axios.js */ "./node_modules/axios/lib/axios.js");


// This module is intended to unwrap Axios default export as named.
// Keep top-level export same with static properties
// so that it can keep same with es module or cjs
const {
  Axios,
  AxiosError,
  CanceledError,
  isCancel,
  CancelToken,
  VERSION,
  all,
  Cancel,
  isAxiosError,
  spread,
  toFormData,
  AxiosHeaders,
  HttpStatusCode,
  formToJSON,
  getAdapter,
  mergeConfig
} = _lib_axios_js__WEBPACK_IMPORTED_MODULE_0__["default"];




/***/ }),

/***/ "./node_modules/axios/lib/adapters/adapters.js":
/*!*****************************************************!*\
  !*** ./node_modules/axios/lib/adapters/adapters.js ***!
  \*****************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../utils.js */ "./node_modules/axios/lib/utils.js");
/* harmony import */ var _http_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./http.js */ "./node_modules/axios/lib/helpers/null.js");
/* harmony import */ var _xhr_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./xhr.js */ "./node_modules/axios/lib/adapters/xhr.js");
/* harmony import */ var _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../core/AxiosError.js */ "./node_modules/axios/lib/core/AxiosError.js");





const knownAdapters = {
  http: _http_js__WEBPACK_IMPORTED_MODULE_0__["default"],
  xhr: _xhr_js__WEBPACK_IMPORTED_MODULE_1__["default"]
}

_utils_js__WEBPACK_IMPORTED_MODULE_2__["default"].forEach(knownAdapters, (fn, value) => {
  if (fn) {
    try {
      Object.defineProperty(fn, 'name', {value});
    } catch (e) {
      // eslint-disable-next-line no-empty
    }
    Object.defineProperty(fn, 'adapterName', {value});
  }
});

const renderReason = (reason) => `- ${reason}`;

const isResolvedHandle = (adapter) => _utils_js__WEBPACK_IMPORTED_MODULE_2__["default"].isFunction(adapter) || adapter === null || adapter === false;

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ({
  getAdapter: (adapters) => {
    adapters = _utils_js__WEBPACK_IMPORTED_MODULE_2__["default"].isArray(adapters) ? adapters : [adapters];

    const {length} = adapters;
    let nameOrAdapter;
    let adapter;

    const rejectedReasons = {};

    for (let i = 0; i < length; i++) {
      nameOrAdapter = adapters[i];
      let id;

      adapter = nameOrAdapter;

      if (!isResolvedHandle(nameOrAdapter)) {
        adapter = knownAdapters[(id = String(nameOrAdapter)).toLowerCase()];

        if (adapter === undefined) {
          throw new _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_3__["default"](`Unknown adapter '${id}'`);
        }
      }

      if (adapter) {
        break;
      }

      rejectedReasons[id || '#' + i] = adapter;
    }

    if (!adapter) {

      const reasons = Object.entries(rejectedReasons)
        .map(([id, state]) => `adapter ${id} ` +
          (state === false ? 'is not supported by the environment' : 'is not available in the build')
        );

      let s = length ?
        (reasons.length > 1 ? 'since :\n' + reasons.map(renderReason).join('\n') : ' ' + renderReason(reasons[0])) :
        'as no adapter specified';

      throw new _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_3__["default"](
        `There is no suitable adapter to dispatch the request ` + s,
        'ERR_NOT_SUPPORT'
      );
    }

    return adapter;
  },
  adapters: knownAdapters
});


/***/ }),

/***/ "./node_modules/axios/lib/adapters/xhr.js":
/*!************************************************!*\
  !*** ./node_modules/axios/lib/adapters/xhr.js ***!
  \************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./../utils.js */ "./node_modules/axios/lib/utils.js");
/* harmony import */ var _core_settle_js__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./../core/settle.js */ "./node_modules/axios/lib/core/settle.js");
/* harmony import */ var _helpers_cookies_js__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./../helpers/cookies.js */ "./node_modules/axios/lib/helpers/cookies.js");
/* harmony import */ var _helpers_buildURL_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./../helpers/buildURL.js */ "./node_modules/axios/lib/helpers/buildURL.js");
/* harmony import */ var _core_buildFullPath_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../core/buildFullPath.js */ "./node_modules/axios/lib/core/buildFullPath.js");
/* harmony import */ var _helpers_isURLSameOrigin_js__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./../helpers/isURLSameOrigin.js */ "./node_modules/axios/lib/helpers/isURLSameOrigin.js");
/* harmony import */ var _defaults_transitional_js__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../defaults/transitional.js */ "./node_modules/axios/lib/defaults/transitional.js");
/* harmony import */ var _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../core/AxiosError.js */ "./node_modules/axios/lib/core/AxiosError.js");
/* harmony import */ var _cancel_CanceledError_js__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ../cancel/CanceledError.js */ "./node_modules/axios/lib/cancel/CanceledError.js");
/* harmony import */ var _helpers_parseProtocol_js__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ../helpers/parseProtocol.js */ "./node_modules/axios/lib/helpers/parseProtocol.js");
/* harmony import */ var _platform_index_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../platform/index.js */ "./node_modules/axios/lib/platform/index.js");
/* harmony import */ var _core_AxiosHeaders_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../core/AxiosHeaders.js */ "./node_modules/axios/lib/core/AxiosHeaders.js");
/* harmony import */ var _helpers_speedometer_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../helpers/speedometer.js */ "./node_modules/axios/lib/helpers/speedometer.js");
















function progressEventReducer(listener, isDownloadStream) {
  let bytesNotified = 0;
  const _speedometer = (0,_helpers_speedometer_js__WEBPACK_IMPORTED_MODULE_0__["default"])(50, 250);

  return e => {
    const loaded = e.loaded;
    const total = e.lengthComputable ? e.total : undefined;
    const progressBytes = loaded - bytesNotified;
    const rate = _speedometer(progressBytes);
    const inRange = loaded <= total;

    bytesNotified = loaded;

    const data = {
      loaded,
      total,
      progress: total ? (loaded / total) : undefined,
      bytes: progressBytes,
      rate: rate ? rate : undefined,
      estimated: rate && total && inRange ? (total - loaded) / rate : undefined,
      event: e
    };

    data[isDownloadStream ? 'download' : 'upload'] = true;

    listener(data);
  };
}

const isXHRAdapterSupported = typeof XMLHttpRequest !== 'undefined';

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (isXHRAdapterSupported && function (config) {
  return new Promise(function dispatchXhrRequest(resolve, reject) {
    let requestData = config.data;
    const requestHeaders = _core_AxiosHeaders_js__WEBPACK_IMPORTED_MODULE_1__["default"].from(config.headers).normalize();
    let {responseType, withXSRFToken} = config;
    let onCanceled;
    function done() {
      if (config.cancelToken) {
        config.cancelToken.unsubscribe(onCanceled);
      }

      if (config.signal) {
        config.signal.removeEventListener('abort', onCanceled);
      }
    }

    let contentType;

    if (_utils_js__WEBPACK_IMPORTED_MODULE_2__["default"].isFormData(requestData)) {
      if (_platform_index_js__WEBPACK_IMPORTED_MODULE_3__["default"].hasStandardBrowserEnv || _platform_index_js__WEBPACK_IMPORTED_MODULE_3__["default"].hasStandardBrowserWebWorkerEnv) {
        requestHeaders.setContentType(false); // Let the browser set it
      } else if ((contentType = requestHeaders.getContentType()) !== false) {
        // fix semicolon duplication issue for ReactNative FormData implementation
        const [type, ...tokens] = contentType ? contentType.split(';').map(token => token.trim()).filter(Boolean) : [];
        requestHeaders.setContentType([type || 'multipart/form-data', ...tokens].join('; '));
      }
    }

    let request = new XMLHttpRequest();

    // HTTP basic authentication
    if (config.auth) {
      const username = config.auth.username || '';
      const password = config.auth.password ? unescape(encodeURIComponent(config.auth.password)) : '';
      requestHeaders.set('Authorization', 'Basic ' + btoa(username + ':' + password));
    }

    const fullPath = (0,_core_buildFullPath_js__WEBPACK_IMPORTED_MODULE_4__["default"])(config.baseURL, config.url);

    request.open(config.method.toUpperCase(), (0,_helpers_buildURL_js__WEBPACK_IMPORTED_MODULE_5__["default"])(fullPath, config.params, config.paramsSerializer), true);

    // Set the request timeout in MS
    request.timeout = config.timeout;

    function onloadend() {
      if (!request) {
        return;
      }
      // Prepare the response
      const responseHeaders = _core_AxiosHeaders_js__WEBPACK_IMPORTED_MODULE_1__["default"].from(
        'getAllResponseHeaders' in request && request.getAllResponseHeaders()
      );
      const responseData = !responseType || responseType === 'text' || responseType === 'json' ?
        request.responseText : request.response;
      const response = {
        data: responseData,
        status: request.status,
        statusText: request.statusText,
        headers: responseHeaders,
        config,
        request
      };

      (0,_core_settle_js__WEBPACK_IMPORTED_MODULE_6__["default"])(function _resolve(value) {
        resolve(value);
        done();
      }, function _reject(err) {
        reject(err);
        done();
      }, response);

      // Clean up request
      request = null;
    }

    if ('onloadend' in request) {
      // Use onloadend if available
      request.onloadend = onloadend;
    } else {
      // Listen for ready state to emulate onloadend
      request.onreadystatechange = function handleLoad() {
        if (!request || request.readyState !== 4) {
          return;
        }

        // The request errored out and we didn't get a response, this will be
        // handled by onerror instead
        // With one exception: request that using file: protocol, most browsers
        // will return status as 0 even though it's a successful request
        if (request.status === 0 && !(request.responseURL && request.responseURL.indexOf('file:') === 0)) {
          return;
        }
        // readystate handler is calling before onerror or ontimeout handlers,
        // so we should call onloadend on the next 'tick'
        setTimeout(onloadend);
      };
    }

    // Handle browser request cancellation (as opposed to a manual cancellation)
    request.onabort = function handleAbort() {
      if (!request) {
        return;
      }

      reject(new _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_7__["default"]('Request aborted', _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_7__["default"].ECONNABORTED, config, request));

      // Clean up request
      request = null;
    };

    // Handle low level network errors
    request.onerror = function handleError() {
      // Real errors are hidden from us by the browser
      // onerror should only fire if it's a network error
      reject(new _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_7__["default"]('Network Error', _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_7__["default"].ERR_NETWORK, config, request));

      // Clean up request
      request = null;
    };

    // Handle timeout
    request.ontimeout = function handleTimeout() {
      let timeoutErrorMessage = config.timeout ? 'timeout of ' + config.timeout + 'ms exceeded' : 'timeout exceeded';
      const transitional = config.transitional || _defaults_transitional_js__WEBPACK_IMPORTED_MODULE_8__["default"];
      if (config.timeoutErrorMessage) {
        timeoutErrorMessage = config.timeoutErrorMessage;
      }
      reject(new _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_7__["default"](
        timeoutErrorMessage,
        transitional.clarifyTimeoutError ? _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_7__["default"].ETIMEDOUT : _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_7__["default"].ECONNABORTED,
        config,
        request));

      // Clean up request
      request = null;
    };

    // Add xsrf header
    // This is only done if running in a standard browser environment.
    // Specifically not if we're in a web worker, or react-native.
    if(_platform_index_js__WEBPACK_IMPORTED_MODULE_3__["default"].hasStandardBrowserEnv) {
      withXSRFToken && _utils_js__WEBPACK_IMPORTED_MODULE_2__["default"].isFunction(withXSRFToken) && (withXSRFToken = withXSRFToken(config));

      if (withXSRFToken || (withXSRFToken !== false && (0,_helpers_isURLSameOrigin_js__WEBPACK_IMPORTED_MODULE_9__["default"])(fullPath))) {
        // Add xsrf header
        const xsrfValue = config.xsrfHeaderName && config.xsrfCookieName && _helpers_cookies_js__WEBPACK_IMPORTED_MODULE_10__["default"].read(config.xsrfCookieName);

        if (xsrfValue) {
          requestHeaders.set(config.xsrfHeaderName, xsrfValue);
        }
      }
    }

    // Remove Content-Type if data is undefined
    requestData === undefined && requestHeaders.setContentType(null);

    // Add headers to the request
    if ('setRequestHeader' in request) {
      _utils_js__WEBPACK_IMPORTED_MODULE_2__["default"].forEach(requestHeaders.toJSON(), function setRequestHeader(val, key) {
        request.setRequestHeader(key, val);
      });
    }

    // Add withCredentials to request if needed
    if (!_utils_js__WEBPACK_IMPORTED_MODULE_2__["default"].isUndefined(config.withCredentials)) {
      request.withCredentials = !!config.withCredentials;
    }

    // Add responseType to request if needed
    if (responseType && responseType !== 'json') {
      request.responseType = config.responseType;
    }

    // Handle progress if needed
    if (typeof config.onDownloadProgress === 'function') {
      request.addEventListener('progress', progressEventReducer(config.onDownloadProgress, true));
    }

    // Not all browsers support upload events
    if (typeof config.onUploadProgress === 'function' && request.upload) {
      request.upload.addEventListener('progress', progressEventReducer(config.onUploadProgress));
    }

    if (config.cancelToken || config.signal) {
      // Handle cancellation
      // eslint-disable-next-line func-names
      onCanceled = cancel => {
        if (!request) {
          return;
        }
        reject(!cancel || cancel.type ? new _cancel_CanceledError_js__WEBPACK_IMPORTED_MODULE_11__["default"](null, config, request) : cancel);
        request.abort();
        request = null;
      };

      config.cancelToken && config.cancelToken.subscribe(onCanceled);
      if (config.signal) {
        config.signal.aborted ? onCanceled() : config.signal.addEventListener('abort', onCanceled);
      }
    }

    const protocol = (0,_helpers_parseProtocol_js__WEBPACK_IMPORTED_MODULE_12__["default"])(fullPath);

    if (protocol && _platform_index_js__WEBPACK_IMPORTED_MODULE_3__["default"].protocols.indexOf(protocol) === -1) {
      reject(new _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_7__["default"]('Unsupported protocol ' + protocol + ':', _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_7__["default"].ERR_BAD_REQUEST, config));
      return;
    }


    // Send the request
    request.send(requestData || null);
  });
});


/***/ }),

/***/ "./node_modules/axios/lib/axios.js":
/*!*****************************************!*\
  !*** ./node_modules/axios/lib/axios.js ***!
  \*****************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./utils.js */ "./node_modules/axios/lib/utils.js");
/* harmony import */ var _helpers_bind_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./helpers/bind.js */ "./node_modules/axios/lib/helpers/bind.js");
/* harmony import */ var _core_Axios_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./core/Axios.js */ "./node_modules/axios/lib/core/Axios.js");
/* harmony import */ var _core_mergeConfig_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./core/mergeConfig.js */ "./node_modules/axios/lib/core/mergeConfig.js");
/* harmony import */ var _defaults_index_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./defaults/index.js */ "./node_modules/axios/lib/defaults/index.js");
/* harmony import */ var _helpers_formDataToJSON_js__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! ./helpers/formDataToJSON.js */ "./node_modules/axios/lib/helpers/formDataToJSON.js");
/* harmony import */ var _cancel_CanceledError_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./cancel/CanceledError.js */ "./node_modules/axios/lib/cancel/CanceledError.js");
/* harmony import */ var _cancel_CancelToken_js__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./cancel/CancelToken.js */ "./node_modules/axios/lib/cancel/CancelToken.js");
/* harmony import */ var _cancel_isCancel_js__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./cancel/isCancel.js */ "./node_modules/axios/lib/cancel/isCancel.js");
/* harmony import */ var _env_data_js__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./env/data.js */ "./node_modules/axios/lib/env/data.js");
/* harmony import */ var _helpers_toFormData_js__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./helpers/toFormData.js */ "./node_modules/axios/lib/helpers/toFormData.js");
/* harmony import */ var _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./core/AxiosError.js */ "./node_modules/axios/lib/core/AxiosError.js");
/* harmony import */ var _helpers_spread_js__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ./helpers/spread.js */ "./node_modules/axios/lib/helpers/spread.js");
/* harmony import */ var _helpers_isAxiosError_js__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ./helpers/isAxiosError.js */ "./node_modules/axios/lib/helpers/isAxiosError.js");
/* harmony import */ var _core_AxiosHeaders_js__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! ./core/AxiosHeaders.js */ "./node_modules/axios/lib/core/AxiosHeaders.js");
/* harmony import */ var _adapters_adapters_js__WEBPACK_IMPORTED_MODULE_15__ = __webpack_require__(/*! ./adapters/adapters.js */ "./node_modules/axios/lib/adapters/adapters.js");
/* harmony import */ var _helpers_HttpStatusCode_js__WEBPACK_IMPORTED_MODULE_16__ = __webpack_require__(/*! ./helpers/HttpStatusCode.js */ "./node_modules/axios/lib/helpers/HttpStatusCode.js");




















/**
 * Create an instance of Axios
 *
 * @param {Object} defaultConfig The default config for the instance
 *
 * @returns {Axios} A new instance of Axios
 */
function createInstance(defaultConfig) {
  const context = new _core_Axios_js__WEBPACK_IMPORTED_MODULE_0__["default"](defaultConfig);
  const instance = (0,_helpers_bind_js__WEBPACK_IMPORTED_MODULE_1__["default"])(_core_Axios_js__WEBPACK_IMPORTED_MODULE_0__["default"].prototype.request, context);

  // Copy axios.prototype to instance
  _utils_js__WEBPACK_IMPORTED_MODULE_2__["default"].extend(instance, _core_Axios_js__WEBPACK_IMPORTED_MODULE_0__["default"].prototype, context, {allOwnKeys: true});

  // Copy context to instance
  _utils_js__WEBPACK_IMPORTED_MODULE_2__["default"].extend(instance, context, null, {allOwnKeys: true});

  // Factory for creating new instances
  instance.create = function create(instanceConfig) {
    return createInstance((0,_core_mergeConfig_js__WEBPACK_IMPORTED_MODULE_3__["default"])(defaultConfig, instanceConfig));
  };

  return instance;
}

// Create the default instance to be exported
const axios = createInstance(_defaults_index_js__WEBPACK_IMPORTED_MODULE_4__["default"]);

// Expose Axios class to allow class inheritance
axios.Axios = _core_Axios_js__WEBPACK_IMPORTED_MODULE_0__["default"];

// Expose Cancel & CancelToken
axios.CanceledError = _cancel_CanceledError_js__WEBPACK_IMPORTED_MODULE_5__["default"];
axios.CancelToken = _cancel_CancelToken_js__WEBPACK_IMPORTED_MODULE_6__["default"];
axios.isCancel = _cancel_isCancel_js__WEBPACK_IMPORTED_MODULE_7__["default"];
axios.VERSION = _env_data_js__WEBPACK_IMPORTED_MODULE_8__.VERSION;
axios.toFormData = _helpers_toFormData_js__WEBPACK_IMPORTED_MODULE_9__["default"];

// Expose AxiosError class
axios.AxiosError = _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_10__["default"];

// alias for CanceledError for backward compatibility
axios.Cancel = axios.CanceledError;

// Expose all/spread
axios.all = function all(promises) {
  return Promise.all(promises);
};

axios.spread = _helpers_spread_js__WEBPACK_IMPORTED_MODULE_11__["default"];

// Expose isAxiosError
axios.isAxiosError = _helpers_isAxiosError_js__WEBPACK_IMPORTED_MODULE_12__["default"];

// Expose mergeConfig
axios.mergeConfig = _core_mergeConfig_js__WEBPACK_IMPORTED_MODULE_3__["default"];

axios.AxiosHeaders = _core_AxiosHeaders_js__WEBPACK_IMPORTED_MODULE_13__["default"];

axios.formToJSON = thing => (0,_helpers_formDataToJSON_js__WEBPACK_IMPORTED_MODULE_14__["default"])(_utils_js__WEBPACK_IMPORTED_MODULE_2__["default"].isHTMLForm(thing) ? new FormData(thing) : thing);

axios.getAdapter = _adapters_adapters_js__WEBPACK_IMPORTED_MODULE_15__["default"].getAdapter;

axios.HttpStatusCode = _helpers_HttpStatusCode_js__WEBPACK_IMPORTED_MODULE_16__["default"];

axios.default = axios;

// this module should only have a default export
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (axios);


/***/ }),

/***/ "./node_modules/axios/lib/cancel/CancelToken.js":
/*!******************************************************!*\
  !*** ./node_modules/axios/lib/cancel/CancelToken.js ***!
  \******************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _CanceledError_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./CanceledError.js */ "./node_modules/axios/lib/cancel/CanceledError.js");




/**
 * A `CancelToken` is an object that can be used to request cancellation of an operation.
 *
 * @param {Function} executor The executor function.
 *
 * @returns {CancelToken}
 */
class CancelToken {
  constructor(executor) {
    if (typeof executor !== 'function') {
      throw new TypeError('executor must be a function.');
    }

    let resolvePromise;

    this.promise = new Promise(function promiseExecutor(resolve) {
      resolvePromise = resolve;
    });

    const token = this;

    // eslint-disable-next-line func-names
    this.promise.then(cancel => {
      if (!token._listeners) return;

      let i = token._listeners.length;

      while (i-- > 0) {
        token._listeners[i](cancel);
      }
      token._listeners = null;
    });

    // eslint-disable-next-line func-names
    this.promise.then = onfulfilled => {
      let _resolve;
      // eslint-disable-next-line func-names
      const promise = new Promise(resolve => {
        token.subscribe(resolve);
        _resolve = resolve;
      }).then(onfulfilled);

      promise.cancel = function reject() {
        token.unsubscribe(_resolve);
      };

      return promise;
    };

    executor(function cancel(message, config, request) {
      if (token.reason) {
        // Cancellation has already been requested
        return;
      }

      token.reason = new _CanceledError_js__WEBPACK_IMPORTED_MODULE_0__["default"](message, config, request);
      resolvePromise(token.reason);
    });
  }

  /**
   * Throws a `CanceledError` if cancellation has been requested.
   */
  throwIfRequested() {
    if (this.reason) {
      throw this.reason;
    }
  }

  /**
   * Subscribe to the cancel signal
   */

  subscribe(listener) {
    if (this.reason) {
      listener(this.reason);
      return;
    }

    if (this._listeners) {
      this._listeners.push(listener);
    } else {
      this._listeners = [listener];
    }
  }

  /**
   * Unsubscribe from the cancel signal
   */

  unsubscribe(listener) {
    if (!this._listeners) {
      return;
    }
    const index = this._listeners.indexOf(listener);
    if (index !== -1) {
      this._listeners.splice(index, 1);
    }
  }

  /**
   * Returns an object that contains a new `CancelToken` and a function that, when called,
   * cancels the `CancelToken`.
   */
  static source() {
    let cancel;
    const token = new CancelToken(function executor(c) {
      cancel = c;
    });
    return {
      token,
      cancel
    };
  }
}

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (CancelToken);


/***/ }),

/***/ "./node_modules/axios/lib/cancel/CanceledError.js":
/*!********************************************************!*\
  !*** ./node_modules/axios/lib/cancel/CanceledError.js ***!
  \********************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../core/AxiosError.js */ "./node_modules/axios/lib/core/AxiosError.js");
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../utils.js */ "./node_modules/axios/lib/utils.js");





/**
 * A `CanceledError` is an object that is thrown when an operation is canceled.
 *
 * @param {string=} message The message.
 * @param {Object=} config The config.
 * @param {Object=} request The request.
 *
 * @returns {CanceledError} The created error.
 */
function CanceledError(message, config, request) {
  // eslint-disable-next-line no-eq-null,eqeqeq
  _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_0__["default"].call(this, message == null ? 'canceled' : message, _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_0__["default"].ERR_CANCELED, config, request);
  this.name = 'CanceledError';
}

_utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].inherits(CanceledError, _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_0__["default"], {
  __CANCEL__: true
});

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (CanceledError);


/***/ }),

/***/ "./node_modules/axios/lib/cancel/isCancel.js":
/*!***************************************************!*\
  !*** ./node_modules/axios/lib/cancel/isCancel.js ***!
  \***************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ isCancel)
/* harmony export */ });


function isCancel(value) {
  return !!(value && value.__CANCEL__);
}


/***/ }),

/***/ "./node_modules/axios/lib/core/Axios.js":
/*!**********************************************!*\
  !*** ./node_modules/axios/lib/core/Axios.js ***!
  \**********************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./../utils.js */ "./node_modules/axios/lib/utils.js");
/* harmony import */ var _helpers_buildURL_js__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../helpers/buildURL.js */ "./node_modules/axios/lib/helpers/buildURL.js");
/* harmony import */ var _InterceptorManager_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./InterceptorManager.js */ "./node_modules/axios/lib/core/InterceptorManager.js");
/* harmony import */ var _dispatchRequest_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./dispatchRequest.js */ "./node_modules/axios/lib/core/dispatchRequest.js");
/* harmony import */ var _mergeConfig_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./mergeConfig.js */ "./node_modules/axios/lib/core/mergeConfig.js");
/* harmony import */ var _buildFullPath_js__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./buildFullPath.js */ "./node_modules/axios/lib/core/buildFullPath.js");
/* harmony import */ var _helpers_validator_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../helpers/validator.js */ "./node_modules/axios/lib/helpers/validator.js");
/* harmony import */ var _AxiosHeaders_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./AxiosHeaders.js */ "./node_modules/axios/lib/core/AxiosHeaders.js");











const validators = _helpers_validator_js__WEBPACK_IMPORTED_MODULE_0__["default"].validators;

/**
 * Create a new instance of Axios
 *
 * @param {Object} instanceConfig The default config for the instance
 *
 * @return {Axios} A new instance of Axios
 */
class Axios {
  constructor(instanceConfig) {
    this.defaults = instanceConfig;
    this.interceptors = {
      request: new _InterceptorManager_js__WEBPACK_IMPORTED_MODULE_1__["default"](),
      response: new _InterceptorManager_js__WEBPACK_IMPORTED_MODULE_1__["default"]()
    };
  }

  /**
   * Dispatch a request
   *
   * @param {String|Object} configOrUrl The config specific for this request (merged with this.defaults)
   * @param {?Object} config
   *
   * @returns {Promise} The Promise to be fulfilled
   */
  request(configOrUrl, config) {
    /*eslint no-param-reassign:0*/
    // Allow for axios('example/url'[, config]) a la fetch API
    if (typeof configOrUrl === 'string') {
      config = config || {};
      config.url = configOrUrl;
    } else {
      config = configOrUrl || {};
    }

    config = (0,_mergeConfig_js__WEBPACK_IMPORTED_MODULE_2__["default"])(this.defaults, config);

    const {transitional, paramsSerializer, headers} = config;

    if (transitional !== undefined) {
      _helpers_validator_js__WEBPACK_IMPORTED_MODULE_0__["default"].assertOptions(transitional, {
        silentJSONParsing: validators.transitional(validators.boolean),
        forcedJSONParsing: validators.transitional(validators.boolean),
        clarifyTimeoutError: validators.transitional(validators.boolean)
      }, false);
    }

    if (paramsSerializer != null) {
      if (_utils_js__WEBPACK_IMPORTED_MODULE_3__["default"].isFunction(paramsSerializer)) {
        config.paramsSerializer = {
          serialize: paramsSerializer
        }
      } else {
        _helpers_validator_js__WEBPACK_IMPORTED_MODULE_0__["default"].assertOptions(paramsSerializer, {
          encode: validators.function,
          serialize: validators.function
        }, true);
      }
    }

    // Set config.method
    config.method = (config.method || this.defaults.method || 'get').toLowerCase();

    // Flatten headers
    let contextHeaders = headers && _utils_js__WEBPACK_IMPORTED_MODULE_3__["default"].merge(
      headers.common,
      headers[config.method]
    );

    headers && _utils_js__WEBPACK_IMPORTED_MODULE_3__["default"].forEach(
      ['delete', 'get', 'head', 'post', 'put', 'patch', 'common'],
      (method) => {
        delete headers[method];
      }
    );

    config.headers = _AxiosHeaders_js__WEBPACK_IMPORTED_MODULE_4__["default"].concat(contextHeaders, headers);

    // filter out skipped interceptors
    const requestInterceptorChain = [];
    let synchronousRequestInterceptors = true;
    this.interceptors.request.forEach(function unshiftRequestInterceptors(interceptor) {
      if (typeof interceptor.runWhen === 'function' && interceptor.runWhen(config) === false) {
        return;
      }

      synchronousRequestInterceptors = synchronousRequestInterceptors && interceptor.synchronous;

      requestInterceptorChain.unshift(interceptor.fulfilled, interceptor.rejected);
    });

    const responseInterceptorChain = [];
    this.interceptors.response.forEach(function pushResponseInterceptors(interceptor) {
      responseInterceptorChain.push(interceptor.fulfilled, interceptor.rejected);
    });

    let promise;
    let i = 0;
    let len;

    if (!synchronousRequestInterceptors) {
      const chain = [_dispatchRequest_js__WEBPACK_IMPORTED_MODULE_5__["default"].bind(this), undefined];
      chain.unshift.apply(chain, requestInterceptorChain);
      chain.push.apply(chain, responseInterceptorChain);
      len = chain.length;

      promise = Promise.resolve(config);

      while (i < len) {
        promise = promise.then(chain[i++], chain[i++]);
      }

      return promise;
    }

    len = requestInterceptorChain.length;

    let newConfig = config;

    i = 0;

    while (i < len) {
      const onFulfilled = requestInterceptorChain[i++];
      const onRejected = requestInterceptorChain[i++];
      try {
        newConfig = onFulfilled(newConfig);
      } catch (error) {
        onRejected.call(this, error);
        break;
      }
    }

    try {
      promise = _dispatchRequest_js__WEBPACK_IMPORTED_MODULE_5__["default"].call(this, newConfig);
    } catch (error) {
      return Promise.reject(error);
    }

    i = 0;
    len = responseInterceptorChain.length;

    while (i < len) {
      promise = promise.then(responseInterceptorChain[i++], responseInterceptorChain[i++]);
    }

    return promise;
  }

  getUri(config) {
    config = (0,_mergeConfig_js__WEBPACK_IMPORTED_MODULE_2__["default"])(this.defaults, config);
    const fullPath = (0,_buildFullPath_js__WEBPACK_IMPORTED_MODULE_6__["default"])(config.baseURL, config.url);
    return (0,_helpers_buildURL_js__WEBPACK_IMPORTED_MODULE_7__["default"])(fullPath, config.params, config.paramsSerializer);
  }
}

// Provide aliases for supported request methods
_utils_js__WEBPACK_IMPORTED_MODULE_3__["default"].forEach(['delete', 'get', 'head', 'options'], function forEachMethodNoData(method) {
  /*eslint func-names:0*/
  Axios.prototype[method] = function(url, config) {
    return this.request((0,_mergeConfig_js__WEBPACK_IMPORTED_MODULE_2__["default"])(config || {}, {
      method,
      url,
      data: (config || {}).data
    }));
  };
});

_utils_js__WEBPACK_IMPORTED_MODULE_3__["default"].forEach(['post', 'put', 'patch'], function forEachMethodWithData(method) {
  /*eslint func-names:0*/

  function generateHTTPMethod(isForm) {
    return function httpMethod(url, data, config) {
      return this.request((0,_mergeConfig_js__WEBPACK_IMPORTED_MODULE_2__["default"])(config || {}, {
        method,
        headers: isForm ? {
          'Content-Type': 'multipart/form-data'
        } : {},
        url,
        data
      }));
    };
  }

  Axios.prototype[method] = generateHTTPMethod();

  Axios.prototype[method + 'Form'] = generateHTTPMethod(true);
});

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (Axios);


/***/ }),

/***/ "./node_modules/axios/lib/core/AxiosError.js":
/*!***************************************************!*\
  !*** ./node_modules/axios/lib/core/AxiosError.js ***!
  \***************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../utils.js */ "./node_modules/axios/lib/utils.js");




/**
 * Create an Error with the specified message, config, error code, request and response.
 *
 * @param {string} message The error message.
 * @param {string} [code] The error code (for example, 'ECONNABORTED').
 * @param {Object} [config] The config.
 * @param {Object} [request] The request.
 * @param {Object} [response] The response.
 *
 * @returns {Error} The created error.
 */
function AxiosError(message, code, config, request, response) {
  Error.call(this);

  if (Error.captureStackTrace) {
    Error.captureStackTrace(this, this.constructor);
  } else {
    this.stack = (new Error()).stack;
  }

  this.message = message;
  this.name = 'AxiosError';
  code && (this.code = code);
  config && (this.config = config);
  request && (this.request = request);
  response && (this.response = response);
}

_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].inherits(AxiosError, Error, {
  toJSON: function toJSON() {
    return {
      // Standard
      message: this.message,
      name: this.name,
      // Microsoft
      description: this.description,
      number: this.number,
      // Mozilla
      fileName: this.fileName,
      lineNumber: this.lineNumber,
      columnNumber: this.columnNumber,
      stack: this.stack,
      // Axios
      config: _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].toJSONObject(this.config),
      code: this.code,
      status: this.response && this.response.status ? this.response.status : null
    };
  }
});

const prototype = AxiosError.prototype;
const descriptors = {};

[
  'ERR_BAD_OPTION_VALUE',
  'ERR_BAD_OPTION',
  'ECONNABORTED',
  'ETIMEDOUT',
  'ERR_NETWORK',
  'ERR_FR_TOO_MANY_REDIRECTS',
  'ERR_DEPRECATED',
  'ERR_BAD_RESPONSE',
  'ERR_BAD_REQUEST',
  'ERR_CANCELED',
  'ERR_NOT_SUPPORT',
  'ERR_INVALID_URL'
// eslint-disable-next-line func-names
].forEach(code => {
  descriptors[code] = {value: code};
});

Object.defineProperties(AxiosError, descriptors);
Object.defineProperty(prototype, 'isAxiosError', {value: true});

// eslint-disable-next-line func-names
AxiosError.from = (error, code, config, request, response, customProps) => {
  const axiosError = Object.create(prototype);

  _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].toFlatObject(error, axiosError, function filter(obj) {
    return obj !== Error.prototype;
  }, prop => {
    return prop !== 'isAxiosError';
  });

  AxiosError.call(axiosError, error.message, code, config, request, response);

  axiosError.cause = error;

  axiosError.name = error.name;

  customProps && Object.assign(axiosError, customProps);

  return axiosError;
};

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (AxiosError);


/***/ }),

/***/ "./node_modules/axios/lib/core/AxiosHeaders.js":
/*!*****************************************************!*\
  !*** ./node_modules/axios/lib/core/AxiosHeaders.js ***!
  \*****************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../utils.js */ "./node_modules/axios/lib/utils.js");
/* harmony import */ var _helpers_parseHeaders_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../helpers/parseHeaders.js */ "./node_modules/axios/lib/helpers/parseHeaders.js");





const $internals = Symbol('internals');

function normalizeHeader(header) {
  return header && String(header).trim().toLowerCase();
}

function normalizeValue(value) {
  if (value === false || value == null) {
    return value;
  }

  return _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isArray(value) ? value.map(normalizeValue) : String(value);
}

function parseTokens(str) {
  const tokens = Object.create(null);
  const tokensRE = /([^\s,;=]+)\s*(?:=\s*([^,;]+))?/g;
  let match;

  while ((match = tokensRE.exec(str))) {
    tokens[match[1]] = match[2];
  }

  return tokens;
}

const isValidHeaderName = (str) => /^[-_a-zA-Z0-9^`|~,!#$%&'*+.]+$/.test(str.trim());

function matchHeaderValue(context, value, header, filter, isHeaderNameFilter) {
  if (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isFunction(filter)) {
    return filter.call(this, value, header);
  }

  if (isHeaderNameFilter) {
    value = header;
  }

  if (!_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isString(value)) return;

  if (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isString(filter)) {
    return value.indexOf(filter) !== -1;
  }

  if (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isRegExp(filter)) {
    return filter.test(value);
  }
}

function formatHeader(header) {
  return header.trim()
    .toLowerCase().replace(/([a-z\d])(\w*)/g, (w, char, str) => {
      return char.toUpperCase() + str;
    });
}

function buildAccessors(obj, header) {
  const accessorName = _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].toCamelCase(' ' + header);

  ['get', 'set', 'has'].forEach(methodName => {
    Object.defineProperty(obj, methodName + accessorName, {
      value: function(arg1, arg2, arg3) {
        return this[methodName].call(this, header, arg1, arg2, arg3);
      },
      configurable: true
    });
  });
}

class AxiosHeaders {
  constructor(headers) {
    headers && this.set(headers);
  }

  set(header, valueOrRewrite, rewrite) {
    const self = this;

    function setHeader(_value, _header, _rewrite) {
      const lHeader = normalizeHeader(_header);

      if (!lHeader) {
        throw new Error('header name must be a non-empty string');
      }

      const key = _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].findKey(self, lHeader);

      if(!key || self[key] === undefined || _rewrite === true || (_rewrite === undefined && self[key] !== false)) {
        self[key || _header] = normalizeValue(_value);
      }
    }

    const setHeaders = (headers, _rewrite) =>
      _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].forEach(headers, (_value, _header) => setHeader(_value, _header, _rewrite));

    if (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isPlainObject(header) || header instanceof this.constructor) {
      setHeaders(header, valueOrRewrite)
    } else if(_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isString(header) && (header = header.trim()) && !isValidHeaderName(header)) {
      setHeaders((0,_helpers_parseHeaders_js__WEBPACK_IMPORTED_MODULE_1__["default"])(header), valueOrRewrite);
    } else {
      header != null && setHeader(valueOrRewrite, header, rewrite);
    }

    return this;
  }

  get(header, parser) {
    header = normalizeHeader(header);

    if (header) {
      const key = _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].findKey(this, header);

      if (key) {
        const value = this[key];

        if (!parser) {
          return value;
        }

        if (parser === true) {
          return parseTokens(value);
        }

        if (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isFunction(parser)) {
          return parser.call(this, value, key);
        }

        if (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isRegExp(parser)) {
          return parser.exec(value);
        }

        throw new TypeError('parser must be boolean|regexp|function');
      }
    }
  }

  has(header, matcher) {
    header = normalizeHeader(header);

    if (header) {
      const key = _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].findKey(this, header);

      return !!(key && this[key] !== undefined && (!matcher || matchHeaderValue(this, this[key], key, matcher)));
    }

    return false;
  }

  delete(header, matcher) {
    const self = this;
    let deleted = false;

    function deleteHeader(_header) {
      _header = normalizeHeader(_header);

      if (_header) {
        const key = _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].findKey(self, _header);

        if (key && (!matcher || matchHeaderValue(self, self[key], key, matcher))) {
          delete self[key];

          deleted = true;
        }
      }
    }

    if (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isArray(header)) {
      header.forEach(deleteHeader);
    } else {
      deleteHeader(header);
    }

    return deleted;
  }

  clear(matcher) {
    const keys = Object.keys(this);
    let i = keys.length;
    let deleted = false;

    while (i--) {
      const key = keys[i];
      if(!matcher || matchHeaderValue(this, this[key], key, matcher, true)) {
        delete this[key];
        deleted = true;
      }
    }

    return deleted;
  }

  normalize(format) {
    const self = this;
    const headers = {};

    _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].forEach(this, (value, header) => {
      const key = _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].findKey(headers, header);

      if (key) {
        self[key] = normalizeValue(value);
        delete self[header];
        return;
      }

      const normalized = format ? formatHeader(header) : String(header).trim();

      if (normalized !== header) {
        delete self[header];
      }

      self[normalized] = normalizeValue(value);

      headers[normalized] = true;
    });

    return this;
  }

  concat(...targets) {
    return this.constructor.concat(this, ...targets);
  }

  toJSON(asStrings) {
    const obj = Object.create(null);

    _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].forEach(this, (value, header) => {
      value != null && value !== false && (obj[header] = asStrings && _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isArray(value) ? value.join(', ') : value);
    });

    return obj;
  }

  [Symbol.iterator]() {
    return Object.entries(this.toJSON())[Symbol.iterator]();
  }

  toString() {
    return Object.entries(this.toJSON()).map(([header, value]) => header + ': ' + value).join('\n');
  }

  get [Symbol.toStringTag]() {
    return 'AxiosHeaders';
  }

  static from(thing) {
    return thing instanceof this ? thing : new this(thing);
  }

  static concat(first, ...targets) {
    const computed = new this(first);

    targets.forEach((target) => computed.set(target));

    return computed;
  }

  static accessor(header) {
    const internals = this[$internals] = (this[$internals] = {
      accessors: {}
    });

    const accessors = internals.accessors;
    const prototype = this.prototype;

    function defineAccessor(_header) {
      const lHeader = normalizeHeader(_header);

      if (!accessors[lHeader]) {
        buildAccessors(prototype, _header);
        accessors[lHeader] = true;
      }
    }

    _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isArray(header) ? header.forEach(defineAccessor) : defineAccessor(header);

    return this;
  }
}

AxiosHeaders.accessor(['Content-Type', 'Content-Length', 'Accept', 'Accept-Encoding', 'User-Agent', 'Authorization']);

// reserved names hotfix
_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].reduceDescriptors(AxiosHeaders.prototype, ({value}, key) => {
  let mapped = key[0].toUpperCase() + key.slice(1); // map `set` => `Set`
  return {
    get: () => value,
    set(headerValue) {
      this[mapped] = headerValue;
    }
  }
});

_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].freezeMethods(AxiosHeaders);

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (AxiosHeaders);


/***/ }),

/***/ "./node_modules/axios/lib/core/InterceptorManager.js":
/*!***********************************************************!*\
  !*** ./node_modules/axios/lib/core/InterceptorManager.js ***!
  \***********************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./../utils.js */ "./node_modules/axios/lib/utils.js");




class InterceptorManager {
  constructor() {
    this.handlers = [];
  }

  /**
   * Add a new interceptor to the stack
   *
   * @param {Function} fulfilled The function to handle `then` for a `Promise`
   * @param {Function} rejected The function to handle `reject` for a `Promise`
   *
   * @return {Number} An ID used to remove interceptor later
   */
  use(fulfilled, rejected, options) {
    this.handlers.push({
      fulfilled,
      rejected,
      synchronous: options ? options.synchronous : false,
      runWhen: options ? options.runWhen : null
    });
    return this.handlers.length - 1;
  }

  /**
   * Remove an interceptor from the stack
   *
   * @param {Number} id The ID that was returned by `use`
   *
   * @returns {Boolean} `true` if the interceptor was removed, `false` otherwise
   */
  eject(id) {
    if (this.handlers[id]) {
      this.handlers[id] = null;
    }
  }

  /**
   * Clear all interceptors from the stack
   *
   * @returns {void}
   */
  clear() {
    if (this.handlers) {
      this.handlers = [];
    }
  }

  /**
   * Iterate over all the registered interceptors
   *
   * This method is particularly useful for skipping over any
   * interceptors that may have become `null` calling `eject`.
   *
   * @param {Function} fn The function to call for each interceptor
   *
   * @returns {void}
   */
  forEach(fn) {
    _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].forEach(this.handlers, function forEachHandler(h) {
      if (h !== null) {
        fn(h);
      }
    });
  }
}

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (InterceptorManager);


/***/ }),

/***/ "./node_modules/axios/lib/core/buildFullPath.js":
/*!******************************************************!*\
  !*** ./node_modules/axios/lib/core/buildFullPath.js ***!
  \******************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ buildFullPath)
/* harmony export */ });
/* harmony import */ var _helpers_isAbsoluteURL_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../helpers/isAbsoluteURL.js */ "./node_modules/axios/lib/helpers/isAbsoluteURL.js");
/* harmony import */ var _helpers_combineURLs_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../helpers/combineURLs.js */ "./node_modules/axios/lib/helpers/combineURLs.js");





/**
 * Creates a new URL by combining the baseURL with the requestedURL,
 * only when the requestedURL is not already an absolute URL.
 * If the requestURL is absolute, this function returns the requestedURL untouched.
 *
 * @param {string} baseURL The base URL
 * @param {string} requestedURL Absolute or relative URL to combine
 *
 * @returns {string} The combined full path
 */
function buildFullPath(baseURL, requestedURL) {
  if (baseURL && !(0,_helpers_isAbsoluteURL_js__WEBPACK_IMPORTED_MODULE_0__["default"])(requestedURL)) {
    return (0,_helpers_combineURLs_js__WEBPACK_IMPORTED_MODULE_1__["default"])(baseURL, requestedURL);
  }
  return requestedURL;
}


/***/ }),

/***/ "./node_modules/axios/lib/core/dispatchRequest.js":
/*!********************************************************!*\
  !*** ./node_modules/axios/lib/core/dispatchRequest.js ***!
  \********************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ dispatchRequest)
/* harmony export */ });
/* harmony import */ var _transformData_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./transformData.js */ "./node_modules/axios/lib/core/transformData.js");
/* harmony import */ var _cancel_isCancel_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../cancel/isCancel.js */ "./node_modules/axios/lib/cancel/isCancel.js");
/* harmony import */ var _defaults_index_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../defaults/index.js */ "./node_modules/axios/lib/defaults/index.js");
/* harmony import */ var _cancel_CanceledError_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../cancel/CanceledError.js */ "./node_modules/axios/lib/cancel/CanceledError.js");
/* harmony import */ var _core_AxiosHeaders_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../core/AxiosHeaders.js */ "./node_modules/axios/lib/core/AxiosHeaders.js");
/* harmony import */ var _adapters_adapters_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../adapters/adapters.js */ "./node_modules/axios/lib/adapters/adapters.js");









/**
 * Throws a `CanceledError` if cancellation has been requested.
 *
 * @param {Object} config The config that is to be used for the request
 *
 * @returns {void}
 */
function throwIfCancellationRequested(config) {
  if (config.cancelToken) {
    config.cancelToken.throwIfRequested();
  }

  if (config.signal && config.signal.aborted) {
    throw new _cancel_CanceledError_js__WEBPACK_IMPORTED_MODULE_0__["default"](null, config);
  }
}

/**
 * Dispatch a request to the server using the configured adapter.
 *
 * @param {object} config The config that is to be used for the request
 *
 * @returns {Promise} The Promise to be fulfilled
 */
function dispatchRequest(config) {
  throwIfCancellationRequested(config);

  config.headers = _core_AxiosHeaders_js__WEBPACK_IMPORTED_MODULE_1__["default"].from(config.headers);

  // Transform request data
  config.data = _transformData_js__WEBPACK_IMPORTED_MODULE_2__["default"].call(
    config,
    config.transformRequest
  );

  if (['post', 'put', 'patch'].indexOf(config.method) !== -1) {
    config.headers.setContentType('application/x-www-form-urlencoded', false);
  }

  const adapter = _adapters_adapters_js__WEBPACK_IMPORTED_MODULE_3__["default"].getAdapter(config.adapter || _defaults_index_js__WEBPACK_IMPORTED_MODULE_4__["default"].adapter);

  return adapter(config).then(function onAdapterResolution(response) {
    throwIfCancellationRequested(config);

    // Transform response data
    response.data = _transformData_js__WEBPACK_IMPORTED_MODULE_2__["default"].call(
      config,
      config.transformResponse,
      response
    );

    response.headers = _core_AxiosHeaders_js__WEBPACK_IMPORTED_MODULE_1__["default"].from(response.headers);

    return response;
  }, function onAdapterRejection(reason) {
    if (!(0,_cancel_isCancel_js__WEBPACK_IMPORTED_MODULE_5__["default"])(reason)) {
      throwIfCancellationRequested(config);

      // Transform response data
      if (reason && reason.response) {
        reason.response.data = _transformData_js__WEBPACK_IMPORTED_MODULE_2__["default"].call(
          config,
          config.transformResponse,
          reason.response
        );
        reason.response.headers = _core_AxiosHeaders_js__WEBPACK_IMPORTED_MODULE_1__["default"].from(reason.response.headers);
      }
    }

    return Promise.reject(reason);
  });
}


/***/ }),

/***/ "./node_modules/axios/lib/core/mergeConfig.js":
/*!****************************************************!*\
  !*** ./node_modules/axios/lib/core/mergeConfig.js ***!
  \****************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ mergeConfig)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../utils.js */ "./node_modules/axios/lib/utils.js");
/* harmony import */ var _AxiosHeaders_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./AxiosHeaders.js */ "./node_modules/axios/lib/core/AxiosHeaders.js");





const headersToObject = (thing) => thing instanceof _AxiosHeaders_js__WEBPACK_IMPORTED_MODULE_0__["default"] ? thing.toJSON() : thing;

/**
 * Config-specific merge-function which creates a new config-object
 * by merging two configuration objects together.
 *
 * @param {Object} config1
 * @param {Object} config2
 *
 * @returns {Object} New object resulting from merging config2 to config1
 */
function mergeConfig(config1, config2) {
  // eslint-disable-next-line no-param-reassign
  config2 = config2 || {};
  const config = {};

  function getMergedValue(target, source, caseless) {
    if (_utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].isPlainObject(target) && _utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].isPlainObject(source)) {
      return _utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].merge.call({caseless}, target, source);
    } else if (_utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].isPlainObject(source)) {
      return _utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].merge({}, source);
    } else if (_utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].isArray(source)) {
      return source.slice();
    }
    return source;
  }

  // eslint-disable-next-line consistent-return
  function mergeDeepProperties(a, b, caseless) {
    if (!_utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].isUndefined(b)) {
      return getMergedValue(a, b, caseless);
    } else if (!_utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].isUndefined(a)) {
      return getMergedValue(undefined, a, caseless);
    }
  }

  // eslint-disable-next-line consistent-return
  function valueFromConfig2(a, b) {
    if (!_utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].isUndefined(b)) {
      return getMergedValue(undefined, b);
    }
  }

  // eslint-disable-next-line consistent-return
  function defaultToConfig2(a, b) {
    if (!_utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].isUndefined(b)) {
      return getMergedValue(undefined, b);
    } else if (!_utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].isUndefined(a)) {
      return getMergedValue(undefined, a);
    }
  }

  // eslint-disable-next-line consistent-return
  function mergeDirectKeys(a, b, prop) {
    if (prop in config2) {
      return getMergedValue(a, b);
    } else if (prop in config1) {
      return getMergedValue(undefined, a);
    }
  }

  const mergeMap = {
    url: valueFromConfig2,
    method: valueFromConfig2,
    data: valueFromConfig2,
    baseURL: defaultToConfig2,
    transformRequest: defaultToConfig2,
    transformResponse: defaultToConfig2,
    paramsSerializer: defaultToConfig2,
    timeout: defaultToConfig2,
    timeoutMessage: defaultToConfig2,
    withCredentials: defaultToConfig2,
    withXSRFToken: defaultToConfig2,
    adapter: defaultToConfig2,
    responseType: defaultToConfig2,
    xsrfCookieName: defaultToConfig2,
    xsrfHeaderName: defaultToConfig2,
    onUploadProgress: defaultToConfig2,
    onDownloadProgress: defaultToConfig2,
    decompress: defaultToConfig2,
    maxContentLength: defaultToConfig2,
    maxBodyLength: defaultToConfig2,
    beforeRedirect: defaultToConfig2,
    transport: defaultToConfig2,
    httpAgent: defaultToConfig2,
    httpsAgent: defaultToConfig2,
    cancelToken: defaultToConfig2,
    socketPath: defaultToConfig2,
    responseEncoding: defaultToConfig2,
    validateStatus: mergeDirectKeys,
    headers: (a, b) => mergeDeepProperties(headersToObject(a), headersToObject(b), true)
  };

  _utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].forEach(Object.keys(Object.assign({}, config1, config2)), function computeConfigValue(prop) {
    const merge = mergeMap[prop] || mergeDeepProperties;
    const configValue = merge(config1[prop], config2[prop], prop);
    (_utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].isUndefined(configValue) && merge !== mergeDirectKeys) || (config[prop] = configValue);
  });

  return config;
}


/***/ }),

/***/ "./node_modules/axios/lib/core/settle.js":
/*!***********************************************!*\
  !*** ./node_modules/axios/lib/core/settle.js ***!
  \***********************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ settle)
/* harmony export */ });
/* harmony import */ var _AxiosError_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./AxiosError.js */ "./node_modules/axios/lib/core/AxiosError.js");




/**
 * Resolve or reject a Promise based on response status.
 *
 * @param {Function} resolve A function that resolves the promise.
 * @param {Function} reject A function that rejects the promise.
 * @param {object} response The response.
 *
 * @returns {object} The response.
 */
function settle(resolve, reject, response) {
  const validateStatus = response.config.validateStatus;
  if (!response.status || !validateStatus || validateStatus(response.status)) {
    resolve(response);
  } else {
    reject(new _AxiosError_js__WEBPACK_IMPORTED_MODULE_0__["default"](
      'Request failed with status code ' + response.status,
      [_AxiosError_js__WEBPACK_IMPORTED_MODULE_0__["default"].ERR_BAD_REQUEST, _AxiosError_js__WEBPACK_IMPORTED_MODULE_0__["default"].ERR_BAD_RESPONSE][Math.floor(response.status / 100) - 4],
      response.config,
      response.request,
      response
    ));
  }
}


/***/ }),

/***/ "./node_modules/axios/lib/core/transformData.js":
/*!******************************************************!*\
  !*** ./node_modules/axios/lib/core/transformData.js ***!
  \******************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ transformData)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./../utils.js */ "./node_modules/axios/lib/utils.js");
/* harmony import */ var _defaults_index_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../defaults/index.js */ "./node_modules/axios/lib/defaults/index.js");
/* harmony import */ var _core_AxiosHeaders_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../core/AxiosHeaders.js */ "./node_modules/axios/lib/core/AxiosHeaders.js");






/**
 * Transform the data for a request or a response
 *
 * @param {Array|Function} fns A single function or Array of functions
 * @param {?Object} response The response object
 *
 * @returns {*} The resulting transformed data
 */
function transformData(fns, response) {
  const config = this || _defaults_index_js__WEBPACK_IMPORTED_MODULE_0__["default"];
  const context = response || config;
  const headers = _core_AxiosHeaders_js__WEBPACK_IMPORTED_MODULE_1__["default"].from(context.headers);
  let data = context.data;

  _utils_js__WEBPACK_IMPORTED_MODULE_2__["default"].forEach(fns, function transform(fn) {
    data = fn.call(config, data, headers.normalize(), response ? response.status : undefined);
  });

  headers.normalize();

  return data;
}


/***/ }),

/***/ "./node_modules/axios/lib/defaults/index.js":
/*!**************************************************!*\
  !*** ./node_modules/axios/lib/defaults/index.js ***!
  \**************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../utils.js */ "./node_modules/axios/lib/utils.js");
/* harmony import */ var _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../core/AxiosError.js */ "./node_modules/axios/lib/core/AxiosError.js");
/* harmony import */ var _transitional_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./transitional.js */ "./node_modules/axios/lib/defaults/transitional.js");
/* harmony import */ var _helpers_toFormData_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../helpers/toFormData.js */ "./node_modules/axios/lib/helpers/toFormData.js");
/* harmony import */ var _helpers_toURLEncodedForm_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../helpers/toURLEncodedForm.js */ "./node_modules/axios/lib/helpers/toURLEncodedForm.js");
/* harmony import */ var _platform_index_js__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../platform/index.js */ "./node_modules/axios/lib/platform/index.js");
/* harmony import */ var _helpers_formDataToJSON_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../helpers/formDataToJSON.js */ "./node_modules/axios/lib/helpers/formDataToJSON.js");










/**
 * It takes a string, tries to parse it, and if it fails, it returns the stringified version
 * of the input
 *
 * @param {any} rawValue - The value to be stringified.
 * @param {Function} parser - A function that parses a string into a JavaScript object.
 * @param {Function} encoder - A function that takes a value and returns a string.
 *
 * @returns {string} A stringified version of the rawValue.
 */
function stringifySafely(rawValue, parser, encoder) {
  if (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isString(rawValue)) {
    try {
      (parser || JSON.parse)(rawValue);
      return _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].trim(rawValue);
    } catch (e) {
      if (e.name !== 'SyntaxError') {
        throw e;
      }
    }
  }

  return (encoder || JSON.stringify)(rawValue);
}

const defaults = {

  transitional: _transitional_js__WEBPACK_IMPORTED_MODULE_1__["default"],

  adapter: ['xhr', 'http'],

  transformRequest: [function transformRequest(data, headers) {
    const contentType = headers.getContentType() || '';
    const hasJSONContentType = contentType.indexOf('application/json') > -1;
    const isObjectPayload = _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isObject(data);

    if (isObjectPayload && _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isHTMLForm(data)) {
      data = new FormData(data);
    }

    const isFormData = _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isFormData(data);

    if (isFormData) {
      if (!hasJSONContentType) {
        return data;
      }
      return hasJSONContentType ? JSON.stringify((0,_helpers_formDataToJSON_js__WEBPACK_IMPORTED_MODULE_2__["default"])(data)) : data;
    }

    if (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isArrayBuffer(data) ||
      _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isBuffer(data) ||
      _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isStream(data) ||
      _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isFile(data) ||
      _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isBlob(data)
    ) {
      return data;
    }
    if (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isArrayBufferView(data)) {
      return data.buffer;
    }
    if (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isURLSearchParams(data)) {
      headers.setContentType('application/x-www-form-urlencoded;charset=utf-8', false);
      return data.toString();
    }

    let isFileList;

    if (isObjectPayload) {
      if (contentType.indexOf('application/x-www-form-urlencoded') > -1) {
        return (0,_helpers_toURLEncodedForm_js__WEBPACK_IMPORTED_MODULE_3__["default"])(data, this.formSerializer).toString();
      }

      if ((isFileList = _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isFileList(data)) || contentType.indexOf('multipart/form-data') > -1) {
        const _FormData = this.env && this.env.FormData;

        return (0,_helpers_toFormData_js__WEBPACK_IMPORTED_MODULE_4__["default"])(
          isFileList ? {'files[]': data} : data,
          _FormData && new _FormData(),
          this.formSerializer
        );
      }
    }

    if (isObjectPayload || hasJSONContentType ) {
      headers.setContentType('application/json', false);
      return stringifySafely(data);
    }

    return data;
  }],

  transformResponse: [function transformResponse(data) {
    const transitional = this.transitional || defaults.transitional;
    const forcedJSONParsing = transitional && transitional.forcedJSONParsing;
    const JSONRequested = this.responseType === 'json';

    if (data && _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isString(data) && ((forcedJSONParsing && !this.responseType) || JSONRequested)) {
      const silentJSONParsing = transitional && transitional.silentJSONParsing;
      const strictJSONParsing = !silentJSONParsing && JSONRequested;

      try {
        return JSON.parse(data);
      } catch (e) {
        if (strictJSONParsing) {
          if (e.name === 'SyntaxError') {
            throw _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_5__["default"].from(e, _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_5__["default"].ERR_BAD_RESPONSE, this, null, this.response);
          }
          throw e;
        }
      }
    }

    return data;
  }],

  /**
   * A timeout in milliseconds to abort a request. If set to 0 (default) a
   * timeout is not created.
   */
  timeout: 0,

  xsrfCookieName: 'XSRF-TOKEN',
  xsrfHeaderName: 'X-XSRF-TOKEN',

  maxContentLength: -1,
  maxBodyLength: -1,

  env: {
    FormData: _platform_index_js__WEBPACK_IMPORTED_MODULE_6__["default"].classes.FormData,
    Blob: _platform_index_js__WEBPACK_IMPORTED_MODULE_6__["default"].classes.Blob
  },

  validateStatus: function validateStatus(status) {
    return status >= 200 && status < 300;
  },

  headers: {
    common: {
      'Accept': 'application/json, text/plain, */*',
      'Content-Type': undefined
    }
  }
};

_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].forEach(['delete', 'get', 'head', 'post', 'put', 'patch'], (method) => {
  defaults.headers[method] = {};
});

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (defaults);


/***/ }),

/***/ "./node_modules/axios/lib/defaults/transitional.js":
/*!*********************************************************!*\
  !*** ./node_modules/axios/lib/defaults/transitional.js ***!
  \*********************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });


/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ({
  silentJSONParsing: true,
  forcedJSONParsing: true,
  clarifyTimeoutError: false
});


/***/ }),

/***/ "./node_modules/axios/lib/env/data.js":
/*!********************************************!*\
  !*** ./node_modules/axios/lib/env/data.js ***!
  \********************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   VERSION: () => (/* binding */ VERSION)
/* harmony export */ });
const VERSION = "1.6.2";

/***/ }),

/***/ "./node_modules/axios/lib/helpers/AxiosURLSearchParams.js":
/*!****************************************************************!*\
  !*** ./node_modules/axios/lib/helpers/AxiosURLSearchParams.js ***!
  \****************************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _toFormData_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./toFormData.js */ "./node_modules/axios/lib/helpers/toFormData.js");




/**
 * It encodes a string by replacing all characters that are not in the unreserved set with
 * their percent-encoded equivalents
 *
 * @param {string} str - The string to encode.
 *
 * @returns {string} The encoded string.
 */
function encode(str) {
  const charMap = {
    '!': '%21',
    "'": '%27',
    '(': '%28',
    ')': '%29',
    '~': '%7E',
    '%20': '+',
    '%00': '\x00'
  };
  return encodeURIComponent(str).replace(/[!'()~]|%20|%00/g, function replacer(match) {
    return charMap[match];
  });
}

/**
 * It takes a params object and converts it to a FormData object
 *
 * @param {Object<string, any>} params - The parameters to be converted to a FormData object.
 * @param {Object<string, any>} options - The options object passed to the Axios constructor.
 *
 * @returns {void}
 */
function AxiosURLSearchParams(params, options) {
  this._pairs = [];

  params && (0,_toFormData_js__WEBPACK_IMPORTED_MODULE_0__["default"])(params, this, options);
}

const prototype = AxiosURLSearchParams.prototype;

prototype.append = function append(name, value) {
  this._pairs.push([name, value]);
};

prototype.toString = function toString(encoder) {
  const _encode = encoder ? function(value) {
    return encoder.call(this, value, encode);
  } : encode;

  return this._pairs.map(function each(pair) {
    return _encode(pair[0]) + '=' + _encode(pair[1]);
  }, '').join('&');
};

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (AxiosURLSearchParams);


/***/ }),

/***/ "./node_modules/axios/lib/helpers/HttpStatusCode.js":
/*!**********************************************************!*\
  !*** ./node_modules/axios/lib/helpers/HttpStatusCode.js ***!
  \**********************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
const HttpStatusCode = {
  Continue: 100,
  SwitchingProtocols: 101,
  Processing: 102,
  EarlyHints: 103,
  Ok: 200,
  Created: 201,
  Accepted: 202,
  NonAuthoritativeInformation: 203,
  NoContent: 204,
  ResetContent: 205,
  PartialContent: 206,
  MultiStatus: 207,
  AlreadyReported: 208,
  ImUsed: 226,
  MultipleChoices: 300,
  MovedPermanently: 301,
  Found: 302,
  SeeOther: 303,
  NotModified: 304,
  UseProxy: 305,
  Unused: 306,
  TemporaryRedirect: 307,
  PermanentRedirect: 308,
  BadRequest: 400,
  Unauthorized: 401,
  PaymentRequired: 402,
  Forbidden: 403,
  NotFound: 404,
  MethodNotAllowed: 405,
  NotAcceptable: 406,
  ProxyAuthenticationRequired: 407,
  RequestTimeout: 408,
  Conflict: 409,
  Gone: 410,
  LengthRequired: 411,
  PreconditionFailed: 412,
  PayloadTooLarge: 413,
  UriTooLong: 414,
  UnsupportedMediaType: 415,
  RangeNotSatisfiable: 416,
  ExpectationFailed: 417,
  ImATeapot: 418,
  MisdirectedRequest: 421,
  UnprocessableEntity: 422,
  Locked: 423,
  FailedDependency: 424,
  TooEarly: 425,
  UpgradeRequired: 426,
  PreconditionRequired: 428,
  TooManyRequests: 429,
  RequestHeaderFieldsTooLarge: 431,
  UnavailableForLegalReasons: 451,
  InternalServerError: 500,
  NotImplemented: 501,
  BadGateway: 502,
  ServiceUnavailable: 503,
  GatewayTimeout: 504,
  HttpVersionNotSupported: 505,
  VariantAlsoNegotiates: 506,
  InsufficientStorage: 507,
  LoopDetected: 508,
  NotExtended: 510,
  NetworkAuthenticationRequired: 511,
};

Object.entries(HttpStatusCode).forEach(([key, value]) => {
  HttpStatusCode[value] = key;
});

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (HttpStatusCode);


/***/ }),

/***/ "./node_modules/axios/lib/helpers/bind.js":
/*!************************************************!*\
  !*** ./node_modules/axios/lib/helpers/bind.js ***!
  \************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ bind)
/* harmony export */ });


function bind(fn, thisArg) {
  return function wrap() {
    return fn.apply(thisArg, arguments);
  };
}


/***/ }),

/***/ "./node_modules/axios/lib/helpers/buildURL.js":
/*!****************************************************!*\
  !*** ./node_modules/axios/lib/helpers/buildURL.js ***!
  \****************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ buildURL)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../utils.js */ "./node_modules/axios/lib/utils.js");
/* harmony import */ var _helpers_AxiosURLSearchParams_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../helpers/AxiosURLSearchParams.js */ "./node_modules/axios/lib/helpers/AxiosURLSearchParams.js");





/**
 * It replaces all instances of the characters `:`, `$`, `,`, `+`, `[`, and `]` with their
 * URI encoded counterparts
 *
 * @param {string} val The value to be encoded.
 *
 * @returns {string} The encoded value.
 */
function encode(val) {
  return encodeURIComponent(val).
    replace(/%3A/gi, ':').
    replace(/%24/g, '$').
    replace(/%2C/gi, ',').
    replace(/%20/g, '+').
    replace(/%5B/gi, '[').
    replace(/%5D/gi, ']');
}

/**
 * Build a URL by appending params to the end
 *
 * @param {string} url The base of the url (e.g., http://www.google.com)
 * @param {object} [params] The params to be appended
 * @param {?object} options
 *
 * @returns {string} The formatted url
 */
function buildURL(url, params, options) {
  /*eslint no-param-reassign:0*/
  if (!params) {
    return url;
  }
  
  const _encode = options && options.encode || encode;

  const serializeFn = options && options.serialize;

  let serializedParams;

  if (serializeFn) {
    serializedParams = serializeFn(params, options);
  } else {
    serializedParams = _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isURLSearchParams(params) ?
      params.toString() :
      new _helpers_AxiosURLSearchParams_js__WEBPACK_IMPORTED_MODULE_1__["default"](params, options).toString(_encode);
  }

  if (serializedParams) {
    const hashmarkIndex = url.indexOf("#");

    if (hashmarkIndex !== -1) {
      url = url.slice(0, hashmarkIndex);
    }
    url += (url.indexOf('?') === -1 ? '?' : '&') + serializedParams;
  }

  return url;
}


/***/ }),

/***/ "./node_modules/axios/lib/helpers/combineURLs.js":
/*!*******************************************************!*\
  !*** ./node_modules/axios/lib/helpers/combineURLs.js ***!
  \*******************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ combineURLs)
/* harmony export */ });


/**
 * Creates a new URL by combining the specified URLs
 *
 * @param {string} baseURL The base URL
 * @param {string} relativeURL The relative URL
 *
 * @returns {string} The combined URL
 */
function combineURLs(baseURL, relativeURL) {
  return relativeURL
    ? baseURL.replace(/\/+$/, '') + '/' + relativeURL.replace(/^\/+/, '')
    : baseURL;
}


/***/ }),

/***/ "./node_modules/axios/lib/helpers/cookies.js":
/*!***************************************************!*\
  !*** ./node_modules/axios/lib/helpers/cookies.js ***!
  \***************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./../utils.js */ "./node_modules/axios/lib/utils.js");
/* harmony import */ var _platform_index_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../platform/index.js */ "./node_modules/axios/lib/platform/index.js");



/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (_platform_index_js__WEBPACK_IMPORTED_MODULE_0__["default"].hasStandardBrowserEnv ?

  // Standard browser envs support document.cookie
  {
    write(name, value, expires, path, domain, secure) {
      const cookie = [name + '=' + encodeURIComponent(value)];

      _utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].isNumber(expires) && cookie.push('expires=' + new Date(expires).toGMTString());

      _utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].isString(path) && cookie.push('path=' + path);

      _utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].isString(domain) && cookie.push('domain=' + domain);

      secure === true && cookie.push('secure');

      document.cookie = cookie.join('; ');
    },

    read(name) {
      const match = document.cookie.match(new RegExp('(^|;\\s*)(' + name + ')=([^;]*)'));
      return (match ? decodeURIComponent(match[3]) : null);
    },

    remove(name) {
      this.write(name, '', Date.now() - 86400000);
    }
  }

  :

  // Non-standard browser env (web workers, react-native) lack needed support.
  {
    write() {},
    read() {
      return null;
    },
    remove() {}
  });



/***/ }),

/***/ "./node_modules/axios/lib/helpers/formDataToJSON.js":
/*!**********************************************************!*\
  !*** ./node_modules/axios/lib/helpers/formDataToJSON.js ***!
  \**********************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../utils.js */ "./node_modules/axios/lib/utils.js");




/**
 * It takes a string like `foo[x][y][z]` and returns an array like `['foo', 'x', 'y', 'z']
 *
 * @param {string} name - The name of the property to get.
 *
 * @returns An array of strings.
 */
function parsePropPath(name) {
  // foo[x][y][z]
  // foo.x.y.z
  // foo-x-y-z
  // foo x y z
  return _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].matchAll(/\w+|\[(\w*)]/g, name).map(match => {
    return match[0] === '[]' ? '' : match[1] || match[0];
  });
}

/**
 * Convert an array to an object.
 *
 * @param {Array<any>} arr - The array to convert to an object.
 *
 * @returns An object with the same keys and values as the array.
 */
function arrayToObject(arr) {
  const obj = {};
  const keys = Object.keys(arr);
  let i;
  const len = keys.length;
  let key;
  for (i = 0; i < len; i++) {
    key = keys[i];
    obj[key] = arr[key];
  }
  return obj;
}

/**
 * It takes a FormData object and returns a JavaScript object
 *
 * @param {string} formData The FormData object to convert to JSON.
 *
 * @returns {Object<string, any> | null} The converted object.
 */
function formDataToJSON(formData) {
  function buildPath(path, value, target, index) {
    let name = path[index++];
    const isNumericKey = Number.isFinite(+name);
    const isLast = index >= path.length;
    name = !name && _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isArray(target) ? target.length : name;

    if (isLast) {
      if (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].hasOwnProp(target, name)) {
        target[name] = [target[name], value];
      } else {
        target[name] = value;
      }

      return !isNumericKey;
    }

    if (!target[name] || !_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isObject(target[name])) {
      target[name] = [];
    }

    const result = buildPath(path, value, target[name], index);

    if (result && _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isArray(target[name])) {
      target[name] = arrayToObject(target[name]);
    }

    return !isNumericKey;
  }

  if (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isFormData(formData) && _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isFunction(formData.entries)) {
    const obj = {};

    _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].forEachEntry(formData, (name, value) => {
      buildPath(parsePropPath(name), value, obj, 0);
    });

    return obj;
  }

  return null;
}

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (formDataToJSON);


/***/ }),

/***/ "./node_modules/axios/lib/helpers/isAbsoluteURL.js":
/*!*********************************************************!*\
  !*** ./node_modules/axios/lib/helpers/isAbsoluteURL.js ***!
  \*********************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ isAbsoluteURL)
/* harmony export */ });


/**
 * Determines whether the specified URL is absolute
 *
 * @param {string} url The URL to test
 *
 * @returns {boolean} True if the specified URL is absolute, otherwise false
 */
function isAbsoluteURL(url) {
  // A URL is considered absolute if it begins with "<scheme>://" or "//" (protocol-relative URL).
  // RFC 3986 defines scheme name as a sequence of characters beginning with a letter and followed
  // by any combination of letters, digits, plus, period, or hyphen.
  return /^([a-z][a-z\d+\-.]*:)?\/\//i.test(url);
}


/***/ }),

/***/ "./node_modules/axios/lib/helpers/isAxiosError.js":
/*!********************************************************!*\
  !*** ./node_modules/axios/lib/helpers/isAxiosError.js ***!
  \********************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ isAxiosError)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./../utils.js */ "./node_modules/axios/lib/utils.js");




/**
 * Determines whether the payload is an error thrown by Axios
 *
 * @param {*} payload The value to test
 *
 * @returns {boolean} True if the payload is an error thrown by Axios, otherwise false
 */
function isAxiosError(payload) {
  return _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isObject(payload) && (payload.isAxiosError === true);
}


/***/ }),

/***/ "./node_modules/axios/lib/helpers/isURLSameOrigin.js":
/*!***********************************************************!*\
  !*** ./node_modules/axios/lib/helpers/isURLSameOrigin.js ***!
  \***********************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./../utils.js */ "./node_modules/axios/lib/utils.js");
/* harmony import */ var _platform_index_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../platform/index.js */ "./node_modules/axios/lib/platform/index.js");





/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (_platform_index_js__WEBPACK_IMPORTED_MODULE_0__["default"].hasStandardBrowserEnv ?

// Standard browser envs have full support of the APIs needed to test
// whether the request URL is of the same origin as current location.
  (function standardBrowserEnv() {
    const msie = /(msie|trident)/i.test(navigator.userAgent);
    const urlParsingNode = document.createElement('a');
    let originURL;

    /**
    * Parse a URL to discover its components
    *
    * @param {String} url The URL to be parsed
    * @returns {Object}
    */
    function resolveURL(url) {
      let href = url;

      if (msie) {
        // IE needs attribute set twice to normalize properties
        urlParsingNode.setAttribute('href', href);
        href = urlParsingNode.href;
      }

      urlParsingNode.setAttribute('href', href);

      // urlParsingNode provides the UrlUtils interface - http://url.spec.whatwg.org/#urlutils
      return {
        href: urlParsingNode.href,
        protocol: urlParsingNode.protocol ? urlParsingNode.protocol.replace(/:$/, '') : '',
        host: urlParsingNode.host,
        search: urlParsingNode.search ? urlParsingNode.search.replace(/^\?/, '') : '',
        hash: urlParsingNode.hash ? urlParsingNode.hash.replace(/^#/, '') : '',
        hostname: urlParsingNode.hostname,
        port: urlParsingNode.port,
        pathname: (urlParsingNode.pathname.charAt(0) === '/') ?
          urlParsingNode.pathname :
          '/' + urlParsingNode.pathname
      };
    }

    originURL = resolveURL(window.location.href);

    /**
    * Determine if a URL shares the same origin as the current location
    *
    * @param {String} requestURL The URL to test
    * @returns {boolean} True if URL shares the same origin, otherwise false
    */
    return function isURLSameOrigin(requestURL) {
      const parsed = (_utils_js__WEBPACK_IMPORTED_MODULE_1__["default"].isString(requestURL)) ? resolveURL(requestURL) : requestURL;
      return (parsed.protocol === originURL.protocol &&
          parsed.host === originURL.host);
    };
  })() :

  // Non standard browser envs (web workers, react-native) lack needed support.
  (function nonStandardBrowserEnv() {
    return function isURLSameOrigin() {
      return true;
    };
  })());


/***/ }),

/***/ "./node_modules/axios/lib/helpers/null.js":
/*!************************************************!*\
  !*** ./node_modules/axios/lib/helpers/null.js ***!
  \************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
// eslint-disable-next-line strict
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (null);


/***/ }),

/***/ "./node_modules/axios/lib/helpers/parseHeaders.js":
/*!********************************************************!*\
  !*** ./node_modules/axios/lib/helpers/parseHeaders.js ***!
  \********************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./../utils.js */ "./node_modules/axios/lib/utils.js");




// RawAxiosHeaders whose duplicates are ignored by node
// c.f. https://nodejs.org/api/http.html#http_message_headers
const ignoreDuplicateOf = _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].toObjectSet([
  'age', 'authorization', 'content-length', 'content-type', 'etag',
  'expires', 'from', 'host', 'if-modified-since', 'if-unmodified-since',
  'last-modified', 'location', 'max-forwards', 'proxy-authorization',
  'referer', 'retry-after', 'user-agent'
]);

/**
 * Parse headers into an object
 *
 * ```
 * Date: Wed, 27 Aug 2014 08:58:49 GMT
 * Content-Type: application/json
 * Connection: keep-alive
 * Transfer-Encoding: chunked
 * ```
 *
 * @param {String} rawHeaders Headers needing to be parsed
 *
 * @returns {Object} Headers parsed into an object
 */
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (rawHeaders => {
  const parsed = {};
  let key;
  let val;
  let i;

  rawHeaders && rawHeaders.split('\n').forEach(function parser(line) {
    i = line.indexOf(':');
    key = line.substring(0, i).trim().toLowerCase();
    val = line.substring(i + 1).trim();

    if (!key || (parsed[key] && ignoreDuplicateOf[key])) {
      return;
    }

    if (key === 'set-cookie') {
      if (parsed[key]) {
        parsed[key].push(val);
      } else {
        parsed[key] = [val];
      }
    } else {
      parsed[key] = parsed[key] ? parsed[key] + ', ' + val : val;
    }
  });

  return parsed;
});


/***/ }),

/***/ "./node_modules/axios/lib/helpers/parseProtocol.js":
/*!*********************************************************!*\
  !*** ./node_modules/axios/lib/helpers/parseProtocol.js ***!
  \*********************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ parseProtocol)
/* harmony export */ });


function parseProtocol(url) {
  const match = /^([-+\w]{1,25})(:?\/\/|:)/.exec(url);
  return match && match[1] || '';
}


/***/ }),

/***/ "./node_modules/axios/lib/helpers/speedometer.js":
/*!*******************************************************!*\
  !*** ./node_modules/axios/lib/helpers/speedometer.js ***!
  \*******************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });


/**
 * Calculate data maxRate
 * @param {Number} [samplesCount= 10]
 * @param {Number} [min= 1000]
 * @returns {Function}
 */
function speedometer(samplesCount, min) {
  samplesCount = samplesCount || 10;
  const bytes = new Array(samplesCount);
  const timestamps = new Array(samplesCount);
  let head = 0;
  let tail = 0;
  let firstSampleTS;

  min = min !== undefined ? min : 1000;

  return function push(chunkLength) {
    const now = Date.now();

    const startedAt = timestamps[tail];

    if (!firstSampleTS) {
      firstSampleTS = now;
    }

    bytes[head] = chunkLength;
    timestamps[head] = now;

    let i = tail;
    let bytesCount = 0;

    while (i !== head) {
      bytesCount += bytes[i++];
      i = i % samplesCount;
    }

    head = (head + 1) % samplesCount;

    if (head === tail) {
      tail = (tail + 1) % samplesCount;
    }

    if (now - firstSampleTS < min) {
      return;
    }

    const passed = startedAt && now - startedAt;

    return passed ? Math.round(bytesCount * 1000 / passed) : undefined;
  };
}

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (speedometer);


/***/ }),

/***/ "./node_modules/axios/lib/helpers/spread.js":
/*!**************************************************!*\
  !*** ./node_modules/axios/lib/helpers/spread.js ***!
  \**************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ spread)
/* harmony export */ });


/**
 * Syntactic sugar for invoking a function and expanding an array for arguments.
 *
 * Common use case would be to use `Function.prototype.apply`.
 *
 *  ```js
 *  function f(x, y, z) {}
 *  var args = [1, 2, 3];
 *  f.apply(null, args);
 *  ```
 *
 * With `spread` this example can be re-written.
 *
 *  ```js
 *  spread(function(x, y, z) {})([1, 2, 3]);
 *  ```
 *
 * @param {Function} callback
 *
 * @returns {Function}
 */
function spread(callback) {
  return function wrap(arr) {
    return callback.apply(null, arr);
  };
}


/***/ }),

/***/ "./node_modules/axios/lib/helpers/toFormData.js":
/*!******************************************************!*\
  !*** ./node_modules/axios/lib/helpers/toFormData.js ***!
  \******************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../utils.js */ "./node_modules/axios/lib/utils.js");
/* harmony import */ var _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../core/AxiosError.js */ "./node_modules/axios/lib/core/AxiosError.js");
/* harmony import */ var _platform_node_classes_FormData_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../platform/node/classes/FormData.js */ "./node_modules/axios/lib/helpers/null.js");




// temporary hotfix to avoid circular references until AxiosURLSearchParams is refactored


/**
 * Determines if the given thing is a array or js object.
 *
 * @param {string} thing - The object or array to be visited.
 *
 * @returns {boolean}
 */
function isVisitable(thing) {
  return _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isPlainObject(thing) || _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isArray(thing);
}

/**
 * It removes the brackets from the end of a string
 *
 * @param {string} key - The key of the parameter.
 *
 * @returns {string} the key without the brackets.
 */
function removeBrackets(key) {
  return _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].endsWith(key, '[]') ? key.slice(0, -2) : key;
}

/**
 * It takes a path, a key, and a boolean, and returns a string
 *
 * @param {string} path - The path to the current key.
 * @param {string} key - The key of the current object being iterated over.
 * @param {string} dots - If true, the key will be rendered with dots instead of brackets.
 *
 * @returns {string} The path to the current key.
 */
function renderKey(path, key, dots) {
  if (!path) return key;
  return path.concat(key).map(function each(token, i) {
    // eslint-disable-next-line no-param-reassign
    token = removeBrackets(token);
    return !dots && i ? '[' + token + ']' : token;
  }).join(dots ? '.' : '');
}

/**
 * If the array is an array and none of its elements are visitable, then it's a flat array.
 *
 * @param {Array<any>} arr - The array to check
 *
 * @returns {boolean}
 */
function isFlatArray(arr) {
  return _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isArray(arr) && !arr.some(isVisitable);
}

const predicates = _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].toFlatObject(_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"], {}, null, function filter(prop) {
  return /^is[A-Z]/.test(prop);
});

/**
 * Convert a data object to FormData
 *
 * @param {Object} obj
 * @param {?Object} [formData]
 * @param {?Object} [options]
 * @param {Function} [options.visitor]
 * @param {Boolean} [options.metaTokens = true]
 * @param {Boolean} [options.dots = false]
 * @param {?Boolean} [options.indexes = false]
 *
 * @returns {Object}
 **/

/**
 * It converts an object into a FormData object
 *
 * @param {Object<any, any>} obj - The object to convert to form data.
 * @param {string} formData - The FormData object to append to.
 * @param {Object<string, any>} options
 *
 * @returns
 */
function toFormData(obj, formData, options) {
  if (!_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isObject(obj)) {
    throw new TypeError('target must be an object');
  }

  // eslint-disable-next-line no-param-reassign
  formData = formData || new (_platform_node_classes_FormData_js__WEBPACK_IMPORTED_MODULE_1__["default"] || FormData)();

  // eslint-disable-next-line no-param-reassign
  options = _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].toFlatObject(options, {
    metaTokens: true,
    dots: false,
    indexes: false
  }, false, function defined(option, source) {
    // eslint-disable-next-line no-eq-null,eqeqeq
    return !_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isUndefined(source[option]);
  });

  const metaTokens = options.metaTokens;
  // eslint-disable-next-line no-use-before-define
  const visitor = options.visitor || defaultVisitor;
  const dots = options.dots;
  const indexes = options.indexes;
  const _Blob = options.Blob || typeof Blob !== 'undefined' && Blob;
  const useBlob = _Blob && _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isSpecCompliantForm(formData);

  if (!_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isFunction(visitor)) {
    throw new TypeError('visitor must be a function');
  }

  function convertValue(value) {
    if (value === null) return '';

    if (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isDate(value)) {
      return value.toISOString();
    }

    if (!useBlob && _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isBlob(value)) {
      throw new _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_2__["default"]('Blob is not supported. Use a Buffer instead.');
    }

    if (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isArrayBuffer(value) || _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isTypedArray(value)) {
      return useBlob && typeof Blob === 'function' ? new Blob([value]) : Buffer.from(value);
    }

    return value;
  }

  /**
   * Default visitor.
   *
   * @param {*} value
   * @param {String|Number} key
   * @param {Array<String|Number>} path
   * @this {FormData}
   *
   * @returns {boolean} return true to visit the each prop of the value recursively
   */
  function defaultVisitor(value, key, path) {
    let arr = value;

    if (value && !path && typeof value === 'object') {
      if (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].endsWith(key, '{}')) {
        // eslint-disable-next-line no-param-reassign
        key = metaTokens ? key : key.slice(0, -2);
        // eslint-disable-next-line no-param-reassign
        value = JSON.stringify(value);
      } else if (
        (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isArray(value) && isFlatArray(value)) ||
        ((_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isFileList(value) || _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].endsWith(key, '[]')) && (arr = _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].toArray(value))
        )) {
        // eslint-disable-next-line no-param-reassign
        key = removeBrackets(key);

        arr.forEach(function each(el, index) {
          !(_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isUndefined(el) || el === null) && formData.append(
            // eslint-disable-next-line no-nested-ternary
            indexes === true ? renderKey([key], index, dots) : (indexes === null ? key : key + '[]'),
            convertValue(el)
          );
        });
        return false;
      }
    }

    if (isVisitable(value)) {
      return true;
    }

    formData.append(renderKey(path, key, dots), convertValue(value));

    return false;
  }

  const stack = [];

  const exposedHelpers = Object.assign(predicates, {
    defaultVisitor,
    convertValue,
    isVisitable
  });

  function build(value, path) {
    if (_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isUndefined(value)) return;

    if (stack.indexOf(value) !== -1) {
      throw Error('Circular reference detected in ' + path.join('.'));
    }

    stack.push(value);

    _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].forEach(value, function each(el, key) {
      const result = !(_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isUndefined(el) || el === null) && visitor.call(
        formData, el, _utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isString(key) ? key.trim() : key, path, exposedHelpers
      );

      if (result === true) {
        build(el, path ? path.concat(key) : [key]);
      }
    });

    stack.pop();
  }

  if (!_utils_js__WEBPACK_IMPORTED_MODULE_0__["default"].isObject(obj)) {
    throw new TypeError('data must be an object');
  }

  build(obj);

  return formData;
}

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (toFormData);


/***/ }),

/***/ "./node_modules/axios/lib/helpers/toURLEncodedForm.js":
/*!************************************************************!*\
  !*** ./node_modules/axios/lib/helpers/toURLEncodedForm.js ***!
  \************************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ toURLEncodedForm)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../utils.js */ "./node_modules/axios/lib/utils.js");
/* harmony import */ var _toFormData_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./toFormData.js */ "./node_modules/axios/lib/helpers/toFormData.js");
/* harmony import */ var _platform_index_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../platform/index.js */ "./node_modules/axios/lib/platform/index.js");






function toURLEncodedForm(data, options) {
  return (0,_toFormData_js__WEBPACK_IMPORTED_MODULE_0__["default"])(data, new _platform_index_js__WEBPACK_IMPORTED_MODULE_1__["default"].classes.URLSearchParams(), Object.assign({
    visitor: function(value, key, path, helpers) {
      if (_platform_index_js__WEBPACK_IMPORTED_MODULE_1__["default"].isNode && _utils_js__WEBPACK_IMPORTED_MODULE_2__["default"].isBuffer(value)) {
        this.append(key, value.toString('base64'));
        return false;
      }

      return helpers.defaultVisitor.apply(this, arguments);
    }
  }, options));
}


/***/ }),

/***/ "./node_modules/axios/lib/helpers/validator.js":
/*!*****************************************************!*\
  !*** ./node_modules/axios/lib/helpers/validator.js ***!
  \*****************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _env_data_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../env/data.js */ "./node_modules/axios/lib/env/data.js");
/* harmony import */ var _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../core/AxiosError.js */ "./node_modules/axios/lib/core/AxiosError.js");





const validators = {};

// eslint-disable-next-line func-names
['object', 'boolean', 'number', 'function', 'string', 'symbol'].forEach((type, i) => {
  validators[type] = function validator(thing) {
    return typeof thing === type || 'a' + (i < 1 ? 'n ' : ' ') + type;
  };
});

const deprecatedWarnings = {};

/**
 * Transitional option validator
 *
 * @param {function|boolean?} validator - set to false if the transitional option has been removed
 * @param {string?} version - deprecated version / removed since version
 * @param {string?} message - some message with additional info
 *
 * @returns {function}
 */
validators.transitional = function transitional(validator, version, message) {
  function formatMessage(opt, desc) {
    return '[Axios v' + _env_data_js__WEBPACK_IMPORTED_MODULE_0__.VERSION + '] Transitional option \'' + opt + '\'' + desc + (message ? '. ' + message : '');
  }

  // eslint-disable-next-line func-names
  return (value, opt, opts) => {
    if (validator === false) {
      throw new _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_1__["default"](
        formatMessage(opt, ' has been removed' + (version ? ' in ' + version : '')),
        _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_1__["default"].ERR_DEPRECATED
      );
    }

    if (version && !deprecatedWarnings[opt]) {
      deprecatedWarnings[opt] = true;
      // eslint-disable-next-line no-console
      console.warn(
        formatMessage(
          opt,
          ' has been deprecated since v' + version + ' and will be removed in the near future'
        )
      );
    }

    return validator ? validator(value, opt, opts) : true;
  };
};

/**
 * Assert object's properties type
 *
 * @param {object} options
 * @param {object} schema
 * @param {boolean?} allowUnknown
 *
 * @returns {object}
 */

function assertOptions(options, schema, allowUnknown) {
  if (typeof options !== 'object') {
    throw new _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_1__["default"]('options must be an object', _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_1__["default"].ERR_BAD_OPTION_VALUE);
  }
  const keys = Object.keys(options);
  let i = keys.length;
  while (i-- > 0) {
    const opt = keys[i];
    const validator = schema[opt];
    if (validator) {
      const value = options[opt];
      const result = value === undefined || validator(value, opt, options);
      if (result !== true) {
        throw new _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_1__["default"]('option ' + opt + ' must be ' + result, _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_1__["default"].ERR_BAD_OPTION_VALUE);
      }
      continue;
    }
    if (allowUnknown !== true) {
      throw new _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_1__["default"]('Unknown option ' + opt, _core_AxiosError_js__WEBPACK_IMPORTED_MODULE_1__["default"].ERR_BAD_OPTION);
    }
  }
}

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ({
  assertOptions,
  validators
});


/***/ }),

/***/ "./node_modules/axios/lib/platform/browser/classes/Blob.js":
/*!*****************************************************************!*\
  !*** ./node_modules/axios/lib/platform/browser/classes/Blob.js ***!
  \*****************************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });


/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (typeof Blob !== 'undefined' ? Blob : null);


/***/ }),

/***/ "./node_modules/axios/lib/platform/browser/classes/FormData.js":
/*!*********************************************************************!*\
  !*** ./node_modules/axios/lib/platform/browser/classes/FormData.js ***!
  \*********************************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });


/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (typeof FormData !== 'undefined' ? FormData : null);


/***/ }),

/***/ "./node_modules/axios/lib/platform/browser/classes/URLSearchParams.js":
/*!****************************************************************************!*\
  !*** ./node_modules/axios/lib/platform/browser/classes/URLSearchParams.js ***!
  \****************************************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _helpers_AxiosURLSearchParams_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../../helpers/AxiosURLSearchParams.js */ "./node_modules/axios/lib/helpers/AxiosURLSearchParams.js");



/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (typeof URLSearchParams !== 'undefined' ? URLSearchParams : _helpers_AxiosURLSearchParams_js__WEBPACK_IMPORTED_MODULE_0__["default"]);


/***/ }),

/***/ "./node_modules/axios/lib/platform/browser/index.js":
/*!**********************************************************!*\
  !*** ./node_modules/axios/lib/platform/browser/index.js ***!
  \**********************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _classes_URLSearchParams_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./classes/URLSearchParams.js */ "./node_modules/axios/lib/platform/browser/classes/URLSearchParams.js");
/* harmony import */ var _classes_FormData_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./classes/FormData.js */ "./node_modules/axios/lib/platform/browser/classes/FormData.js");
/* harmony import */ var _classes_Blob_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./classes/Blob.js */ "./node_modules/axios/lib/platform/browser/classes/Blob.js");




/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ({
  isBrowser: true,
  classes: {
    URLSearchParams: _classes_URLSearchParams_js__WEBPACK_IMPORTED_MODULE_0__["default"],
    FormData: _classes_FormData_js__WEBPACK_IMPORTED_MODULE_1__["default"],
    Blob: _classes_Blob_js__WEBPACK_IMPORTED_MODULE_2__["default"]
  },
  protocols: ['http', 'https', 'file', 'blob', 'url', 'data']
});


/***/ }),

/***/ "./node_modules/axios/lib/platform/common/utils.js":
/*!*********************************************************!*\
  !*** ./node_modules/axios/lib/platform/common/utils.js ***!
  \*********************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   hasBrowserEnv: () => (/* binding */ hasBrowserEnv),
/* harmony export */   hasStandardBrowserEnv: () => (/* binding */ hasStandardBrowserEnv),
/* harmony export */   hasStandardBrowserWebWorkerEnv: () => (/* binding */ hasStandardBrowserWebWorkerEnv)
/* harmony export */ });
const hasBrowserEnv = typeof window !== 'undefined' && typeof document !== 'undefined';

/**
 * Determine if we're running in a standard browser environment
 *
 * This allows axios to run in a web worker, and react-native.
 * Both environments support XMLHttpRequest, but not fully standard globals.
 *
 * web workers:
 *  typeof window -> undefined
 *  typeof document -> undefined
 *
 * react-native:
 *  navigator.product -> 'ReactNative'
 * nativescript
 *  navigator.product -> 'NativeScript' or 'NS'
 *
 * @returns {boolean}
 */
const hasStandardBrowserEnv = (
  (product) => {
    return hasBrowserEnv && ['ReactNative', 'NativeScript', 'NS'].indexOf(product) < 0
  })(typeof navigator !== 'undefined' && navigator.product);

/**
 * Determine if we're running in a standard browser webWorker environment
 *
 * Although the `isStandardBrowserEnv` method indicates that
 * `allows axios to run in a web worker`, the WebWorker will still be
 * filtered out due to its judgment standard
 * `typeof window !== 'undefined' && typeof document !== 'undefined'`.
 * This leads to a problem when axios post `FormData` in webWorker
 */
const hasStandardBrowserWebWorkerEnv = (() => {
  return (
    typeof WorkerGlobalScope !== 'undefined' &&
    // eslint-disable-next-line no-undef
    self instanceof WorkerGlobalScope &&
    typeof self.importScripts === 'function'
  );
})();




/***/ }),

/***/ "./node_modules/axios/lib/platform/index.js":
/*!**************************************************!*\
  !*** ./node_modules/axios/lib/platform/index.js ***!
  \**************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_index_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./node/index.js */ "./node_modules/axios/lib/platform/browser/index.js");
/* harmony import */ var _common_utils_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./common/utils.js */ "./node_modules/axios/lib/platform/common/utils.js");



/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ({
  ..._common_utils_js__WEBPACK_IMPORTED_MODULE_0__,
  ..._node_index_js__WEBPACK_IMPORTED_MODULE_1__["default"]
});


/***/ }),

/***/ "./node_modules/axios/lib/utils.js":
/*!*****************************************!*\
  !*** ./node_modules/axios/lib/utils.js ***!
  \*****************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _helpers_bind_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./helpers/bind.js */ "./node_modules/axios/lib/helpers/bind.js");




// utils is a library of generic helper functions non-specific to axios

const {toString} = Object.prototype;
const {getPrototypeOf} = Object;

const kindOf = (cache => thing => {
    const str = toString.call(thing);
    return cache[str] || (cache[str] = str.slice(8, -1).toLowerCase());
})(Object.create(null));

const kindOfTest = (type) => {
  type = type.toLowerCase();
  return (thing) => kindOf(thing) === type
}

const typeOfTest = type => thing => typeof thing === type;

/**
 * Determine if a value is an Array
 *
 * @param {Object} val The value to test
 *
 * @returns {boolean} True if value is an Array, otherwise false
 */
const {isArray} = Array;

/**
 * Determine if a value is undefined
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if the value is undefined, otherwise false
 */
const isUndefined = typeOfTest('undefined');

/**
 * Determine if a value is a Buffer
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a Buffer, otherwise false
 */
function isBuffer(val) {
  return val !== null && !isUndefined(val) && val.constructor !== null && !isUndefined(val.constructor)
    && isFunction(val.constructor.isBuffer) && val.constructor.isBuffer(val);
}

/**
 * Determine if a value is an ArrayBuffer
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is an ArrayBuffer, otherwise false
 */
const isArrayBuffer = kindOfTest('ArrayBuffer');


/**
 * Determine if a value is a view on an ArrayBuffer
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a view on an ArrayBuffer, otherwise false
 */
function isArrayBufferView(val) {
  let result;
  if ((typeof ArrayBuffer !== 'undefined') && (ArrayBuffer.isView)) {
    result = ArrayBuffer.isView(val);
  } else {
    result = (val) && (val.buffer) && (isArrayBuffer(val.buffer));
  }
  return result;
}

/**
 * Determine if a value is a String
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a String, otherwise false
 */
const isString = typeOfTest('string');

/**
 * Determine if a value is a Function
 *
 * @param {*} val The value to test
 * @returns {boolean} True if value is a Function, otherwise false
 */
const isFunction = typeOfTest('function');

/**
 * Determine if a value is a Number
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a Number, otherwise false
 */
const isNumber = typeOfTest('number');

/**
 * Determine if a value is an Object
 *
 * @param {*} thing The value to test
 *
 * @returns {boolean} True if value is an Object, otherwise false
 */
const isObject = (thing) => thing !== null && typeof thing === 'object';

/**
 * Determine if a value is a Boolean
 *
 * @param {*} thing The value to test
 * @returns {boolean} True if value is a Boolean, otherwise false
 */
const isBoolean = thing => thing === true || thing === false;

/**
 * Determine if a value is a plain Object
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a plain Object, otherwise false
 */
const isPlainObject = (val) => {
  if (kindOf(val) !== 'object') {
    return false;
  }

  const prototype = getPrototypeOf(val);
  return (prototype === null || prototype === Object.prototype || Object.getPrototypeOf(prototype) === null) && !(Symbol.toStringTag in val) && !(Symbol.iterator in val);
}

/**
 * Determine if a value is a Date
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a Date, otherwise false
 */
const isDate = kindOfTest('Date');

/**
 * Determine if a value is a File
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a File, otherwise false
 */
const isFile = kindOfTest('File');

/**
 * Determine if a value is a Blob
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a Blob, otherwise false
 */
const isBlob = kindOfTest('Blob');

/**
 * Determine if a value is a FileList
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a File, otherwise false
 */
const isFileList = kindOfTest('FileList');

/**
 * Determine if a value is a Stream
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a Stream, otherwise false
 */
const isStream = (val) => isObject(val) && isFunction(val.pipe);

/**
 * Determine if a value is a FormData
 *
 * @param {*} thing The value to test
 *
 * @returns {boolean} True if value is an FormData, otherwise false
 */
const isFormData = (thing) => {
  let kind;
  return thing && (
    (typeof FormData === 'function' && thing instanceof FormData) || (
      isFunction(thing.append) && (
        (kind = kindOf(thing)) === 'formdata' ||
        // detect form-data instance
        (kind === 'object' && isFunction(thing.toString) && thing.toString() === '[object FormData]')
      )
    )
  )
}

/**
 * Determine if a value is a URLSearchParams object
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a URLSearchParams object, otherwise false
 */
const isURLSearchParams = kindOfTest('URLSearchParams');

/**
 * Trim excess whitespace off the beginning and end of a string
 *
 * @param {String} str The String to trim
 *
 * @returns {String} The String freed of excess whitespace
 */
const trim = (str) => str.trim ?
  str.trim() : str.replace(/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g, '');

/**
 * Iterate over an Array or an Object invoking a function for each item.
 *
 * If `obj` is an Array callback will be called passing
 * the value, index, and complete array for each item.
 *
 * If 'obj' is an Object callback will be called passing
 * the value, key, and complete object for each property.
 *
 * @param {Object|Array} obj The object to iterate
 * @param {Function} fn The callback to invoke for each item
 *
 * @param {Boolean} [allOwnKeys = false]
 * @returns {any}
 */
function forEach(obj, fn, {allOwnKeys = false} = {}) {
  // Don't bother if no value provided
  if (obj === null || typeof obj === 'undefined') {
    return;
  }

  let i;
  let l;

  // Force an array if not already something iterable
  if (typeof obj !== 'object') {
    /*eslint no-param-reassign:0*/
    obj = [obj];
  }

  if (isArray(obj)) {
    // Iterate over array values
    for (i = 0, l = obj.length; i < l; i++) {
      fn.call(null, obj[i], i, obj);
    }
  } else {
    // Iterate over object keys
    const keys = allOwnKeys ? Object.getOwnPropertyNames(obj) : Object.keys(obj);
    const len = keys.length;
    let key;

    for (i = 0; i < len; i++) {
      key = keys[i];
      fn.call(null, obj[key], key, obj);
    }
  }
}

function findKey(obj, key) {
  key = key.toLowerCase();
  const keys = Object.keys(obj);
  let i = keys.length;
  let _key;
  while (i-- > 0) {
    _key = keys[i];
    if (key === _key.toLowerCase()) {
      return _key;
    }
  }
  return null;
}

const _global = (() => {
  /*eslint no-undef:0*/
  if (typeof globalThis !== "undefined") return globalThis;
  return typeof self !== "undefined" ? self : (typeof window !== 'undefined' ? window : global)
})();

const isContextDefined = (context) => !isUndefined(context) && context !== _global;

/**
 * Accepts varargs expecting each argument to be an object, then
 * immutably merges the properties of each object and returns result.
 *
 * When multiple objects contain the same key the later object in
 * the arguments list will take precedence.
 *
 * Example:
 *
 * ```js
 * var result = merge({foo: 123}, {foo: 456});
 * console.log(result.foo); // outputs 456
 * ```
 *
 * @param {Object} obj1 Object to merge
 *
 * @returns {Object} Result of all merge properties
 */
function merge(/* obj1, obj2, obj3, ... */) {
  const {caseless} = isContextDefined(this) && this || {};
  const result = {};
  const assignValue = (val, key) => {
    const targetKey = caseless && findKey(result, key) || key;
    if (isPlainObject(result[targetKey]) && isPlainObject(val)) {
      result[targetKey] = merge(result[targetKey], val);
    } else if (isPlainObject(val)) {
      result[targetKey] = merge({}, val);
    } else if (isArray(val)) {
      result[targetKey] = val.slice();
    } else {
      result[targetKey] = val;
    }
  }

  for (let i = 0, l = arguments.length; i < l; i++) {
    arguments[i] && forEach(arguments[i], assignValue);
  }
  return result;
}

/**
 * Extends object a by mutably adding to it the properties of object b.
 *
 * @param {Object} a The object to be extended
 * @param {Object} b The object to copy properties from
 * @param {Object} thisArg The object to bind function to
 *
 * @param {Boolean} [allOwnKeys]
 * @returns {Object} The resulting value of object a
 */
const extend = (a, b, thisArg, {allOwnKeys}= {}) => {
  forEach(b, (val, key) => {
    if (thisArg && isFunction(val)) {
      a[key] = (0,_helpers_bind_js__WEBPACK_IMPORTED_MODULE_0__["default"])(val, thisArg);
    } else {
      a[key] = val;
    }
  }, {allOwnKeys});
  return a;
}

/**
 * Remove byte order marker. This catches EF BB BF (the UTF-8 BOM)
 *
 * @param {string} content with BOM
 *
 * @returns {string} content value without BOM
 */
const stripBOM = (content) => {
  if (content.charCodeAt(0) === 0xFEFF) {
    content = content.slice(1);
  }
  return content;
}

/**
 * Inherit the prototype methods from one constructor into another
 * @param {function} constructor
 * @param {function} superConstructor
 * @param {object} [props]
 * @param {object} [descriptors]
 *
 * @returns {void}
 */
const inherits = (constructor, superConstructor, props, descriptors) => {
  constructor.prototype = Object.create(superConstructor.prototype, descriptors);
  constructor.prototype.constructor = constructor;
  Object.defineProperty(constructor, 'super', {
    value: superConstructor.prototype
  });
  props && Object.assign(constructor.prototype, props);
}

/**
 * Resolve object with deep prototype chain to a flat object
 * @param {Object} sourceObj source object
 * @param {Object} [destObj]
 * @param {Function|Boolean} [filter]
 * @param {Function} [propFilter]
 *
 * @returns {Object}
 */
const toFlatObject = (sourceObj, destObj, filter, propFilter) => {
  let props;
  let i;
  let prop;
  const merged = {};

  destObj = destObj || {};
  // eslint-disable-next-line no-eq-null,eqeqeq
  if (sourceObj == null) return destObj;

  do {
    props = Object.getOwnPropertyNames(sourceObj);
    i = props.length;
    while (i-- > 0) {
      prop = props[i];
      if ((!propFilter || propFilter(prop, sourceObj, destObj)) && !merged[prop]) {
        destObj[prop] = sourceObj[prop];
        merged[prop] = true;
      }
    }
    sourceObj = filter !== false && getPrototypeOf(sourceObj);
  } while (sourceObj && (!filter || filter(sourceObj, destObj)) && sourceObj !== Object.prototype);

  return destObj;
}

/**
 * Determines whether a string ends with the characters of a specified string
 *
 * @param {String} str
 * @param {String} searchString
 * @param {Number} [position= 0]
 *
 * @returns {boolean}
 */
const endsWith = (str, searchString, position) => {
  str = String(str);
  if (position === undefined || position > str.length) {
    position = str.length;
  }
  position -= searchString.length;
  const lastIndex = str.indexOf(searchString, position);
  return lastIndex !== -1 && lastIndex === position;
}


/**
 * Returns new array from array like object or null if failed
 *
 * @param {*} [thing]
 *
 * @returns {?Array}
 */
const toArray = (thing) => {
  if (!thing) return null;
  if (isArray(thing)) return thing;
  let i = thing.length;
  if (!isNumber(i)) return null;
  const arr = new Array(i);
  while (i-- > 0) {
    arr[i] = thing[i];
  }
  return arr;
}

/**
 * Checking if the Uint8Array exists and if it does, it returns a function that checks if the
 * thing passed in is an instance of Uint8Array
 *
 * @param {TypedArray}
 *
 * @returns {Array}
 */
// eslint-disable-next-line func-names
const isTypedArray = (TypedArray => {
  // eslint-disable-next-line func-names
  return thing => {
    return TypedArray && thing instanceof TypedArray;
  };
})(typeof Uint8Array !== 'undefined' && getPrototypeOf(Uint8Array));

/**
 * For each entry in the object, call the function with the key and value.
 *
 * @param {Object<any, any>} obj - The object to iterate over.
 * @param {Function} fn - The function to call for each entry.
 *
 * @returns {void}
 */
const forEachEntry = (obj, fn) => {
  const generator = obj && obj[Symbol.iterator];

  const iterator = generator.call(obj);

  let result;

  while ((result = iterator.next()) && !result.done) {
    const pair = result.value;
    fn.call(obj, pair[0], pair[1]);
  }
}

/**
 * It takes a regular expression and a string, and returns an array of all the matches
 *
 * @param {string} regExp - The regular expression to match against.
 * @param {string} str - The string to search.
 *
 * @returns {Array<boolean>}
 */
const matchAll = (regExp, str) => {
  let matches;
  const arr = [];

  while ((matches = regExp.exec(str)) !== null) {
    arr.push(matches);
  }

  return arr;
}

/* Checking if the kindOfTest function returns true when passed an HTMLFormElement. */
const isHTMLForm = kindOfTest('HTMLFormElement');

const toCamelCase = str => {
  return str.toLowerCase().replace(/[-_\s]([a-z\d])(\w*)/g,
    function replacer(m, p1, p2) {
      return p1.toUpperCase() + p2;
    }
  );
};

/* Creating a function that will check if an object has a property. */
const hasOwnProperty = (({hasOwnProperty}) => (obj, prop) => hasOwnProperty.call(obj, prop))(Object.prototype);

/**
 * Determine if a value is a RegExp object
 *
 * @param {*} val The value to test
 *
 * @returns {boolean} True if value is a RegExp object, otherwise false
 */
const isRegExp = kindOfTest('RegExp');

const reduceDescriptors = (obj, reducer) => {
  const descriptors = Object.getOwnPropertyDescriptors(obj);
  const reducedDescriptors = {};

  forEach(descriptors, (descriptor, name) => {
    let ret;
    if ((ret = reducer(descriptor, name, obj)) !== false) {
      reducedDescriptors[name] = ret || descriptor;
    }
  });

  Object.defineProperties(obj, reducedDescriptors);
}

/**
 * Makes all methods read-only
 * @param {Object} obj
 */

const freezeMethods = (obj) => {
  reduceDescriptors(obj, (descriptor, name) => {
    // skip restricted props in strict mode
    if (isFunction(obj) && ['arguments', 'caller', 'callee'].indexOf(name) !== -1) {
      return false;
    }

    const value = obj[name];

    if (!isFunction(value)) return;

    descriptor.enumerable = false;

    if ('writable' in descriptor) {
      descriptor.writable = false;
      return;
    }

    if (!descriptor.set) {
      descriptor.set = () => {
        throw Error('Can not rewrite read-only method \'' + name + '\'');
      };
    }
  });
}

const toObjectSet = (arrayOrString, delimiter) => {
  const obj = {};

  const define = (arr) => {
    arr.forEach(value => {
      obj[value] = true;
    });
  }

  isArray(arrayOrString) ? define(arrayOrString) : define(String(arrayOrString).split(delimiter));

  return obj;
}

const noop = () => {}

const toFiniteNumber = (value, defaultValue) => {
  value = +value;
  return Number.isFinite(value) ? value : defaultValue;
}

const ALPHA = 'abcdefghijklmnopqrstuvwxyz'

const DIGIT = '0123456789';

const ALPHABET = {
  DIGIT,
  ALPHA,
  ALPHA_DIGIT: ALPHA + ALPHA.toUpperCase() + DIGIT
}

const generateString = (size = 16, alphabet = ALPHABET.ALPHA_DIGIT) => {
  let str = '';
  const {length} = alphabet;
  while (size--) {
    str += alphabet[Math.random() * length|0]
  }

  return str;
}

/**
 * If the thing is a FormData object, return true, otherwise return false.
 *
 * @param {unknown} thing - The thing to check.
 *
 * @returns {boolean}
 */
function isSpecCompliantForm(thing) {
  return !!(thing && isFunction(thing.append) && thing[Symbol.toStringTag] === 'FormData' && thing[Symbol.iterator]);
}

const toJSONObject = (obj) => {
  const stack = new Array(10);

  const visit = (source, i) => {

    if (isObject(source)) {
      if (stack.indexOf(source) >= 0) {
        return;
      }

      if(!('toJSON' in source)) {
        stack[i] = source;
        const target = isArray(source) ? [] : {};

        forEach(source, (value, key) => {
          const reducedValue = visit(value, i + 1);
          !isUndefined(reducedValue) && (target[key] = reducedValue);
        });

        stack[i] = undefined;

        return target;
      }
    }

    return source;
  }

  return visit(obj, 0);
}

const isAsyncFn = kindOfTest('AsyncFunction');

const isThenable = (thing) =>
  thing && (isObject(thing) || isFunction(thing)) && isFunction(thing.then) && isFunction(thing.catch);

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ({
  isArray,
  isArrayBuffer,
  isBuffer,
  isFormData,
  isArrayBufferView,
  isString,
  isNumber,
  isBoolean,
  isObject,
  isPlainObject,
  isUndefined,
  isDate,
  isFile,
  isBlob,
  isRegExp,
  isFunction,
  isStream,
  isURLSearchParams,
  isTypedArray,
  isFileList,
  forEach,
  merge,
  extend,
  trim,
  stripBOM,
  inherits,
  toFlatObject,
  kindOf,
  kindOfTest,
  endsWith,
  toArray,
  forEachEntry,
  matchAll,
  isHTMLForm,
  hasOwnProperty,
  hasOwnProp: hasOwnProperty, // an alias to avoid ESLint no-prototype-builtins detection
  reduceDescriptors,
  freezeMethods,
  toObjectSet,
  toCamelCase,
  noop,
  toFiniteNumber,
  findKey,
  global: _global,
  isContextDefined,
  ALPHABET,
  generateString,
  isSpecCompliantForm,
  toJSONObject,
  isAsyncFn,
  isThenable
});


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry need to be wrapped in an IIFE because it need to be isolated against other modules in the chunk.
(() => {
/*!*************************!*\
  !*** ./ui_src/index.ts ***!
  \*************************/
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _drawing__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./drawing */ "./ui_src/drawing.ts");
/* harmony import */ var _visual__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./visual */ "./ui_src/visual.ts");
/* harmony import */ var _plan_visualiser_api__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./plan_visualiser_api */ "./ui_src/plan_visualiser_api.ts");
/* harmony import */ var _manage_visual__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./manage_visual */ "./ui_src/manage_visual.ts");
/* harmony import */ var _plot_visual__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./plot_visual */ "./ui_src/plot_visual.ts");
/* harmony import */ var _utilities__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./utilities */ "./ui_src/utilities.ts");
/* harmony import */ var _manage_swimlanes__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./manage_swimlanes */ "./ui_src/manage_swimlanes.ts");
/* harmony import */ var _manage_timelines__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./manage_timelines */ "./ui_src/manage_timelines.ts");
/* harmony import */ var _manage_visual_image__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./manage_visual_image */ "./ui_src/manage_visual_image.ts");










window.addEventListener('DOMContentLoaded', () => {
    console.log("DOM Loaded zzzz....");
});
console.log("Executing index.ts");
window.get_plan_activity_data = _plan_visualiser_api__WEBPACK_IMPORTED_MODULE_2__.get_plan_activity_data;
window.get_visual_activity_data = _plan_visualiser_api__WEBPACK_IMPORTED_MODULE_2__.get_visual_activity_data;
window.createPlanTree = _manage_visual__WEBPACK_IMPORTED_MODULE_3__.createPlanTree;
window.addStylesheetToDOM = _utilities__WEBPACK_IMPORTED_MODULE_5__.addStylesheetToDOM;
window.checkKey = _visual__WEBPACK_IMPORTED_MODULE_1__.checkKey;
window.initialise_canvas = _drawing__WEBPACK_IMPORTED_MODULE_0__.initialise_canvas;
window.initialise_canvases = _plot_visual__WEBPACK_IMPORTED_MODULE_4__.initialise_canvases;
window.plot_visual = _plot_visual__WEBPACK_IMPORTED_MODULE_4__.plot_visual;
window.update_swimlane_data = _manage_swimlanes__WEBPACK_IMPORTED_MODULE_6__.update_swimlane_data;
window.update_timeline_panel = _manage_timelines__WEBPACK_IMPORTED_MODULE_7__.update_timeline_panel;
window.get_style_records = _plan_visualiser_api__WEBPACK_IMPORTED_MODULE_2__.get_style_records;
window.get_shape_records = _plan_visualiser_api__WEBPACK_IMPORTED_MODULE_2__.get_shape_records;
window.get_visual_settings = _plan_visualiser_api__WEBPACK_IMPORTED_MODULE_2__.get_visual_settings;
window.add_download_image_event_listener = _manage_visual_image__WEBPACK_IMPORTED_MODULE_8__.add_download_image_event_listener;
window.addVisualImages = _manage_visual_image__WEBPACK_IMPORTED_MODULE_8__.addVisualImages;

})();

/******/ })()
;
//# sourceMappingURL=bundle.js.map