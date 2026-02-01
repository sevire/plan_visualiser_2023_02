from abc import ABC, abstractmethod
from typing import Iterable, Dict, List, Optional
from plan_visual_django.services.visual.rendering.plotables import RectangleBasedPlotable, Plotable
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor


class VisualRenderer(ABC):
    """
    Base class for all renderers that convert Plotables into a target medium.

    Architecture:
    - Takes plotables organized by layer (timelines, swimlanes, activities)
    - Layer order determines z-index/stacking order in the rendered output
    - Handles arbitrary nesting depth of plotables (e.g., timelines contain timeline labels)
    - Each subclass implements render_plotable() for medium-specific rendering
    """

    def render_from_iterable(self, visual_plotables: Dict[str, Iterable]):
        """
        Main entry point for rendering. Takes plotables organized by layer:
        {
            "timelines": [...],         # Background layer
            "swimlanes": [...],         # Middle layer
            "visual_activities": [...]  # Foreground layer
        }

        Layer order determines z-index in final output. Iterates through layers
        and recursively renders nested structures.

        :param visual_plotables: Dictionary mapping layer names to iterables of Plotables
        :return: Renderer-specific output (defined by _finalize_render())
        """
        for layer_name, plotable_iterable in visual_plotables.items():
            self._render_iterable(plotable_iterable)
        return self._finalize_render()

    def _render_iterable(self, plotable_iterable: Plotable | Iterable):
        """
        Recursively renders nested iterables of plotables.
        Handles arbitrary nesting depth (e.g., timeline -> timeline_labels).

        :param plotable_iterable: Either a single Plotable or an iterable containing
                                  Plotables and/or nested iterables
        """
        if isinstance(plotable_iterable, Plotable):
            self.render_plotable(plotable_iterable)
        elif isinstance(plotable_iterable, Iterable):
            for item in plotable_iterable:
                self._render_iterable(item)
        else:
            raise TypeError(f"Expected Plotable or Iterable, got {type(plotable_iterable)}")

    def _calculate_visual_bounds(self, visual_plotables: Dict[str, Iterable]):
        """
        Calculate the total dimensions of the visual by examining all plotables.
        
        :param visual_plotables: Dictionary of layer_name -> plotables
        :return: Tuple of (min_left, min_top, max_right, max_bottom, width, height)
        """
        min_left = float('inf')
        min_top = float('inf')
        max_right = float('-inf')
        max_bottom = float('-inf')

        # Updates visual bounds based on plotable dimensions
        def update_bounds(plotable: Plotable):
            nonlocal min_left, min_top, max_right, max_bottom
            min_left = min(min_left, plotable.get_left())
            min_top = min(min_top, plotable.get_top())
            max_right = max(max_right, plotable.get_right())
            max_bottom = max(max_bottom, plotable.get_bottom())

        def traverse(item):
            if isinstance(item, Plotable):
                update_bounds(item)
            elif isinstance(item, Iterable):
                for sub_item in item:
                    traverse(sub_item)

        for layer_plotables in visual_plotables.values():
            traverse(layer_plotables)

        width = max_right - min_left if max_right != float('-inf') else 0
        height = max_bottom - min_top if max_bottom != float('-inf') else 0

        return min_left, min_top, max_right, max_bottom, width, height

    @abstractmethod
    def render_plotable(self, plotable: Plotable):
        """
        Render a single plotable to the target medium.
        Must be implemented by each subclass for their specific output format.

        :param plotable: The Plotable object to render
        """
        pass

    def _finalize_render(self):
        """
        Called after all plotables have been rendered.
        Override to return medium-specific output.

        :return: The final rendered output (format depends on subclass)
        """
        return None


