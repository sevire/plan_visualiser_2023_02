from plan_visual_django.services.visual.model.plotable_shapes import PlotableShapeName


class VisualSettings:
    """
    Holds key information about the visual which is required to physically plot it.

    Most of this will come from the VisualActivity object, but some will be hard-coded or calculated.
    name

    """

    def __init__(self, visual_id: int):
        self.visual_id = visual_id
        from plan_visual_django.models import PlanVisual
        self.visual: PlanVisual = PlanVisual.objects.get(id=visual_id)

        self.width: float = self.visual.width
        self.max_height: float = self.visual.max_height
        self.track_height: float = self.visual.track_height
        self.track_gap: float = self.visual.track_gap
        self.milestone_width = self.visual.milestone_width
        self.swimlane_gap: float = self.visual.swimlane_gap

        self.default_milestone_shape = self.visual.default_milestone_shape
        self.default_activity_shape = self.visual.default_activity_shape
        self.default_activity_plotable_style = self.visual.default_activity_plotable_style
        self.default_milestone_plotable_style = self.visual.default_milestone_plotable_style
        self.default_swimlane_plotable_style = self.visual.default_swimlane_plotable_style
        self.default_timeline_plotable_style_odd = self.visual.default_timeline_plotable_style_odd
        self.default_timeline_height = self.visual.default_timeline_height

        if self.visual.default_timeline_plotable_style_even is not None:
            self.default_timeline_plotable_style_even = self.visual.default_timeline_plotable_style_even
        else:
            self.default_timeline_plotable_style_even = self.visual.default_timeline_plotable_style_odd

    @staticmethod
    def calculate_defaults_for_visual(plan, **exclude):
        """
        Encapsulates calculation of default values for a new visual.  May want to make this
        more sophisticated (e.g. allow default values to be stored in the database) but for
        now just have default values defined in a single place in the code.

        exclude is a dictionary of the fields which have been specified by the caller and so don't need defaults. Only
        the defaults which aren't excluded should be calculated, as the others may fail depending upon context which is
        why the user/caller has the option to provide them.

        :param plan:
        :return:
        """
        defaults = {}
        excluded_field_names = exclude.keys()

        # Local function to help in setting only defaults that user hasn't already specified.
        def set_default(key, calculate_value):
            if key not in excluded_field_names:
                defaults[key] = calculate_value()

        from plan_visual_django.models import PlotableStyle

        num_visuals_for_plan = plan.planvisual_set.count()

        # Only set defaults for field names that haven't been specified.
        set_default("name", lambda: f"{plan.plan_name}-Visual-{num_visuals_for_plan+1:02d}")
        set_default("width", lambda: 1200)
        set_default("max_height", lambda: 800)
        set_default("include_title", lambda: False)
        set_default("default_activity_shape", lambda: PlotableShapeName.RECTANGLE.name)
        set_default("default_milestone_shape", lambda: PlotableShapeName.DIAMOND.name)
        set_default("track_height", lambda: 20)
        set_default("track_gap", lambda: 4)
        set_default("milestone_width", lambda: 10)
        set_default("swimlane_gap", lambda: 5)
        set_default("default_activity_plotable_style", lambda: PlotableStyle.objects.get(style_name="theme-01-001-activities-01"))
        set_default("default_milestone_plotable_style", lambda: PlotableStyle.objects.get(style_name="theme-01-004-milestones-01"))
        set_default("default_swimlane_plotable_style", lambda: PlotableStyle.objects.get(style_name="theme-01-006-swimlanes-01"))
        set_default("default_timeline_plotable_style_odd", lambda: PlotableStyle.objects.get(style_name="theme-01-008-timelines-01"))
        set_default("default_timeline_plotable_style_even", lambda: PlotableStyle.objects.get(style_name="theme-01-009-timelines-02"))
        set_default("default_timeline_height", lambda: 20)

        return defaults

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



