from __future__ import annotations
from plan_visual_django.models import PlanActivity, Plan, CustomUser
from plan_visual_django.services.plan_file_utilities.plan_tree import PlanTree, PlanActivityTreeNode
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple, Iterable
import statistics
from django.test import TestCase

"""
Initial visual layout algorithm for project plans.
Python 3.12 implementation based on the agreed specification.

Key features
- Swimlanes: top-level WBS nodes (level==1), ≤5 total with a dedicated top "Milestones" lane.
- Coarsening: replace dense sibling sets by their parent to fit ≤8 content tracks per lane; allow overflow as last resort.
- Track packing: interval partitioning per lane with deterministic sorting and parent/sibling affinity.
- Label side: left/right decided by bar center vs timeline midpoint.
- Deterministic & stable across runs.

Public API
- build_initial_layout(activities: list[Activity], options: LayoutOptions) -> dict

Run tests:
    python -m unittest auto_layout.py
"""


# -----------------------------
# Data models
# -----------------------------

@dataclass(frozen=True)
class xxxActivityForAutoLayout:
    id: str
    name: str
    start: date
    end: date
    is_milestone: bool
    level: int
    parent_id: Optional[str]  # None for root(s)

    def duration_days_inclusive(self) -> int:
        """Inclusive duration in days. Minimum 1 day for layout semantics."""
        d = (self.end - self.start).days + 1
        return max(1, d)

def interval(self) -> Tuple[date, date]:
    """Return [start, end_exclusive) interval for non-overlap checks.
    Guarantees at least 1 day width.
    """
    end_excl = self.end + timedelta(days=1)
    if end_excl <= self.start:
        # Zero/negative -> inflate to 1 day wide starting at start
        end_excl = self.start + timedelta(days=1)
    return (self.start, end_excl)


@dataclass
class LayoutOptions:
    max_lanes: int = 5                     # includes Milestones lane
    max_tracks_per_lane: int = 8           # content tracks 1..8; track 0 reserved
    reserve_track_zero: bool = True
    milestones_lane_name: str = "Milestones"
    label_window_start: Optional[date] = None  # for label side heuristic
    label_window_end: Optional[date] = None


# -----------------------------
# Internal helpers
# -----------------------------

# @dataclass
# class TreeNode:
#     act: ActivityForAutoLayout
#     children: List["TreeNode"] = field(default_factory=list)
#
#
# def build_tree(activities: List[ActivityForAutoLayout]) -> Tuple[Dict[str, TreeNode], List[TreeNode]]:
#     nodes: Dict[str, TreeNode] = {a.id: TreeNode(a) for a in activities}
#     roots: List[TreeNode] = []
#     for n in nodes.values():
#         pid = n.act.parent_id
#         if pid and pid in nodes:
#             nodes[pid].children.append(n)
#         else:
#             roots.append(n)
#     # Ensure deterministic child order (by start, -duration, name, id)
#     for n in nodes.values():
#         n.children.sort(key=lambda c: (
#             c.act.start,
#             -c.act.duration_days_inclusive(),
#             c.act.name.lower(),
#             c.act.id,
#         ))
#     # Also sort roots deterministically
#     roots.sort(key=lambda c: (
#         c.act.start,
#         -c.act.duration_days_inclusive(),
#         c.act.name.lower(),
#         c.act.id,
#     ))
#     return nodes, roots


# def collect_top_level(nodes: Dict[str, TreeNode], roots: List[TreeNode]) -> List[TreeNode]:
#     """Top-level WBS nodes are level==1 items as per spec.
#     Fallback: if no level==1, treat immediate children of roots as top-level.
#     """
#     tops = [n for n in nodes.values() if n.act.level == 1]
#     if not tops:
#         # Fallback: next level under root(s)
#         for r in roots:
#             tops.extend(r.children)
#     # Deduplicate and sort deterministically
#     seen = set()
#     uniq: List[TreeNode] = []
#     for n in tops:
#         if n.act.id not in seen:
#             seen.add(n.act.id)
#             uniq.append(n)
#     uniq.sort(key=lambda c: (
#         c.act.start,
#         -c.act.duration_days_inclusive(),
#         c.act.name.lower(),
#         c.act.id,
#     ))
#     return uniq


def iter_subtree(node: PlanActivityTreeNode) -> Iterable[PlanActivityTreeNode]:
    yield node
    for ch in node.children:
        yield from iter_subtree(ch)


