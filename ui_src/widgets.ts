import {get_visual_activity_data} from "./plan_visualiser_api";
import {plot_visual} from "./plot_visual";

export class Dropdown {
    // General class which creates a dropdown for use in the activity panel to handle changes to attributes such as
    // swimlane, style, shape etc for a given visual activity.
    // Handles the creation of a dropdown widget and then calls the passed in callback function when one of the options
    // is selected.
    activity_unique_id: string;
    element: HTMLElement | null;
    options: [[string, number]]; // [0] is text for dropdown, [1] is id to use for option HTML element
    selectedOption: string;

    // Select handler will take the unique id of the activity and the selected value.  The passed in function should use
    // this to send an update to the activity, and when that is complete the common handler in this class will get
    // updated canvas data and re-plot the visual.
    select_handler: (unique_id: string, selected_value: number) => void;

    constructor(id: string, activity_unique_id: string, options: [[string, number]], select_handler: (unique_id:string, selected_id: number) => void) {
        this.activity_unique_id = activity_unique_id;
        this.options = options;
        this.element = document.getElementById(id);
        this.selectedOption = this.options[0][0];
        this.select_handler = select_handler;

        this.generate();
    }

    async generate() {
        const select = document.createElement('select');
        select.id = "select_element"
        this.options.forEach(option => {
            const option_text = option[0];
            const option_id = option[1]
            const optElement = document.createElement('option');
            optElement.text = option_text;
            optElement.value = option_text;
            optElement.id = option_id.toString();
            select.add(optElement);
        })

        select.addEventListener('click', async (event) => {
            const targetSelectedElement = event.target as HTMLSelectElement;
            const targetOptionElement: HTMLOptionElement = targetSelectedElement.options[targetSelectedElement.selectedIndex];
            const swimlane_id = parseInt(targetOptionElement.id);
            console.log(`Swimlane selected: text:${this.selectedOption}, id:${swimlane_id}`);

            await this.select_handler(this.activity_unique_id, swimlane_id);
            await get_visual_activity_data((window as any).visual_id)
            plot_visual()

        })

        if(this.element) {
            this.element.appendChild(select);
        }
    }
}

export function create_button_with_icon(icon_name: string) {
    const button = document.createElement("button")
    button.classList.add("btn", "btn-primary")

    let iconElement = document.createElement('i')
    iconElement.classList.add("bi", icon_name)
    button.appendChild(iconElement)

    return button
}

export async function add_tooltip(element: HTMLElement, tooltip_text: string) {
    element.setAttribute("data-bs-toggle", "tooltip")
    element.setAttribute("data-bs-placement", "top")
    element.setAttribute("title", tooltip_text)
}

export function clearElement(element: HTMLElement) {
  element.textContent = '';
}

export function createDropdown(
  parentElement: HTMLElement,
  buttonLabel: string,
  classesToAdd?: string[]
): HTMLButtonElement {
  console.log(`Creating dropdown with initial value ${buttonLabel} under ${parentElement}`)
  const dropdownDiv = document.createElement("div")
  dropdownDiv.classList.add("dropdown")
  parentElement.appendChild(dropdownDiv)

  // Add button to Dropdown
  const dropdownButton = document.createElement("button")
  dropdownButton.style.width = "100%" // TEMP Proof of concept to get text-truncate working.
  dropdownButton.setAttribute("type", "button")
  dropdownButton.setAttribute("data-bs-toggle", "dropdown")
  dropdownButton.setAttribute("aria-expanded", "false")
  dropdownButton.classList.add("btn", "btn-sm", "btn-secondary", "dropdown-toggle")
  if (classesToAdd) {
    dropdownButton.classList.add(...classesToAdd)
  }

  // Add text for button as a span element to allow .text-truncate to work without removing the button icon
  // NOTE: I'm not exactly sure why this works! Got here by trial and error.
  const spanElement = document.createElement("span")
  spanElement.classList.add("text-truncate")
  const stylingForDropdown =
    "display: inline-block;" +
    "vertical-align: top;" +
    "width: 90%"
  spanElement.style.cssText = stylingForDropdown
  spanElement.textContent = buttonLabel
  dropdownButton.appendChild(spanElement)
  dropdownDiv.appendChild(dropdownButton)

  // Add dropdown menu to Dropdown
  const dropdownMenu = document.createElement("ul")
  dropdownMenu.classList.add("dropdown-menu")
  dropdownDiv.appendChild(dropdownMenu)

  return dropdownButton;
}

export function populateDropdown(dropdownButton: HTMLButtonElement, names: [string, number][], updateHandler: Function) {
  console.log(`Populating dropdown...`)
  names.forEach((name: [string, number]) => {
    const entry = document.createElement('li');
    entry.classList.add("dropdown-item")
    entry.setAttribute("href", "#")
    entry.setAttribute("id", String(name[1]))
    entry.textContent = name[0];

    entry.addEventListener('click', async function (event) {
      console.log(`New selection for element, ${event.target}`)
      const targetSelectedElement = event.target as HTMLLIElement;
      const id = parseInt(targetSelectedElement.id);
      console.log(`Selected: text:${targetSelectedElement.textContent}, id:${id}`);

      // Update text for span element to selected option
      const dropdownSpan = dropdownButton.querySelector("span")
      dropdownSpan!.textContent = targetSelectedElement.textContent

      await updateHandler(id)  // Pass update functions as arguments
    });

    dropdownButton.parentElement!.querySelector('.dropdown-menu')!.appendChild(entry);
  });
}