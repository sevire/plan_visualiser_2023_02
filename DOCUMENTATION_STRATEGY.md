### Documentation Strategy & Best Practices

For a project with a Python (Django) backend and a TypeScript frontend, a multi-layered documentation strategy ensures that both high-level concepts and low-level implementation details are accessible to different stakeholders (developers, maintainers, users).

#### 1. High-Level Documentation (Project Root)
The root of the project should provide the entry point for anyone new to the repository.

*   **README.md**: The "front door". It should include:
    *   Project vision and core features.
    *   Quick-start guide (How to get it running in 5 minutes).
    *   Prerequisites (Python version, Node version, etc.).
    *   High-level architecture diagram or description.
    *   Link to more detailed documentation.
*   **ARCHITECTURE.md**: Explains the "why" behind technical decisions.
    *   Backend (Django, DRF) vs Frontend (TypeScript/React/etc.) relationship.
    *   Data flow (API, WebSockets).
    *   Key components (e.g., Renderers, Parsers).

#### 2. Backend Documentation (Python)
Python has a mature ecosystem for documentation.

*   **Docstrings (Google or NumPy style)**:
    *   Mandatory for public classes and methods.
    *   Example:
        ```python
        def render_plotable(self, plotable: Plotable):
            """
            Converts a Plotable object into a PowerPoint shape.

            Args:
                plotable (Plotable): The object containing coordinates and styling.
            """
        ```
*   **MkDocs with Material Theme**:
    *   Modern, fast, and easy to host (GitHub Pages).
    *   Use `mkdocstrings` to automatically pull documentation from Python code.
*   **Sphinx**:
    *   The industry standard for complex Python projects. Excellent for PDF output and cross-referencing.

#### 3. Frontend Documentation (TypeScript)
TypeScript's type system itself acts as a form of documentation, but it's not enough.

*   **JSDoc/TSDoc**:
    *   Use for explaining the purpose of components, functions, and interfaces.
*   **TypeDoc**:
    *   The TypeScript equivalent of Javadoc/Doxygen. It generates a searchable website from your TSDoc comments.
*   **Storybook (if using a UI framework)**:
    *   Indispensable for documenting UI components in isolation. It serves as both documentation and a playground.

#### 4. API Documentation (The Bridge)
Since the frontend and backend communicate via API, this is the most critical documentation area.

*   **OpenAPI (Swagger)**:
    *   Use `drf-spectacular` or `drf-yasg` with Django Rest Framework.
    *   Automatically generates interactive documentation (Swagger UI) where developers can test endpoints.
    *   Enables client generation (e.g., generating TypeScript types from the backend API).

#### 5. Developer & DevOps Guides
Located in `/documents` or `/docs`.

*   **CONTRIBUTING.md**: Rules for branching, PRs, and coding standards.
*   **DEVELOPMENT.md**: Environment setup, running tests, linting commands.
*   **DEPLOYMENT.md**: Steps to move code to production, environment variables, CI/CD pipeline overview.

#### 6. Summary of Tools Recommended
| Area | Recommended Tool |
| :--- | :--- |
| **Global** | Markdown (README.md, ARCHITECTURE.md) |
| **Backend** | MkDocs + `mkdocstrings` |
| **Frontend** | TypeDoc |
| **API** | OpenAPI (Swagger) via `drf-spectacular` |
| **Architecture** | Mermaid.js (for diagrams in Markdown) |