def iter_leaves(node: PlanActivityTreeNode) -> Iterable[PlanActivityTreeNode]:
    if not node.children:
        yield node
    else:
        for ch in node.children:
            yield from iter_leaves(ch)


# -----------------------------
# Lane selection and ordering
# -----------------------------

def importance_score_for_lane(top_nodes: List[PlanActivityTreeNode]) -> int:
    """Score by total active days of initial selection (leaves under top_nodes).
    Milestones are counted as 1 but are excluded from non-milestone lanes later; the score ignores that lane separation by design.
    """
    total = 0
    for t in top_nodes:
        for leaf in iter_leaves(t):
            a: PlanActivity = leaf.activity
            # count all leaves; treat milestone as 1 day
            total += 1 if a.milestone_flag else a.duration
    return total


def split_into_primary_and_other(top_levels: List[PlanActivityTreeNode], options: LayoutOptions) -> List[Tuple[str, List[PlanActivityTreeNode]]]:
    """Return a list of (lane_name, top_nodes) excluding the Milestones lane.
    Keep up to 4 individual lanes (since Milestones takes 1, total ≤5). Merge the rest into "Other".
    """
    if not top_levels:
        return [("Other", [])]

    # Compute scores per single top node
    scored = [(n, importance_score_for_lane([n])) for n in top_levels]
    scored.sort(key=lambda x: (-x[1], x[0].activity.start_date, x[0].name.lower(), x[0].id))

    max_individual = max(0, options.max_lanes - 1)  # minus Milestones
    if len(scored) <= max_individual:
        lanes = [(n.name, [n]) for (n, _s) in scored]
        return lanes

    # Keep top (max_individual - 0) but ensure at most 4 (given spec says top 4)
    keep = min(4, max_individual)
    primary = scored[:keep]
    other_nodes = [n for (n, _s) in scored[keep:]]
    lanes: List[Tuple[str, List[PlanActivityTreeNode]]] = [(n.name, [n]) for (n, _s) in primary]
    lanes.append(("Other", other_nodes))
    return lanes


def median_start_date_of_members(members: List[PlanActivity]) -> date:
    if not members:
        return date.min
    ordinals = sorted([a.start_date.toordinal() for a in members])
    med = statistics.median(ordinals)
    # statistics.median may return float for even counts; round to nearest int deterministically
    return date.fromordinal(round(med))


# -----------------------------
# Selection and coarsening
# -----------------------------

@dataclass(frozen=True)
class Plannable:
    """A selected item to place: either an Activity (bar) or a promoted parent (treated as its Activity)."""
    act_node: PlanActivityTreeNode


@dataclass
class CoarsenRecord:
    parent_id: str
    replaced_children: List[str]


def initial_selection_for_lane(top_nodes: List[PlanActivityTreeNode]) -> List[Plannable]:
    sel: List[Plannable] = []
    for t in top_nodes:
        for leaf in iter_leaves(t):
            plan_activity = leaf.activity
            if plan_activity.milestone_flag:
                continue  # milestones will go to the Milestones lane
            sel.append(Plannable(leaf))
    # Deterministic order
    sel.sort(key=lambda p: (
        p.act_node.activity.start_date,
        -p.act_node.activity.duration,
        p.act_node.name.lower(),
        p.act_node.id,
    ))
    return sel

def promotable(node):
    return (
        node is not None
        and isinstance(node, PlanActivityTreeNode)   # excludes the anytree root
        and getattr(node, "activity", None) is not None  # must be drawable
    )

