# Python Code Review and Recommendations

This document provides a focused review of the current Python codebase with actionable recommendations to improve structure, reusability, and readability. The suggestions are prioritized to enable incremental adoption with minimal risk.

Scope examined (representative, not exhaustive):
- api/v1/model/visual/activity/views.py
- api/v1/model/visual/activity/urls.py
- plan_visual_django/services/visual/model/auto_layout.py
- plan_visual_django/services/visual/model/layout.py
- plan_visual_django/services/plan_file_utilities/plan_tree.py
- plan_visual_django/services/plan_file_utilities/plan_field.py
- plan_visual_django/services/initialisation/db_initialisation.py
- plan_visual_django/services/service_utilities/service_response.py


## Top Priority (P1): API structure, consistency, and error handling

1. Standardize DRF patterns in views
   - Use DRF Response and status consistently rather than mixing JsonResponse and Response.
   - Prefer DRF exceptions (NotFound, ValidationError, PermissionDenied) with exception handlers, instead of manual try/except returning Response.
   - Consider ViewSets + Routers for CRUD-like endpoints to reduce boilerplate and enforce conventions.

   Example refactor (views):
   - Replace manual fetch + 404 with get_object_or_404 or raising NotFound.
   - Replace JsonResponse(serializer.data) with Response(serializer.data).

2. Consistent response schema and service layer integration
   - You have a good ServiceResponse and ServiceStatusCode type—use it consistently in service methods and translate to HTTP status codes in a single helper.
   - Add a small mapping function:
     def http_status_from_service(status: ServiceStatusCode) -> int: ...
   - Ensure views return Response({"status": status.as_dict(), "message": str, "data": {...}}) for operations, and plain data for GET list/detail.

3. Clarify “swimlane id vs sequence number” semantics
   - Currently, PUT uses swimlane sequence numbers; PATCH uses swimlane id. This is confusing and increases risk of misuse.
   - Recommendation:
     - Split endpoints or paths explicitly: use /swimlanes/by-sequence/{n} vs /swimlanes/{id}.
     - Or to keep URL clean: accept a single concept, preferably swimlane id everywhere. Compute sequence elsewhere.
     - Document this in the API (docstring + README/API.md).

4. Idempotency and method semantics
   - PUT with no body (ModelVisualActivityAPI.put) is unconventional. Either:
     - Use POST for add-and-place operations, or
     - Accept a body with required parameters and make PUT idempotent on the resource (clear definition of resource).

5. URL param validation
   - Enforce data types via path converters (already partly used) and add serializer validation for inputs (e.g., swimlane value range).


## High Priority (P2): Reusability and duplication reduction

6. Introduce small repository/helpers layer for common lookups
   - Common patterns exist: fetching PlanVisual, fetching VisualActivity by visual + unique id, verifying visual_id matches.
   - Centralize in api/common/db_access.py or services/repositories.py:
     - get_visual(visual_id) -> PlanVisual
     - get_visual_activity(visual_id, unique_id_from_plan) -> VisualActivity
     - validate_activity_belongs_to_visual(activity_id, visual_id) -> None/raise
   - Benefits: consistent errors, single place for select_related/prefetch/annotations.

7. Serializer reuse for updates
   - You already have ModelVisualActivitySerialiserForUpdate; standardize all write paths to go through write-serializers with explicit writable fields.
   - Add ModelVisualActivityMoveSerializer with fields {swimlane_id} or {swimlane_sequence} and validate semantics there.

8. Service boundaries
   - VisualLayoutManager is a good start. Continue to move business logic out of views (e.g., adjusting tracks, enabling/disabling) into service class methods with clear inputs/outputs returning ServiceResponse.


## Medium Priority (P3): Readability, typing, and safeguards

9. Type hints and docstrings
   - Add return types on public functions/methods, especially service methods and utility functions.
   - Ensure docstrings specify what is returned and whether objects are saved or just mutated (e.g., adjust_visual_activity_track does not save; callsite must save).

10. Logging consistency
   - Use module-level loggers with __name__ as done in db_initialisation. Replace print or comments with logger.debug/info/warning.
   - In views, log key operations and errors with context (visual_id, activity ids).

11. Edge case handling and explicit returns
   - adjust_visual_activity_track silently logs when a swimlane does not exist. Consider returning a boolean or raising a domain-specific exception so callers can decide an HTTP status (e.g., 400 for invalid swimlane id).
   - In plan_tree.PlanTree, _get_node_for_id returns None when not found; callers like get_plan_tree_activity_by_unique_id should handle and raise a clear error instead of attribute errors.

12. Remove unused imports and constants
   - api/v1/model/visual/activity/views.py: Max, default constants (DEFAULT_HEIGHT_IN_TRACKS, DEFAULT_TEXT_*), and some serializers may be unused in certain methods.
   - Keep imports tight to improve readability and static analysis.

13. Naming clarity
   - activity_unique_id vs unique_id is inconsistent across endpoints. Choose one name consistently.
   - swimlane param: name should indicate id vs sequence clearly (e.g., swimlane_id, swimlane_seq).


## Lower Priority (P4): Structure and modularity

14. Dispatchers vs explicit methods
   - VisualActivityViewDispatcher and ModelVisualActivitySwimlaneDispatcher custom dispatch adds complexity and hides API surface. Consider using ViewSets with @action routes or separate views with clear names.

