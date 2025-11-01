# Django Project Restructuring Recommendations (Non‑Breaking)

Purpose: Provide a clear, non-breaking path to reorganize the codebase for maintainability and scalability while keeping all existing URLs, behavior, and import paths working during the transition.

Guiding constraints captured from you:
- Do not change URL structure or route names right now.
- Prefer a logical, simple, and consistent structure.
- Minimize risk; allow phased migration with roll-back safety.


## High-level approach: Feature-first (domain) organization with compatibility shims

Move from large monolithic modules to small domain-focused packages. Re-export symbols from current module entry points so external imports keep working during the transition.

Domains suggested for this project:
- plans: Plan management (upload, parse, re-upload, delete)
- visuals: Visual creation, editing, plotting, auto-layout
- styling: Colors, fonts, plotable styles
- content: Static/Help content pages
- auth: Authentication and registration


## Proposed structure (phase 1: additive, non-breaking)

plan_visual_django/
- views/
  - __init__.py            # Re-export existing public view callables to preserve from plan_visual_django import views
  - plans.py               # manage_plans, add_plan, re_upload_plan, delete_plan, FileTypeListView
  - visuals.py             # manage_visuals, add_visual, add_default_visual, add_auto_visual
  - visual_edit.py         # edit_visual, delete_visual
  - visual_plot.py         # plot_visual, plot_visual_new_25
  - visual_parts.py        # manage_swimlanes_for_visual, manage_timelines_for_visual, create_milestone_swimlane, swimlane_actions
  - styling.py             # manage_colors, manage_plotable_styles
  - content.py             # StaticPageView
  - auth.py                # register, CustomLoginView
- models/
  - __init__.py            # Re-export to preserve from plan_visual_django.models import Plan, PlanVisual, ...
  - plan.py
  - visual.py
  - styling.py             # Color, Font, PlotableStyle
  - content.py             # StaticContent, HelpText
  - users.py               # CustomUser (if/when split)
- admin/
  - __init__.py            # Re-export ModelAdmins to preserve existing imports
  - plans.py
  - visuals.py
  - styling.py
  - content.py
  - users.py
- forms/
  - __init__.py
  - plans.py
  - visuals.py
  - styling.py
  - auth.py
- services/
  - auth/
    - user_services.py     # keep as-is
  - general/
    - color_utilities.py
    - date_utilities.py
    - text_constants.py
  - plan_file_utilities/
    - plan_reader.py
    - plan_parsing.py
    - plan_field.py
    - plan_tree.py
  - visual/
    - model/
      - auto_layout.py
      - visual_settings.py
      - timelines.py
      - plotable_shapes.py
    - rendering/
      - plotables.py
      - renderer.py (if split in future)
- urls.py                  # unchanged, continues to import from plan_visual_django.views

Notes:
- This is a file move/rename only. No behavior or URLs change.
- __init__.py modules re-export original names so external modules (including urls.py) don’t need to change immediately.


## URL integrity: keep current routing

- plan_visualiser_2023_02/urls.py keeps:
  - path("pv/", include("plan_visual_django.urls"))
- plan_visual_django/urls.py keeps all existing names and paths. View callables will be imported from plan_visual_django.views package modules but re-exported via views/__init__.py so existing import sites still work.


## Detailed file moves and responsibilities

Views (split by responsibility):
- plans.py: add_plan, re_upload_plan, delete_plan, manage_plans, FileTypeListView
- visuals.py: add_visual, add_default_visual, add_auto_visual, manage_visuals
- visual_edit.py: edit_visual, delete_visual
- visual_plot.py: plot_visual, plot_visual_new_25
- visual_parts.py: manage_swimlanes_for_visual, manage_timelines_for_visual, create_milestone_swimlane, swimlane_actions
- styling.py: manage_colors, manage_plotable_styles
- content.py: StaticPageView
- auth.py: register, CustomLoginView

Models (split by entity):
- plan.py: Plan, PlanActivity, and plan-centric helpers
- visual.py: PlanVisual, VisualActivity, SwimlaneForVisual, TimelineForVisual
- styling.py: Color, Font, PlotableStyle
- content.py: StaticContent, HelpText
- users.py: CustomUser or user-profile extensions (optional for later)

Admin (split mirroring models):
- plans.py: Plan*, PlanActivity admin
- visuals.py: PlanVisual*, VisualActivity, SwimlaneForVisual, TimelineForVisual admin
- styling.py: Color, Font, PlotableStyle admin
- content.py: StaticContent, HelpText admin
- users.py: Custom user admin (if applicable)

