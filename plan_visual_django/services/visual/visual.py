from __future__ import annotations
from abc import ABC, abstractmethod

from plan_visual_django.services.visual.plotables import Plotable
from plan_visual_django.services.visual.visual_elements import VisualElementCollection


class PlotableCollection():
    """
    A sequence of plotable elements or collections of plotable elements which define the structure of a visual. A given
    collection will subclass this class to allow collection specific behaviour to be defined.
    """
    def __init__(self):
        self.plotables: [Plotable | PlotableCollection] = []

    def get_dimensions(self):
        """
        Calculate the enclosing rectangle for this collection by getting all the rectangles for each plotable and
        working out the size of rectangle need to contain them all.
        :return:
        """
        rectangles = [plotable.get_dimensions() for plotable in self.plotables]
        min_left = min([left for top, left, width, height, right, bottom in rectangles])
        max_right = max([right for top, left, width, height, right, bottom in rectangles])
        min_top = min([top for top, left, width, height, right, bottom in rectangles])
        max_bottom = max([bottom for top, left, width, height, right, bottom in rectangles])
        height = max_bottom - min_top
        width = max_right - min_left

        left, top, width, height, right, bottom = min_left, min_top, width, height, max_right, max_bottom

        return left, top, width, height, right, bottom

    def add_plotable(self, plotable: Plotable | PlotableCollection):
        """
        Adds either a plotable object or a collection of plotable objects.

        Note order is important in that objects within a collection will be plotted in order, so
        if they overlap the later ones will sit on top of the earlier ones, unless the default layer
        is overridden within the plotable.

        :param plotable:
        :return:
        """
        self.plotables.append(plotable)


class Visual:
    """
    The top level class which represents a visual to be plotted in one of various media, including on a web page while
    configuring and laying out the visual.

    A visual comprises the following elements:

    - Settings: Visual level settings information, such as the width, height of the visual.
    - Plotable Collections: Collections of plotable objects typically related by function in the plot, such as timeline
      labels, swimlanes etc.
    - Plotable objects: Any object which can be drawn on an output medium.  It will have a size and shape and formatting
      information associated with it to allow it to be drawn.
    - Layers: At the time of writing I am not sure how to implement this but layers is a concept which will determine
      which objects sit on top of other objects. The principle is that Plotable Collections will sit within a layer
      and all Plotable objects within that collection will sit on the same layer, although it will be possible to
      override on an object by object basis.
    """
    def __init__(self):
        self.current_layer = 1
        self.visual = {}  # The visual will contain numbered layers of plotable components.

    def set_layer(self, layer_number: int):
        """
        Sets the layer within which future added objects will sit unless overridden.

        Layer is an integer starting from 1, but can be any number.  When plotting layers on the bottom
        layer are plotted first so that objects on higher numbered layers will sit on top of them.

        :param layer_number:
        :return:
        """
        self.current_layer = layer_number

    def increment_layer(self):
        self.current_layer += 1

    def add_collection(self, collection_name, collection: PlotableCollection=None):
        """
        Can add a passed in collection to the visual or create a new collection to be added to later.

        :param collection_name:
        :param collection:
        :return:
        """
        collection_to_store = PlotableCollection() if collection is None else collection
        self.visual[collection_name] = {
            "layer": self.current_layer,
            "plotables": collection_to_store
        }

    def add_plotable(self, collection_name, plotable: Plotable):
        if collection_name not in self.visual:
            raise ValueError(f"Attept to add plotable to non existent collection {collection_name}")
        else:
            self.visual[collection_name].append(plotable)

    def iter_collections(self):
        """
        Generator to iterate through all the collections in the visual in order of what layer they are in.

        Collections in the same layer will appear in the order they were added.
        :return:
        """
        ordered_layers = sorted(self.visual.items(), key=lambda x: x[1]['layer'])

        # ToDo: Tidy this up a bit - we seem to have layer information twice.
        for layer in ordered_layers:
            layer_name, layer_collection = layer
            collection = layer_collection['plotables']
            yield collection

    def get_dimensions(self):
        """
        Works out the width and height of the overall visual based on the dimensions and position of each collection
        of plotable items it contains.

        :return:
        """
        max_bottom = max([bottom for left, top, width, height, right, bottom in [collection.get_dimensions() for collection in self.iter_collections()]])
        max_right = max([right for left, top, width, height, right, bottom in [collection.get_dimensions() for collection in self.iter_collections()]])

        # As the min top and left will always be zero the max bottom and left are also height wnd width.
        # left, top, width, height, right, bottom
        return 0, 0, max_right, max_bottom, max_right, max_bottom