def coarsen_until_fits(top_nodes: List[PlanActivityTreeNode], selection: List[Plannable], max_tracks: int,
                        coarsen_log: List[CoarsenRecord]) -> List[Plannable]:
    """Greedy coarsening: iteratively replace densest sibling clusters with their parent until packing fits.
    Returns the final selection (list of Plannable).
    """
    # Build helper maps
    by_id: Dict[str, PlanActivityTreeNode] = {n.id: n for t in top_nodes for n in iter_subtree(t)}

    current: List[Plannable] = list(selection)

    while True:
        tracks_needed = measure_tracks_needed(current)
        if tracks_needed <= max_tracks:
            return current
        # Identify sibling clusters that exist in current selection
        clusters: List[Tuple[PlanActivityTreeNode, List[PlanActivityTreeNode]]] = []  # (parent, children_present)
        present_ids = {p.act_node.id for p in current}
        # Consider parents that have ≥2 children present; more impact when coarsened
        considered_parents: set[str] = set()
        for p in current:
            parent_node = p.act_node.parent

            # If we are at the top of the tree we don't want to go any further
            if not promotable(parent_node):
                continue

            children_present = [ch for ch in parent_node.children if ch.id in present_ids]
            if len(children_present) >= 1:
                clusters.append((parent_node, children_present))
                considered_parents.add(parent_node.id)

        if not clusters:
            # Try promoting a single deepest item: pick the earliest-starting item's parent if exists
            candidates = [by_id.get(p.act_node.parent) for p in current if p.act_node.parent.id in by_id]
            candidates = [c for c in candidates if c is not None]
            if not candidates:
                return current  # cannot coarsen further
            # Pick deterministically
            parent_node = sorted(candidates, key=lambda n: (
                n.act_node.activity.start_date,
                -n.act_node.duration,
                n.act_node.name.lower(),
                n.act_node.id,
            ))[0]
            children_present = [ch for ch in parent_node.children if ch.act_node.id in present_ids]
            clusters = [(parent_node, children_present)]

        # Score clusters by overlap pressure
        def cluster_score(item: Tuple[PlanActivityTreeNode, List[PlanActivityTreeNode]]) -> Tuple:
            parent: PlanActivityTreeNode
            children: List[PlanActivityTreeNode]

            parent, children = item
            total_days = sum(max(1, (c.activity.end_date - c.activity.start_date).days + 1) for c in children)
            # Overlap proxy: number of pairwise overlaps among children
            overlaps = 0
            child_intervals = [(c.activity.start_date, c.activity.end_date + timedelta(days=1)) for c in children]
            for i in range(len(child_intervals)):
                for j in range(i+1, len(child_intervals)):
                    a1, b1 = child_intervals[i]
                    a2, b2 = child_intervals[j]
                    if not (b1 <= a2 or b2 <= a1):
                        overlaps += 1
            return (
                -(total_days * (1 + overlaps)),  # higher first
                parent.activity.start_date,
                -parent.activity.duration,
                parent.name.lower(),
                parent.activity.id,
            )

        clusters.sort(key=cluster_score)
        best_parent, present_children = clusters[0]

        # Replace children with parent in current selection
        new_current: List[Plannable] = []
        replaced_ids: List[str] = []
        present_child_ids = {c.id for c in present_children}
        for p in current:
            if p.act_node.id in present_child_ids:
                replaced_ids.append(p.act_node.id)
                continue
            new_current.append(p)
        if best_parent.id not in {p.act_node.id for p in new_current}:
            new_current.append(Plannable(best_parent))
        # Log coarsen
        coarsen_log.append(CoarsenRecord(parent_id=best_parent.id, replaced_children=sorted(replaced_ids)))
        # Deterministic order
        new_current.sort(key=lambda p: (
            p.act_node.activity.start_date,
            -p.act_node.activity.duration,
            p.act_node.name.lower(),
            p.act_node.id,
        ))
        current = new_current


# -----------------------------
# Packing (interval partitioning with affinity)
# -----------------------------

@dataclass
class Placement:
    activity_id: str
    activity: PlanActivity
    start: date
    end: date
    track_index: int
    label_side: str


def measure_tracks_needed(plannables: List[Plannable]) -> int:
    """Greedy interval partitioning to count needed tracks (no affinity)."""
    # Each track keeps the earliest time it becomes free
    free_at: List[date] = []  # per track index (content tracks starting at 1 conceptually)
    # Sort deterministically
    ordered = sorted(plannables, key=lambda p: (
        p.act_node.activity.start_date,
        -p.act_node.activity.duration,
        p.act_node.name.lower(),
        p.act_node.id,
    ))
    for p in ordered:
        s, e_excl = p.act_node.activity.interval()
        # Find first track with free_at <= s
        placed = False
        for i in range(len(free_at)):
            if free_at[i] <= s:
                free_at[i] = e_excl
                placed = True
                break
        if not placed:
            free_at.append(e_excl)
    return len(free_at)


