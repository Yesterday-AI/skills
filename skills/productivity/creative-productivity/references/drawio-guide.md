# draw.io Diagram Guide

Generate editable `.drawio` XML files for architecture diagrams, flowcharts, and technical documentation.

## When to Use

- Detailed technical/cloud architecture diagrams
- Diagrams that need to be edited by non-technical stakeholders (draw.io is free and visual)
- AWS/Azure/GCP architecture with official icons
- Diagrams embedded in Confluence, Notion, or other wikis

## Recommended Skill

For full draw.io generation with AWS icons and automated PNG conversion:
- **Source:** [softaworks/agent-toolkit — draw-io](https://github.com/softaworks/agent-toolkit/tree/main/skills/draw-io)
- **Features:** XML editing, AWS icon search, layout calculations, pre-commit PNG conversion

## Quick Start — XML Structure

```xml
<mxfile host="app.diagrams.net">
  <diagram name="Architecture" id="arch1">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10"
      page="0" defaultFontFamily="Inter">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <!-- Rectangle -->
        <mxCell id="box1" value="Service A" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;" vertex="1" parent="1">
          <mxGeometry x="100" y="100" width="160" height="60" as="geometry"/>
        </mxCell>

        <!-- Arrow -->
        <mxCell id="arrow1" value="API Call" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#666;" edge="1" source="box1" target="box2" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

        <!-- Another Rectangle -->
        <mxCell id="box2" value="Service B" style="rounded=1;whiteSpace=wrap;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;" vertex="1" parent="1">
          <mxGeometry x="400" y="100" width="160" height="60" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Common Style Patterns

### Shape Styles
```
# Rounded rectangle (service/component)
rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;

# Database cylinder
shape=cylinder3;whiteSpace=wrap;fillColor=#f5f5f5;strokeColor=#666;size=15;fontSize=14;

# Cloud shape (external service)
ellipse;shape=cloud;whiteSpace=wrap;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=14;

# Group/container
rounded=1;whiteSpace=wrap;fillColor=none;strokeColor=#999;dashed=1;fontSize=16;fontStyle=1;verticalAlign=top;
```

### Arrow Styles
```
# Standard
edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#666;

# Dashed (async/optional)
edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#999;dashed=1;

# Thick (primary flow)
edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#333;strokeWidth=2;
```

### Color Palette (Semantic)
| Purpose | Fill | Stroke |
|---------|------|--------|
| Compute/Service | `#dae8fc` | `#6c8ebf` |
| Data/Storage | `#d5e8d4` | `#82b366` |
| External/3rd Party | `#fff2cc` | `#d6b656` |
| User/Client | `#f8cecc` | `#b85450` |
| Network/API | `#e1d5e7` | `#9673a6` |
| Neutral/Container | `#f5f5f5` | `#666666` |

## Layout Guidelines

- **Minimum margins:** 30px from container boundaries
- **Element spacing:** 40px minimum between elements
- **Arrow labels:** 20px clearance from elements
- **Font sizes:** 14px for elements, 16-18px for group titles, 12px for annotations
- **Canvas:** Set `page="0"` (no background) for transparent export

## PNG Conversion

```bash
# Using draw.io CLI (if installed)
drawio -x -f png -s 2 -o output.png input.drawio

# Using the softaworks script
bash scripts/convert-drawio-to-png.sh architecture.drawio
```

## Tips

- Place arrows on back layer (define before shape elements in XML)
- Use `verticalAlign=top` for container/group labels
- Set `whiteSpace=wrap` on all text-containing elements
- For AWS icons: use `mxgraph.aws4.*` shapes (e.g., `mxgraph.aws4.compute.ec2_instance`)
- Test by opening the `.drawio` file at [app.diagrams.net](https://app.diagrams.net)
