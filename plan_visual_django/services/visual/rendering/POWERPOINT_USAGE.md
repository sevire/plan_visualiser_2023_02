# PowerPoint Renderer Usage

## Overview

The `PowerPointRenderer` converts visual plotables into PowerPoint shapes, creating a single slide with the entire visual diagram.

## Basic Usage

```python
from plan_visual_django.services.visual.rendering.renderers import PowerPointRenderer
from plan_visual_django.models import PlanVisual

# Get your visual and its plotables
visual = PlanVisual.objects.get(id=visual_id)
plotables = visual.get_plotables()  # Returns dict with layers: timelines, swimlanes, visual_activities

# Create renderer and render
renderer = PowerPointRenderer()
presentation = renderer.render_from_iterable(plotables)

# Save the presentation
presentation.save('output.pptx')
```

## Adding to Existing Presentation

```python
from pptx import Presentation

# Load existing presentation
prs = Presentation('existing.pptx')

# Render visual onto a new slide
renderer = PowerPointRenderer(presentation=prs)
prs = renderer.render_from_iterable(plotables)

# Save
prs.save('existing_with_visual.pptx')
```

## Rendering to Specific Slide

```python
# Render to slide at index 2 (third slide)
renderer = PowerPointRenderer(presentation=prs, slide_index=2)
prs = renderer.render_from_iterable(plotables)
```

## Creating API Endpoint

Example Django view for downloading a visual as PowerPoint:

```python
from django.http import HttpResponse
from plan_visual_django.models import PlanVisual
from plan_visual_django.services.visual.rendering.renderers import PowerPointRenderer
import io

def download_visual_as_pptx(request, visual_id):
    visual = PlanVisual.objects.get(id=visual_id)

    if visual.activity_count() == 0:
        return HttpResponse("No activities to render", status=204)

    # Get plotables and render
    plotables = visual.get_plotables()
    renderer = PowerPointRenderer()
    presentation = renderer.render_from_iterable(plotables)

    # Save to bytes buffer
    buffer = io.BytesIO()
    presentation.save(buffer)
    buffer.seek(0)

    # Return as downloadable file
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
    )
    response['Content-Disposition'] = f'attachment; filename="{visual.name}.pptx"'

    return response
```

## Features

### Automatic Scaling
The renderer automatically scales the visual to fit on a standard PowerPoint slide (10" x 7.5") with 0.5" margins, maintaining aspect ratio.

### Layer Support
Plotables are rendered in layer order:
1. **Timelines** (background)
2. **Swimlanes** (middle)
3. **Activities** (foreground)

This ensures proper z-ordering where activities appear on top of swimlanes.

### Supported Shapes
- Rectangle
- Rounded Rectangle
- Diamond
- Isosceles Triangle
- Bullet (rendered as oval)

### Text Formatting
- Font family, size, and color
- Horizontal alignment (left, center, right)
- Vertical alignment (top, middle, bottom)
- Text flows according to VisualActivity settings

### Colors and Styling
- Fill colors (with RGB values)
- Line colors and thickness
- Transparency support (if alpha < 255)

## Coordinate System

The visual's coordinate system (arbitrary units based on date ranges and track positions) is automatically converted to PowerPoint's coordinate system (inches). The conversion:

1. Calculates the bounding box of all plotables
2. Determines scale factor to fit within slide margins
3. Centers the visual on the slide
4. Converts all coordinates during rendering

## Limitations

- Currently supports only `RectangleBasedPlotable` objects
- External text positioning (for milestones) is handled by placing text inside the shape with alignment
- No support for custom shapes beyond the standard PowerPoint shape library

## Future Enhancements

Possible improvements:
- Support for gradient fills
- Support for external text boxes for milestone labels
- Custom positioning/sizing of slide content
- Multiple visuals per presentation
- Custom slide layouts/themes