def pack_with_affinity(plannables: List[Plannable], label_midpoint: Optional[date]) -> Tuple[List[List[Placement]], int]:
    """Return tracks (index 1..N as list indices 0..N-1) and tracks_used.
    Track 0 (header) is NOT included here; caller can insert a None at index 0.
    """
    # Sort deterministically
    ordered = sorted(plannables, key=lambda p: (
        p.act_node.activity.start_date,
        -p.act_node.activity.duration,
        p.act_node.name.lower(),
        p.act_node.id,
    ))
    # Track availability and last used by parent affinity
    free_at: List[date] = []
    assignments: List[List[Placement]] = []
    parent_to_tracks: Dict[Optional[str], List[int]] = {}

    def label_side_for(act: PlanActivity) -> str:
        if not label_midpoint:
            return "left"
        start, end_excl = act.interval()
        # Center of bar in ordinal space
        center_ord = (start.toordinal() + (end_excl - timedelta(days=1)).toordinal()) / 2
        return "left" if center_ord <= label_midpoint.toordinal() else "right"

    for p in ordered:
        s, e_excl = p.act_node.activity.interval()
        # Find all free tracks
        free_tracks = [idx for idx, t in enumerate(free_at) if t <= s]
        chosen_idx: Optional[int] = None
        # Affinity: prefer a track previously used by this parent
        par = p.act_node.parent.id
        preferred = parent_to_tracks.get(par, [])
        preferred_free = [i for i in preferred if i in free_tracks]
        if preferred_free:
            # choose closest to the smallest preferred index (keeps siblings tight)
            base = min(preferred)
            chosen_idx = min(preferred_free, key=lambda i: abs(i - base))
        elif free_tracks:
            chosen_idx = min(free_tracks)
        else:
            # Need a new track
            chosen_idx = len(free_at)
            free_at.append(date.min)  # placeholder; will set below
            assignments.append([])
        # Ensure assignments list long enough
        while len(assignments) <= chosen_idx:
            assignments.append([])
            free_at.append(date.min)
        # Place
        free_at[chosen_idx] = e_excl
        label_side = label_side_for(p.act_node.activity)
        placement = Placement(
            activity_id=p.act_node.id,
            activity=p.act_node.activity,
            start=p.act_node.activity.start_date,
            end=p.act_node.activity.end_date,
            track_index=chosen_idx + 1,  # content tracks start at 1
            label_side=label_side,
        )
        assignments[chosen_idx].append(placement)
        # Update affinity
        parent_to_tracks.setdefault(par, [])
        if chosen_idx not in parent_to_tracks[par]:
            parent_to_tracks[par].append(chosen_idx)

    tracks_used = len(assignments)
    return assignments, tracks_used


# -----------------------------
# Main entry point
# -----------------------------

