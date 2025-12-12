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