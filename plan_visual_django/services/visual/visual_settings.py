class VisualSettings:
    """
    Holds key information about the visual which is required to physically plot it.

    Most of this will come from the VisualActivity object, but some will be hard-coded or calculated.
    """

    def __init__(self, visual_id: int):
        self.visual_id = visual_id
        from plan_visual_django.models import PlanVisual
        self.visual = PlanVisual.objects.get(id=visual_id)

        self.width: float = self.visual.width
        self.height: float = self.visual.max_height
        self.track_height: float = self.visual.track_height
        self.track_gap: float = self.visual.track_gap
        self.milestone_width = self.visual.milestone_width
        self.swimlane_gap: float = self.visual.swimlane_gap

        self.default_milestone_shape = self.visual.default_milestone_shape
        self.default_activity_shape = self.visual.default_activity_shape
        self.default_activity_plotable_style = self.visual.default_activity_plotable_style
        self.default_milestone_plotable_style = self.visual.default_milestone_plotable_style
        self.default_swimlane_plotable_style = self.visual.default_swimlane_plotable_style

class VisualSettingsCanvas(VisualSettings):
    """
    Sub class of VisualSettings which generates a set of settings for the visual which are specific to
    plotting the visual on a canvas.
    """
    def __init__(self, visual_id):
        """
        No canvas specific settings for now - will probably add some related to canvas element properties
        :param visual_id:
        """
        super().__init__(visual_id)
