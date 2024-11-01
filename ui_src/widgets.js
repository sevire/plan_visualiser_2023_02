var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { get_visual_activity_data } from "./plan_visualiser_api";
import { plot_visual } from "./plot_visual";
export class Dropdown {
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
                yield get_visual_activity_data(window.visual_id);
                plot_visual();
            }));
            if (this.element) {
                this.element.appendChild(select);
            }
        });
    }
}
export function create_button_with_icon(icon_name) {
    const button = document.createElement("button");
    button.classList.add("btn", "btn-primary");
    let iconElement = document.createElement('i');
    iconElement.classList.add("bi", icon_name);
    button.appendChild(iconElement);
    return button;
}
export function add_tooltip(element, tooltip_text) {
    return __awaiter(this, void 0, void 0, function* () {
        element.setAttribute("data-bs-toggle", "tooltip");
        element.setAttribute("data-bs-placement", "top");
        element.setAttribute("title", tooltip_text);
    });
}
export function clearElement(element) {
    element.textContent = '';
}
export function createDropdown(parentElement, buttonLabel, classesToAdd) {
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
export function populateDropdown(dropdownButton, names, updateHandler) {
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
