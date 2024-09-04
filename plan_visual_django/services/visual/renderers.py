from abc import ABC, abstractmethod
from typing import Iterable, Dict
from plan_visual_django.models import VisualActivity, PlotableStyle, Color
from plan_visual_django.services.visual.plotables import RectangleBasedPlotable, Plotable
from plan_visual_django.services.visual.visual_elements import VisualElementCollection, VisualElement


class VisualRenderer(ABC):
    """
    An object which carries out the physical plotting of objects within the visual.
    """

    def plot_visual(self, visual: VisualElementCollection):
        for collection in visual.collection:
            self.plot_collection(collection)

    def plot_collection(self, collection: VisualElementCollection):
        """
        Recursive method which iterates through a collection and either plots the object if it is a Plotable, or
        calls this method recursively if the item is another collection.

        :param collection:
        :return:
        """
        for item, level in collection.iter():
            if type(item) == type(VisualElement) or issubclass(type(item), VisualElement):
                plotable = item.plot_element()
                self.plot_plotable(plotable)
            elif type(item) == type(VisualElementCollection):
                self.plot_collection(item)
            else:
                raise Exception(f"Unexpected type {type(item)} when plotting visual")


    @abstractmethod
    def plot_plotable(self, item: Plotable):
        pass


class CanvasRenderer(VisualRenderer):
    """
    Carries out the plotting activities for plotting on a Canvas on a web page.

    Note that unlike other plotters, this class doesn't carry out the physical plotting as that needs to happen within
    the browser.  This class will create the object which will then be converted to a JSON string and sent to the
    browser to actually plot the shapes on the canvas.
    """
    def __init__(self):
        """
        Set up object to capture plotted information which will get sent to browser as part of a Django template.
        """
        self.browser_data = {
            'settings': {
            },
            'shapes': []
        }

    @staticmethod
    def color_to_tuple(color: Color):
        """
        Takes a color record from database which includes RGBA and returns a tuple which can be serialised
        into JSON

        :return:
        """
        return (
            color.red,
            color.green,
            color.blue,
            color.alpha
        )

    def format_to_dict(
            self,
            shape_format: PlotableStyle,
            text_vertical_alignment: VisualActivity.VerticalAlignment,
            text_flow: VisualActivity.TextFlow,
            external_text_flag
    ):
        """
        Creates simplified dict version of the object to allow JSON serialisation within template.

        :param external_text_flag: Indicates that text is to be positioned outside the shape but other layout options
                                   to be applied still.  Intended for milestone type shapes where the shape is too small
                                   for the text to be positioned inside it.
                                   NOTE: This isn't selected by the user, it's automatically set when converting
                                   activities to plotables, based on whether the activity is a milestone or not.
        :param text_flow:
        :param text_vertical_alignment:
        :param shape_format:
        :return:
        """
        shape_format_dict = {
            "line_style": {
                "line_color": self.color_to_tuple(shape_format.line_color),
                "line_thickness": shape_format.line_thickness,
            },
            "fill_style": {
                "fill_color": self.color_to_tuple(shape_format.fill_color),
            },
            "text_format": {
                "vertical_align": text_vertical_alignment.name,
                "text_flow": text_flow.name,
                "text_color": self.color_to_tuple(shape_format.font_color),
                "external_text_flag": external_text_flag,
                "font": shape_format.font.font_name,
                "font_size": shape_format.font_size,
            }
        }
        return shape_format_dict

    def plot_visual(self, visual_collection: VisualElementCollection):
        """
        For the canvas plotter, the plot data will be accumulated in an object which then needs to be returned so that
        it can be included within the template and sent to the browser.

        :param visual:
        :return:
        """
        width, height = visual_collection.get_dimensions()
        self.browser_data['settings']['canvas_width'] = width + 10  # Just adding a bit of padding for debug
        self.browser_data['settings']['canvas_height'] = height + 10
        super().plot_visual(visual_collection)
        return self.browser_data

    def _render_iterable(self, plotable_iterable: Plotable | Iterable[Iterable | Plotable], rendered_objects: [Dict]):
        if isinstance(plotable_iterable, Plotable):
            rendered_objects.extend(self.plot_plotable(plotable_iterable))
        elif isinstance(plotable_iterable, Iterable):
            for next_plotable_iterable in plotable_iterable:
                self._render_iterable(next_plotable_iterable, rendered_objects)
        else:
            raise TypeError(f"Unsupported type when rendering to Canvas {type(plotable_iterable)}")

    def render_from_iterable(self, visual_plotables):
        """
        Replacement for original plot_visual to remove need for the Collection class.

        Input will be a dictionary of iterables, where each dict entry will be used to create the canvas objects for
        one canvas, and each canvas will be given a z-value to represent which layer it sits in the final rendered
        visual.  Canvases will be positioned back to front, with the first canvas being at the back.

        Output will be an object which can easily be rendered to JSON within the API.  All structure of the visual will
        be lost apart from which canvas an object appears in.

        :return:
        """
        canvas_objects = {}

        for canvas in visual_plotables:
            canvas_objects[canvas] = []
            plotable_iterable = visual_plotables[canvas]
            self._render_iterable(plotable_iterable, canvas_objects[canvas])

        return canvas_objects

    def plot_plotable(self, item: Plotable):
        # ToDo: Replace rectangle with more generic plotable and associated processing.
        """
        Return structure with information required for browser to plot the shape.  Note when we send this to the
        client for plotting on an HTML canvas, all context will be lost, we are just plotting shapes on the screen.
        So any logic around positioning of objects (e.g. text layout) needs to be here.

        :param scale_factor:
        :param item:
        :return:
        """
        if isinstance(item, RectangleBasedPlotable):
            # Note a Plotable can be rendered as more than one canvas object; e.g. one for shape, one for text.

            text_x, text_align = item.get_text_x()
            text_y, text_baseline = item.get_text_y()

            canvas_rendered_objects = [
                {
                    'shape_type': 'rectangle',
                    'shape_name': item.shape,
                    'shape_plot_dims': {
                        'top': item.top,
                        'left': item.left,
                        'width': item.width,
                        'height': item.height,
                    },
                    'fill_color': item.format.fill_color.to_dict(),
                    'stroke_color': item.format.line_color.to_dict(),
                    'stoke_line_width': item.format.line_thickness,
                },
                {
                    'shape_type': 'text',
                    'text': item.text,
                    'shape_name': None,  # If we are plotting text there is no shape name.
                    'shape_plot_dims': {
                        'x': text_x,
                        'y': text_y,
                        'text_align': text_align,
                        'text_baseline': text_baseline
                    },
                    'fill_color': item.format.font_color.to_dict(),
                    'font_size': round(item.format.font_size)
                }
            ]
            return canvas_rendered_objects
        else:
            raise ValueError(f"item of type which can't be rendered {item}:{item.__class__.__name__}")

    def plot_collection(self, collection: VisualElementCollection):
        super().plot_collection(collection)