def build_initial_layout(plan_tree: PlanTree, options: Optional[LayoutOptions] = None) -> dict:
    activity_nodes = plan_tree.get_node_list()
    options = options or LayoutOptions()

    # Split milestones vs others; also catch zero-duration items as milestones
    milestones: List[PlanActivityTreeNode] = []
    non_milestones: List[PlanActivityTreeNode] = []
    for a in plan_tree.get_node_list():
        if a.activity.milestone_flag:
            milestones.append(a)
        else:
            non_milestones.append(a)

    # Lanes (excluding milestones) built from top-levels
    top_levels = plan_tree.get_plan_tree_child_nodes_by_unique_id(plan_tree.get_root().id)
    lane_defs = split_into_primary_and_other(top_levels, options)  # List[(name, [top_nodes])]

    def lane_members_from_top_nodes(top_nodes: List[PlanActivityTreeNode]) -> List[PlanActivity]:
        seen: set[str] = set()
        members: List[PlanActivity] = []
        for t in top_nodes:
            for n in iter_subtree(t):
                if n.id in seen:
                    continue
                seen.add(n.id)
                members.append(n.activity)
        return members

    # Label midpoint (timeline midpoint) for label side heuristic
    # If not provided, compute across ALL activities by min start and max end
    if options.label_window_start and options.label_window_end:
        label_mid = options.label_window_start + (options.label_window_end - options.label_window_start) / 2
        if isinstance(label_mid, timedelta):  # type: ignore[unreachable]
            label_mid = options.label_window_start  # safety
    else:
        if activity_nodes:
            min_start = min(a.activity.start_date for a in activity_nodes)
            max_end = max(a.activity.end_date for a in activity_nodes)
            label_mid = min_start + (max_end - min_start) / 2  # type: ignore[operator]
        else:
            label_mid = None

    # Build Milestones lane first
    lanes_out: List[dict] = []
    # Pack milestones: treat width as at least 1 day via Activity.interval()
    milestones_plannables = [Plannable(a) for a in milestones]
    ms_tracks, ms_tracks_used = pack_with_affinity(milestones_plannables, label_mid)
    ms_tracks_list: List[Optional[List[dict]]] = [None] if options.reserve_track_zero else []
    for idx, track in enumerate(ms_tracks, start=1):
        ms_tracks_list.append([
            {
                "activity_id": pl.activity_id,
                "activity": pl.activity,
                "start": pl.start.isoformat(),
                "end": pl.end.isoformat(),
                "track_index": idx,
                "label_side": pl.label_side,
            }
            for pl in track
        ])
    lanes_out.append({
        "lane_id": options.milestones_lane_name,
        "name": options.milestones_lane_name,
        "is_milestones_lane": True,
        "order_index": 0,
        "max_tracks": options.max_tracks_per_lane,
        "overflow": ms_tracks_used > options.max_tracks_per_lane,
        "tracks_used": ms_tracks_used,
        "tracks": ms_tracks_list,
    })

    # Build non-milestone lanes
    lane_entries: List[Tuple[str, List[PlanActivityTreeNode]]] = lane_defs

    # Order lanes (after milestones) by median start of *selected* members
    ordered_lane_entries: List[Tuple[str, List[PlanActivityTreeNode], date, List[Plannable]]] = []
    for name, top_nodes in lane_entries:
        # Initial selection (leaves)
        selection = initial_selection_for_lane(top_nodes)
        # Median start based on member activities (all nodes under top_nodes)
        members = lane_members_from_top_nodes(top_nodes)
        med = median_start_date_of_members(members)
        ordered_lane_entries.append((name, top_nodes, med, selection))

    ordered_lane_entries.sort(key=lambda t: (t[2], t[0].lower()))

    notes_excluded: List[str] = []
    coarsen_records: List[CoarsenRecord] = []

    order_idx = 1  # 0 is milestones
    for name, top_nodes, _med, selection in ordered_lane_entries:
        # Drop items with missing dates (shouldn't happen with our dataclass, but keep hook)
        sel = [p for p in selection if p.act_node.activity.start_date and p.act_node.activity.end_date]
        missing = [p.act_node.id for p in selection if not (p.act_node.activity.start_date and p.act_node.activity.end_date)]
        notes_excluded.extend(missing)

        # Coarsen to fit
        final_sel = coarsen_until_fits(top_nodes, sel, options.max_tracks_per_lane, coarsen_records)
        # Pack with affinity
        tracks, used = pack_with_affinity(final_sel, label_mid)
        # Build tracks list with reserved header
        tracks_list: List[Optional[List[dict]]] = [None] if options.reserve_track_zero else []
        for idx, track in enumerate(tracks, start=1):
            tracks_list.append([
                {
                    "activity_id": pl.activity_id,
                    "activity": pl.activity,
                    "start": pl.start.isoformat(),
                    "end": pl.end.isoformat(),
                    "track_index": pl.track_index,
                    "label_side": pl.label_side,
                }
                for pl in track
            ])
        lanes_out.append({
            "lane_id": name,
            "name": name,
            "is_milestones_lane": False,
            "order_index": order_idx,
            "max_tracks": options.max_tracks_per_lane,
            "overflow": used > options.max_tracks_per_lane,
            "tracks_used": used,
            "tracks": tracks_list,
        })
        order_idx += 1

    layout = {
        "lanes": lanes_out,
        "notes": {
            "excluded_missing_dates": notes_excluded,
            "coarsened": [
                {"parent_id": r.parent_id, "replaced_children": r.replaced_children}
                for r in coarsen_records
            ],
        },
    }
    return layout


# -----------------------------
# Example tests (golden-ish)
# -----------------------------