class CanvasRenderer(VisualRenderer):
    """
    Renders plotables as JSON data structures for HTML Canvas rendering in the browser.

    This renderer doesn't perform actual drawing - it creates data structures that
    are serialized to JSON and sent to the browser, where JavaScript renders them
    onto HTML canvas elements.

    Output format: Dictionary mapping layer names to lists of canvas objects
    {
        "timelines": [{shape_data}, {shape_data}, ...],
        "swimlanes": [{shape_data}, {shape_data}, ...],
        "visual_activities": [{shape_data}, {shape_data}, ...]
    }
    """

    def __init__(self):
        """Initialize canvas renderer with empty output structure."""
        self.canvas_objects = {}
        self.current_layer = None

    def render_from_iterable(self, visual_plotables: Dict[str, Iterable]):
        """
        Override to track which layer we're rendering for proper organization.

        :param visual_plotables: Dictionary of layer_name -> plotables
        :return: Dictionary of layer_name -> rendered canvas objects
        """
        for layer_name, plotable_iterable in visual_plotables.items():
            self.current_layer = layer_name
            self.canvas_objects[layer_name] = []
            self._render_iterable(plotable_iterable)

        return self.canvas_objects

    def _render_iterable(self, plotable_iterable: Plotable | Iterable):
        """
        Override to accumulate rendered objects in current layer.
        """
        if isinstance(plotable_iterable, Plotable):
            rendered_objects = self.render_plotable(plotable_iterable)
            self.canvas_objects[self.current_layer].extend(rendered_objects)
        elif isinstance(plotable_iterable, Iterable):
            for item in plotable_iterable:
                self._render_iterable(item)
        else:
            raise TypeError(f"Expected Plotable or Iterable, got {type(plotable_iterable)}")

    def render_plotable(self, item: Plotable):
        """
        Converts a Plotable into JSON-serializable canvas rendering data.

        Note: A single Plotable may produce multiple canvas objects (e.g., separate
        objects for shape and text). Text positioning logic is calculated here since
        the browser only receives flat drawing instructions.

        :param item: The Plotable to render
        :return: List of canvas object dictionaries
        """
        if isinstance(item, RectangleBasedPlotable):
            # Note a Plotable can be rendered as more than one canvas object; e.g. one for shape, one for text.

            text_x, text_align = item.get_text_x()
            text_y, text_baseline = item.get_text_y()

            canvas_rendered_objects = [
                {
                    "plotable_id": item.plotable_id,
                    'shape_type': 'rectangle',
                    'shape_name': item.shape.value,
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
                    "plotable_id": f"{item.plotable_id}-text",
                    'shape_type': 'text',
                    'text': item.text,
                    'shape_name': None,  # If we are plotting text there is no shape name.
                    'shape_plot_dims': {
                        'x': text_x,
                        'y': text_y,
                        'text_align': text_align,
                        'text_baseline': text_baseline
                    },
                    'fill_color': item.format.font_color.to_dict(), # Note that when plotting text, fill colour is the
                                                                    # font colour of the text to be plotted
                    'font_size': round(item.format.font_size)
                }
            ]
            return canvas_rendered_objects
        else:
            raise ValueError(f"item of type which can't be rendered {item}:{item.__class__.__name__}")