Forms (split by feature):
- plans.py: PlanForm, ReUploadPlanForm
- visuals.py: VisualFormForAdd, VisualFormForEdit, VisualSwimlaneFormForEdit, VisualTimelineFormForEdit
- styling.py: ColorForm, PlotableStyleForm, SwimlaneDropdownForm
- auth.py: CustomUserCreationForm, CustomLoginForm


## Re-exports for compatibility (key for non-breaking phase)

- plan_visual_django/views/__init__.py:
  - from .plans import (manage_plans, add_plan, re_upload_plan, delete_plan, FileTypeListView)
  - from .visuals import (manage_visuals, add_visual, add_default_visual, add_auto_visual)
  - from .visual_edit import (edit_visual, delete_visual)
  - from .visual_plot import (plot_visual, plot_visual_new_25)
  - from .visual_parts import (manage_swimlanes_for_visual, manage_timelines_for_visual, create_milestone_swimlane, swimlane_actions)
  - from .styling import (manage_colors, manage_plotable_styles)
  - from .content import (StaticPageView,)
  - from .auth import (register, CustomLoginView)

- plan_visual_django/models/__init__.py:
  - from .plan import Plan, PlanActivity
  - from .visual import PlanVisual, VisualActivity, SwimlaneForVisual, TimelineForVisual
  - from .styling import Color, Font, PlotableStyle
  - from .content import StaticContent, HelpText

- plan_visual_django/admin/__init__.py:
  - Re-export ModelAdmins so admin site registration continues to work if other modules import from plan_visual_django.admin


## Templates and static organization alignment

- templates/
  - plans/*.html
  - visuals/*.html
  - styling/*.html
  - content/*.html
- static/plan_visual_django/
  - plans/*
  - visuals/*
  - styling/*
  - content/*

Keep current paths intact. Move gradually, updating Django TEMPLATES['DIRS'] or app template directories only when necessary. Use include templates patterns to ensure reusability.


## Settings

- Consider a settings/ package for environment-specific settings (later):
  - settings/__init__.py -> loads from BASE by default
  - settings/base.py
  - settings/dev.py, settings/prod.py
- Keep existing settings for now. Defer until after view/model/admin split is completed.


## Tests

- tests/
  - plans/
  - visuals/
  - styling/
  - content/
  - auth/
- Start by moving or adding unit tests for services (auto_layout, plan parsing) to reduce regression risk during refactor.


## Phased migration plan with rollback safety

Phase 0: Preparation
- Add this document. Communicate plan and constraints.

Phase 1: Views split (no behavior changes)
- Create plan_visual_django/views/ package modules.
- Move view functions/classes; re-export via views/__init__.py.
- Verify urls.py still imports from plan_visual_django.views (no changes needed).

Phase 2: Admin split
- Create plan_visual_django/admin/ package modules; move registrations; re-export in admin/__init__.py.

Phase 3: Forms split
- Create plan_visual_django/forms/ modules per feature; update imports within views modules only; re-export in forms/__init__.py.

Phase 4: Models split
- Create plan_visual_django/models/ package; split classes; update imports within the app; maintain models/__init__.py re-exports so external imports stay stable.
- No DB schema changes; model class names remain identical; only file locations change.

Phase 5: Templates and static alignment (optional, incremental)
- Move templates and static assets into feature folders; update template references gradually.

Rollback:
- Because we re-export from __init__.py in each package, rolling back is as simple as moving the files back or restoring from VCS; import paths and URLs never changed during the process.


## Quick wins you can do immediately (zero risk)

- Add module-level loggers consistently with logger = logging.getLogger(__name__)
- Remove unused imports in oversized modules
- Add type hints to public functions in services
- Centralize small repository helpers (e.g., get_visual, get_visual_activity)
- Document any ambiguous parameter semantics (e.g., swimlane id vs sequence) in docstrings


## Non-goals for now
- Do not change URL paths or names
- Do not change API signatures consumed by templates
- Do not change DB schema


## Example: views package layout and re-export stub

plan_visual_django/views/__init__.py (first commit during Phase 1):

"""Re-export views to keep existing imports working during the transition."""
from .plans import (manage_plans, add_plan, re_upload_plan, delete_plan, FileTypeListView)
from .visuals import (manage_visuals, add_visual, add_default_visual, add_auto_visual)
from .visual_edit import (edit_visual, delete_visual)
from .visual_plot import (plot_visual, plot_visual_new_25)
from .visual_parts import (manage_swimlanes_for_visual, manage_timelines_for_visual, create_milestone_swimlane, swimlane_actions)
from .styling import (manage_colors, manage_plotable_styles)
from .content import (StaticPageView,)
from .auth import (register, CustomLoginView)


This plan ensures a clear, incremental path to a cleaner, more maintainable codebase without breaking routes or existing behaviors.