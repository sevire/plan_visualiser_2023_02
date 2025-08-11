/**
 * NOTE 2025-08-11: Creating this as part of major re-factor of structure of UI code.  So will build up the elements
 * over time and not everything will be here immediately - some elements will remain in their original position until
 * they are addressed as part of the re-factor.
 * 
 * This file will contain components for managing the plan tree as part of the edit visual screen.
 * 
 */

class PlanTreeManager {
  private rootElement: HTMLElement;

  /**
   * Constructor to set up the manager with the root element of the plan tree.
   * @param rootElement - The root element of the tree (e.g., a <ul> or <div> that contains tree nodes).
   */
  constructor(rootElement: HTMLElement) {
    this.rootElement = rootElement;
  }

  /**
   * Sets all immediate children (sub-elements) of a given tree element to be in the visual.
   * @param parentActivityId - The unique ID of the parent activity in the tree.
   * @param toggleFunction - A function that toggles an activity's inclusion in the visual.
   *                         This may involve backend API calls or DOM updates.
   * @returns A Promise that resolves when all sub-elements are processed.
   */
  async setSubElementsInVisual(
    parentActivityId: string,
    toggleFunction: (activityId: string, inVisual: boolean) => Promise<void>
  ): Promise<void> {
    // Retrieve parent element based on its unique ID
    const parentElement = this.rootElement.querySelector(`[data-activity-id="${parentActivityId}"]`);
    if (!parentElement) {
      console.error(`Parent element with ID ${parentActivityId} not found.`);
      return;
    }

    // Get immediate children of the parent element
    const childElements = Array.from(parentElement.querySelectorAll(":scope > ul > li"));

    if (childElements.length === 0) {
      console.log(`No child elements found for parent activity ID: ${parentActivityId}`);
      return;
    }

    // Process each child element
    for (const childElement of childElements) {
      const activityId = childElement.getAttribute("data-activity-id");
      if (activityId) {
        console.log(`Setting child activity ${activityId} to be in the visual.`);
        await toggleFunction(activityId, true); // Call the provided function to toggle inclusion
      } else {
        console.warn("Child element missing 'data-activity-id' attribute.");
      }
    }
  }
}

// Export the class as a module
export default PlanTreeManager;