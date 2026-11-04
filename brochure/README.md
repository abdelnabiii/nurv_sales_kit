# nurv investor brochure: editable source

- `src/brochure.html`: page content and all styling (HTML/CSS, 1980 x 1080 pt pages). Edit copy here.
- `src/map.svg`: location map (schematic redraw).
- `assets/plans/plan1-4.svg`: redrawn floor plans (basement, ground, first, second).
- `assets/logo/*.svg`: traced logos (Jalour, nurv., Meadis Group).
- `assets/img/*.jpg`: image crops at native resolution.
- `fonts/`: Inter Tight (SIL OFL; see `OFL.txt`).
- `tools/`: scripts used to extract plans and logos from the source PDFs.
  - `cadpaths.py`: dumps CAD paths with layers.
  - `cadsvg.py`: filters and styles the paths into SVG.
  - `trace.py`: logo tracing.
  - `oclayer.py`: layer filter.

## Build

```bash
python3 build.py
```

```bash
node render.js ../output/nurv_Investor_Brochure_2026.pdf
```

`build.py` inlines the SVGs and adds the identical header and footer to every page. `render.js` prints the PDF with Chromium (Playwright), which embeds the fonts.
