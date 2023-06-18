from typing import Type

from plan_visual_django.services.visual.visual import VisualPlotter, Visual, Plotable, PlotableCollection, \
    RectangleBasedPlotable


class CanvasPlotter(VisualPlotter):
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

    def plot_visual(self, visual: Visual):
        """
        For the canvas plotter, the plot data will be accumulated in an object which then needs to be returned so that
        it can be included within the template and sent to the browser.

        :param visual:
        :return:
        """
        left, top, width, height, right, bottom = visual.get_dimensions()
        self.browser_data['settings']['canvas_width'] = width + 20  # Just adding a bit of padding for debug
        self.browser_data['settings']['canvas_height'] = height + 20
        super().plot_visual(visual)
        return self.browser_data

    def plot_plotable(self, item: RectangleBasedPlotable):
        # ToDo: Replace rectangle with more generic plotable and associated processing.
        """
        Return structure with information required for browser to plot the shape.

        :param item:
        :return:
        """

        activity_record = {
            'shape_details': {
                'shape_name': item.shape.name,
                'shape_plot_dims': {
                    'top': item.top,
                    'left': item.left,
                    'width': item.width,
                    'height': item.height
                }
            }
        }


        self.browser_data['shapes'].append(activity_record)

    def plot_collection(self, collection: PlotableCollection):
        super().plot_collection(collection)