class PowerPointRenderer(VisualRenderer):
    """
    Renders plotables as shapes on a PowerPoint slide.

    This renderer creates actual PowerPoint shapes using python-pptx library,
    drawing directly onto a slide with proper layering (timelines at back,
    activities at front).

    The coordinate system is converted from the visual's coordinate system
    (arbitrary units) to PowerPoint's coordinate system (EMUs/Inches).
    """

    def __init__(self, presentation: Optional[Presentation] = None, slide_index: int = None):
        """
        Initialize PowerPoint renderer.

        :param presentation: Optional existing Presentation. If None, creates new one.
        :param slide_index: Optional slide index to use. If None, adds a new blank slide.
        """
        if presentation is None:
            self.presentation = Presentation()
            # Add a blank slide layout (layout 6 is typically blank)
            blank_slide_layout = self.presentation.slide_layouts[6]
            self.slide = self.presentation.slides.add_slide(blank_slide_layout)
        else:
            self.presentation = presentation
            if slide_index is not None:
                self.slide = self.presentation.slides[slide_index]
            else:
                blank_slide_layout = self.presentation.slide_layouts[6]
                self.slide = self.presentation.slides.add_slide(blank_slide_layout)

        # Will be set during rendering to calculate coordinate conversion
        self.visual_width = None
        self.visual_height = None
        self.scale_factor = None

    def render_from_iterable(self, visual_plotables: Dict[str, Iterable]):
        """
        Override to calculate visual dimensions and scale factor before rendering.

        :param visual_plotables: Dictionary of layer_name -> plotables
        :return: The Presentation object with rendered slide
        """
        # Calculate the bounding box of all plotables to determine scale
        _, _, _, _, self.visual_width, self.visual_height = self._calculate_visual_bounds(visual_plotables)

        # Calculate scale factor to fit on slide with some margin
        margin = Inches(0.5)
        
        # Use presentation slide dimensions instead of hardcoded constants
        available_width = self.presentation.slide_width - 2 * margin
        available_height = self.presentation.slide_height - 2 * margin

        scale_x = available_width / self.visual_width if self.visual_width > 0 else 1
        scale_y = available_height / self.visual_height if self.visual_height > 0 else 1

        # Use the smaller scale to ensure it fits
        self.scale_factor = min(scale_x, scale_y)

        # Store offset to center the visual
        self.offset_left = margin + (available_width - self.visual_width * self.scale_factor) / 2
        self.offset_top = margin + (available_height - self.visual_height * self.scale_factor) / 2

        # Now render with the parent implementation
        super().render_from_iterable(visual_plotables)

        return self.presentation

    def _convert_to_pptx_coords(self, left: float, top: float, width: float, height: float):
        """
        Convert visual coordinates to PowerPoint coordinates.

        :return: (left, top, width, height) in PowerPoint units (Inches)
        """
        pptx_left = self.offset_left + left * self.scale_factor
        pptx_top = self.offset_top + top * self.scale_factor
        pptx_width = width * self.scale_factor
        pptx_height = height * self.scale_factor

        return pptx_left, pptx_top, pptx_width, pptx_height

    def _get_shape_type(self, shape_name: str):
        """
        Map plotable shape names to PowerPoint shape types.

        :param shape_name: Name from PlotableShapeName enum
        :return: MSO_SHAPE constant
        """
        shape_mapping = {
            'RECTANGLE': MSO_SHAPE.RECTANGLE,
            'ROUNDED_RECTANGLE': MSO_SHAPE.ROUNDED_RECTANGLE,
            'DIAMOND': MSO_SHAPE.DIAMOND,
            'ISOSCELES_TRIANGLE': MSO_SHAPE.ISOSCELES_TRIANGLE,
            'BULLET': MSO_SHAPE.OVAL,  # Use oval for bullets
        }
        return shape_mapping.get(shape_name, MSO_SHAPE.RECTANGLE)

    def render_plotable(self, item: Plotable):
        """
        Render a single plotable as a PowerPoint shape.

        :param item: The Plotable to render
        """
        if isinstance(item, RectangleBasedPlotable):
            # Convert coordinates
            left, top, width, height = self._convert_to_pptx_coords(
                item.left, item.top, item.width, item.height
            )

            # Add the shape
            shape_type = self._get_shape_type(item.shape.value)
            shape = self.slide.shapes.add_shape(
                shape_type,
                left, top, width, height
            )

            # Set fill color
            fill = shape.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(
                item.format.fill_color.red,
                item.format.fill_color.green,
                item.format.fill_color.blue
            )

            # Set line color and thickness
            line = shape.line
            line.color.rgb = RGBColor(
                item.format.line_color.red,
                item.format.line_color.green,
                item.format.line_color.blue
            )
            line.width = Pt(item.format.line_thickness)

            # Add text if present
            if item.text:
                text_frame = shape.text_frame
                text_frame.clear()  # Clear any default text
                p = text_frame.paragraphs[0]
                run = p.add_run()
                run.text = item.text

                # Set font properties
                font = run.font
                font.size = Pt(item.format.font_size)
                font.color.rgb = RGBColor(
                    item.format.font_color.red,
                    item.format.font_color.green,
                    item.format.font_color.blue
                )
                if item.format.font.font_name:
                    font.name = item.format.font.font_name

                # Set text alignment based on text_flow
                from plan_visual_django.models import VisualActivity
                if item.text_flow == VisualActivity.TextFlow.FLOW_CENTRE:
                    from pptx.enum.text import PP_ALIGN
                    p.alignment = PP_ALIGN.CENTER
                elif item.text_flow == VisualActivity.TextFlow.FLOW_TO_LEFT:
                    from pptx.enum.text import PP_ALIGN
                    p.alignment = PP_ALIGN.RIGHT
                else:  # FLOW_TO_RIGHT or default
                    from pptx.enum.text import PP_ALIGN
                    p.alignment = PP_ALIGN.LEFT

                # Set vertical alignment
                if item.text_vertical_alignment == VisualActivity.VerticalAlignment.MIDDLE:
                    from pptx.enum.text import MSO_ANCHOR
                    text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
                elif item.text_vertical_alignment == VisualActivity.VerticalAlignment.BOTTOM:
                    from pptx.enum.text import MSO_ANCHOR
                    text_frame.vertical_anchor = MSO_ANCHOR.BOTTOM
                else:  # TOP or default
                    from pptx.enum.text import MSO_ANCHOR
                    text_frame.vertical_anchor = MSO_ANCHOR.TOP

        else:
            raise ValueError(f"Unsupported plotable type for PowerPoint: {item.__class__.__name__}")
