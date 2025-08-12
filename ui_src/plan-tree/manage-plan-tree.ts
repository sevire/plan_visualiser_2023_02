class PlanTreeManager {
  private rootElement: string;

  /**
   * Constructor to set up the manager with the root element of the plan tree.
   * @param rootElement - The root element of the tree (e.g., a <ul> or <div> that contains tree nodes).
   */
  constructor() {
    this.rootElement = "dummy for now";
  }

  /**
   * Sets all immediate sub-elements of a given element to be in the visual.
   * The parameter element is a `div` inside an `li`, and its sibling `ul` contains the child `li` elements.
   * @param parentDiv - The `div` element whose sub-activities should be added to the visual.
   */
  setSubActivitiesInVisual(parentDiv: HTMLElement): void {
    console.log(`setSubActivitiesInVisual called with ${parentDiv.tagName} element: ${parentDiv.outerHTML}`);
    // Find the sibling `ul` element that contains the child `li` elements
    const parentLi = parentDiv.parentElement; // The `li` containing this `div`
    if (!parentLi) {
      console.error("Parent <li> not found for the given <div> element.");
      return;
    }

    const childUl = parentLi.querySelector(":scope > ul"); // Find the direct child `ul`
    if (!childUl) {
      console.log(`No <ul> found for parent activity element:`, parentDiv);
      return;
    }

    // Iterate through all direct `li` under the `ul`
    const childLiElements = Array.from(childUl.querySelectorAll(":scope > li"));
    for (const childLi of childLiElements) {
      // Find the `div` within the `li` and add the `in-visual` class
      const childDiv = childLi.querySelector(":scope > div");
      if (childDiv) {
        childDiv.classList.add("in-visual"); // Add the class
        console.log(`Added "in-visual" class to activity:`, childDiv);
      } else {
        console.warn("No <div> found within child <li> element:", childLi);
      }
    }
  }
}

export default PlanTreeManager;