class LayoutTests(TestCase):
    def setUp(self):
        # Build a small synthetic tree with two top-levels and some overlaps
        d = date
        user = CustomUser.objects.create(
            email="<EMAIL>",
            username="testuser"
        )
        self.plan = Plan.objects.create(
            user=user,
            plan_name="",
            file_name="",
            file="",
            file_type_name="",
            session_id=""
        )
        # PlanActivity.objects.create(plan=self.plan,unique_sticky_activity_id="P", activity_name="Program", start_date=d(2025, 1, 1), end_date=d(2025, 12, 31), milestone_flag=False, level=0),
        PlanActivity.objects.create(plan=self.plan,unique_sticky_activity_id="A", activity_name="Alpha", start_date=d(2025, 1, 1), end_date=d(2025, 6, 30), milestone_flag=False, level=1),
        PlanActivity.objects.create(plan=self.plan,unique_sticky_activity_id="A1", activity_name="Alpha-Design", start_date=d(2025, 1, 1), end_date=d(2025, 2, 15), milestone_flag=False, level=2),
        PlanActivity.objects.create(plan=self.plan,unique_sticky_activity_id="A2", activity_name="Alpha-Build", start_date=d(2025, 2, 1), end_date=d(2025, 5, 31), milestone_flag=False, level=2),
        PlanActivity.objects.create(plan=self.plan,unique_sticky_activity_id="A3", activity_name="Alpha-Test",start_date=d(2025, 6, 1), end_date=d(2025, 6, 30), milestone_flag=False, level=2),
        PlanActivity.objects.create(plan=self.plan,unique_sticky_activity_id="AM1", activity_name="Alpha-M1",start_date=d(2025, 3, 1), end_date=d(2025, 3, 1), milestone_flag=True, level=3),
        PlanActivity.objects.create(plan=self.plan,unique_sticky_activity_id="B", activity_name="Beta", start_date=d(2025, 3, 1), end_date=d(2025, 12, 15), milestone_flag=False, level=1),
        PlanActivity.objects.create(plan=self.plan,unique_sticky_activity_id="B1", activity_name="Beta-Design",start_date=d(2025, 3, 1), end_date=d(2025, 4, 15), milestone_flag=False, level=2),
        PlanActivity.objects.create(plan=self.plan,unique_sticky_activity_id="B2", activity_name="Beta-Build",start_date=d(2025, 4, 1), end_date=d(2025, 9, 30), milestone_flag=False, level=2),
        PlanActivity.objects.create(plan=self.plan,unique_sticky_activity_id="B3", activity_name="Beta-Test",start_date=d(2025, 10, 1), end_date=d(2025, 12, 15), milestone_flag=False, level=2),
        PlanActivity.objects.create(plan=self.plan,unique_sticky_activity_id="BM1", activity_name="Beta-M1",start_date=d(2025, 7, 1), end_date=d(2025, 7, 1), milestone_flag=True, level=3),
        PlanActivity.objects.create(plan=self.plan,unique_sticky_activity_id="Z0", activity_name="Zero", start_date=d(2025, 5, 10), end_date=d(2025, 5, 10), milestone_flag=False, level=2),  # zero-duration but not flagged
        self.plan_tree = self.plan.get_plan_tree()

    def test_build_layout(self):
        lay = build_initial_layout(self.plan_tree, LayoutOptions())
        # Milestones lane is top
        self.assertEqual(lay["lanes"][0]["is_milestones_lane"], True)
        self.assertEqual(lay["lanes"][0]["name"], "Milestones")
        # There should be tracks with placements for milestones (AM1, BM1, Z0 as milestone-equivalent)
        milestone_ids = {pl["activity_id"] for track in lay["lanes"][0]["tracks"] if track for pl in track}
        self.assertTrue({"AM1", "BM1", "Z0"}.issubset(milestone_ids))
        # Non-milestone lanes present (Alpha and Beta or Beta may be ordered by median start)
        lane_names = [ln["name"] for ln in lay["lanes"][1:]]
        self.assertIn("Alpha", lane_names)
        self.assertIn("Beta", lane_names)
        # Track 0 reserved
        for lane in lay["lanes"]:
            self.assertIsNone(lane["tracks"][0])
        # No overlaps within tracks (sanity check)
        for lane in lay["lanes"]:
            for idx, track in enumerate(lane["tracks"][1:], start=1):
                if not track:
                    continue
                ints = [(
                    date.fromisoformat(p["start"]),
                    date.fromisoformat(p["end"]) + timedelta(days=1)
                ) for p in track]
                for i in range(len(ints)):
                    for j in range(i+1, len(ints)):
                        a1, b1 = ints[i]
                        a2, b2 = ints[j]
                        self.assertTrue(b1 <= a2 or b2 <= a1, f"overlap in lane {lane['name']} track {idx}")

    def test_coarsening_does_not_crash(self):
        # Inflate overlap by adding many siblings to Alpha
        d = date
        for i in range(10):
            PlanActivity.objects.create(plan=self.plan, unique_sticky_activity_id=f"A2x{i}", activity_name=f"Alpha-Extra-{i}", start_date=d(2025, 2, 1), end_date=d(2025, 5, 15), milestone_flag=False, level=2)
        self.plan_tree_for_coarsening_test = self.plan.get_plan_tree()

        lay = build_initial_layout(self.plan_tree, LayoutOptions(max_tracks_per_lane=8))
        # Alpha lane should exist and not overflow too much (might still overflow if impossible)
        alpha_lane = next(l for l in lay["lanes"] if l["name"] == "Alpha")
        self.assertIn("overflow", alpha_lane)