15. Tests: add unit tests for services
   - Target VisualLayoutManager.add_activity_to_swimlane and add_subactivities with mocked models or a small test DB to assert track placement logic and edge cases.

16. Configuration and initialization
   - db_initialisation: Extract environment reading/validation into a small config object (pydantic or dataclasses). Validate presence of SHARED_USER_NAME, passwords, and email domain with helpful errors.
   - Avoid logging passwords (TODO present). Ensure secrets aren’t printed even temporarily.


## Suggested Micro-Refactors (Safe, incremental)

A. Replace JsonResponse with Response in views where DRF is already used (read endpoints). Example:
- return JsonResponse(response, safe=False) -> return Response(response, status=status.HTTP_200_OK)

B. Add small helper for mapping ServiceStatusCode to HTTP status:

```python
# plan_visual_django/services/service_utilities/http.py
from rest_framework import status as http
from .service_response import ServiceStatusCode

def http_status_from_service(s: ServiceStatusCode) -> int:
    return {
        ServiceStatusCode.SUCCESS: http.HTTP_200_OK,
        ServiceStatusCode.DATA_NOT_FOUND: http.HTTP_404_NOT_FOUND,
        ServiceStatusCode.INVALID_INPUT: http.HTTP_400_BAD_REQUEST,
        ServiceStatusCode.DATA_CONFLICT: http.HTTP_409_CONFLICT,
        ServiceStatusCode.PERMISSION_DENIED: http.HTTP_403_FORBIDDEN,
        ServiceStatusCode.AUTHENTICATION_FAILED: http.HTTP_401_UNAUTHORIZED,
        ServiceStatusCode.SERVICE_UNAVAILABLE: http.HTTP_503_SERVICE_UNAVAILABLE,
        ServiceStatusCode.RESOURCE_LIMIT_REACHED: http.HTTP_429_TOO_MANY_REQUESTS,
    }.get(s, http.HTTP_500_INTERNAL_SERVER_ERROR)
```

Then in views, use:

```python
status_code = http_status_from_service(service_status.status)
return Response({"message": service_status.message}, status=status_code)
```

C. Explicit return value in adjust_visual_activity_track:

```python
def adjust_visual_activity_track(visual_activity, swimlane_id) -> bool:
    try:
        swimlane = SwimlaneForVisual.objects.get(id=swimlane_id)
    except SwimlaneForVisual.DoesNotExist:
        logger.warning(...)
        return False
    new_track = swimlane.get_next_unused_track_number()
    visual_activity.vertical_positioning_value = new_track
    visual_activity.swimlane = swimlane
    return True
```

Callers can check and decide response codes accordingly.

D. plan_tree: guard for None

```python
def get_plan_tree_activity_by_unique_id(self, unique_id: str):
    if self.root is None:
        self._parse_plan_to_tree()
    node = self._get_node_for_id(unique_id)
    if node is None:
        raise ValueError(f"No activity found with id {unique_id}")
    return node.activity
```


## Style and Documentation

- Add module-level docstrings for each service module explaining intent and invariants.
- Ensure serializers specify read_only_fields and writeable fields explicitly; avoid partial=True unless necessary.
- Use isort/black/ruff (or flake8) to standardize formatting and catch simple issues (unused imports, complexity).
- Consider mypy for gradual typing on services and utils.


## Performance Considerations

- Use select_related on VisualActivity queries that reference related swimlane/visual to avoid N+1 in list endpoints.
- If adding multiple activities in a batch, prefer bulk_create / bulk_update where possible with validation done up-front.


## Migration Path / Sequencing

1. Introduce helper utilities (http status mapper, repository getters). No functional change, improves consistency.
2. Update views to use Response and DRF exceptions; keep endpoints and serializers unchanged.
3. Clarify and document swimlane id vs sequence. Optionally add new endpoints while keeping old ones for backward compatibility, with deprecation notes.
4. Tighten typing/docstrings and logging across services; adopt ruff/black for linting/formatting.
5. Add unit tests for service edge cases (swimlane moving, sub-activities addition, plan tree lookups).


## Noted Specifics from Current Files

- views.py
  - Unused imports: Max, DEFAULT_* constants, possibly some serializers in some methods. Clean up.
  - ModelVisualActivityUpdateAPI.patch: returns 400 on not found per-item; consider processing all and returning multi-status, or short-circuit with 207/400 policy documented.
  - delete: uses unique_id vs activity_unique_id naming; align.
  - Transaction use: verify necessity; save inside atomic is fine, but moving save outside loop can reduce overhead if batching.

- layout.adjust_visual_activity_track: recommend explicit return and docstring; callers to check.

- plan_tree: improve None handling and error messaging for missing IDs; add type hints on methods; consider caching results or ensuring deterministic traversal order (ordering of planactivity_set).

- db_initialisation: don’t log passwords; validate env vars; separate data-driver config from logic; handle IntegrityError more precisely (e.g., skip existing with info).

- plan_field.py: Great use of enums; consider docstrings for enums, and factory/helper methods for parsing and validation. Use typing for Any to specific types if known.


---
This document is intended to guide incremental improvements without broad rewrites. Each recommendation can be applied independently to reduce risk while raising overall code quality and maintainability.
