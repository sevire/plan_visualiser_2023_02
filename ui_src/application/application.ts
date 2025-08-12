import PlanTreeManager from "../plan-tree/manage-plan-tree";

class App {
  private planTreeManager: PlanTreeManager | null = null;

  /**
   * Initializes the application, creating and linking all necessary managers.
   * This method will likely be called once on page load.
   */
  public initialize(): void {
    console.log("Initializing App...");

    // Set up the PlanTreeManager
    this.planTreeManager = new PlanTreeManager();
    console.log("PlanTreeManager initialized.");

    // Initialize other components/managers here as needed
  }

  /**
   * Gets the PlanTreeManager instance.
   * Throws an error if it has not been initialized.
   */
  public getPlanTreeManager(): PlanTreeManager {
    if (!this.planTreeManager) {
      throw new Error("PlanTreeManager has not been initialized.");
    }
    return this.planTreeManager;
  }

  /**
   * Example of handling global API data fetching, if needed.
   */
  public async fetchData(endpoint: string): Promise<any> {
    try {
      const response = await fetch(endpoint);
      if (!response.ok) {
        throw new Error(`Failed to fetch data: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error(error);
      return null;
    }
  }
}

export default new App(); // Export a singleton instance of App