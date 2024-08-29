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

    @staticmethod
    def calculate_defaults_for_visual(plan):
        """
        Encapsulates calculation of default values for a new visual.  May want to make this
        more sophisticated (e.g. allow default values to be stored in the database) but for
        now just have default values defined in a single place in the code.

        :param plan:
        :return:
        """

        from plan_visual_django.models import PlotableShape
        from plan_visual_django.models import PlotableStyle

        num_visuals_for_plan = plan.planvisual_set.count()

        return {
            "name": f"{plan.plan_name}-Visual-{num_visuals_for_plan+1:02d}",
            "width": 1200,
            "max_height": 800,
            "include_title": False,
            "default_activity_shape": PlotableShape.objects.get(name=PlotableShape.PlotableShapeName.RECTANGLE),
            "default_milestone_shape": PlotableShape.objects.get(name=PlotableShape.PlotableShapeName.DIAMOND),
            "track_height": 20,
            "track_gap": 4,
            "milestone_width": 10,
            "swimlane_gap": 5,
            "default_activity_plotable_style": PlotableStyle.objects.get(style_name="[03]Activity Default 1"),
            "default_milestone_plotable_style": PlotableStyle.objects.get(style_name="[01]Milestone Default 1"),
            "default_swimlane_plotable_style": PlotableStyle.objects.get(style_name="[05]Swimlane-odd Default 1"),
        }

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



