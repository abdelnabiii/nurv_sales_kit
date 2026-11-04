# nurv Investor Brochure — Open Questions and Notes

Deliverable: `nurv_Investor_Brochure_2026.pdf` (18 pages, 1980 x 1080 pt, fonts embedded).
Editable source: `brochure/` (HTML/CSS + SVG; rebuild with `python3 build.py && node render.js`).

## A. Items needed to finalise (placeholders in the PDF)

| # | Item | Where it appears | Status |
|---|---|---|---|
| A1 | **Approved legal disclaimer text.** None was found in the Drive folder. | p.17 (placeholder box, interim working text) | Please supply |
| A2 | **Basement gross area (BUA).** No figure supplied. | p.6 table, p.7 | Placeholder "to be confirmed" |
| A3 | **Rooftop / track area (BUA).** No figure supplied. | p.6 table, p.12 | Placeholder "to be confirmed" |
| A4 | **Third floor plan.** None exists. Subject to final approvals. | p.11 | Labelled placeholder |
| A5 | **Roof plan.** None exists. | p.12 | Labelled placeholder |

## B. Brand and asset requests

| # | Item | Notes |
|---|---|---|
| B1 | **Aeonik font files (licensed).** The template embeds only a subset of Aeonik, which cannot be reused. Per your approval, the brochure uses **Inter Tight** (SIL Open Font License). | If you supply licensed Aeonik files, switching is a one-line change to the `@font-face` rules in `src/brochure.html`. |
| B2 | **Original vector logos.** All three logos were traced to vector from raster sources. | Jalour: from the "JALOUR®" alpha mask in Nurv._compressed.pdf (510x154 px; the same wordmark as on the Company Profile cover, where the logo sits over a photo and could not be isolated cleanly). nurv.: from DMK-Nurv-Presentation p.4 (raster only). Meadis Group: from the 570x320 px mask in Nurv._compressed.pdf. Original vector files would give exact geometry. |
| B3 | **Higher-resolution Design A renders.** Each image is placed at or below its native size (no upscaling). Higher-resolution originals would allow full-bleed layouts. | Lower-resolution images in use: cover (828x1084 px, the night half of Company Profile p.23), p.4 (1011x811), p.9 (1011x430), p.13 (1000x666). |
| B4 | **Home comfort imagery for the 1st floor.** The only home comfort visual (deck p.32) is a collage, so it was not used. | p.9 uses a crop of the upper-floor glazing instead. |

## C. Decisions applied (from your answers), for the record

1. **Design:** only the "nurv. + RESTAURANT" design (Design A: sales deck, Company Profile p.23, construction video) is used. The NURV. - 20260311.pdf render set (Design B) is not used. That design also appears in the REGALIA images, which are excluded.
2. **Font:** Inter Tight fallback approved.
3. **Units:** "approximately 11 units per floor" is stated for the ground, 1st and 2nd floors. The CAD plans show 11, 7 and 9 subdivisions respectively, and the structural grid is flexible.
4. **Floor heights:** ground 5 m; basement, 1st, 2nd and 3rd 4 m.
5. **Meadis Group:** described as "Jalour's retail and commercial expertise partner", managing nurv. The specification calls Meadis a third-party facilities management company.
6. **Founding year:** "1985" is used (pp.3 and 16). No other historic dates or figures are used.
7. **Specification:** passenger elevator, backup generator (no capacity stated), split-unit cooling and the lit, rubberised perimeter track are kept. The 3–6 month fit-out window is omitted (no other numbers).

## D. Image exclusions and crops (audit trail)

- **Excluded (show "REGALIA"):** `WhatsApp Image 2026-09-13 at 15.26.42.webp`, `3.webp`, `4.webp`.
- **Not used:** `2.webp`. It shows no project name but is a low-resolution duplicate of a Design B render.
- **Third-party brand cropped out:** every Design A hero render shows an **Audi** badge on the car at left. The cover and the p.4 and p.13 images are cropped to exclude it. The SUV at right shows no badge.
- **Please confirm:** on the cover image, a window behind the nurv. sign holds a small, illegible sign-like text block (not a recognisable name). It was judged acceptable. Say if you want a tighter crop.
- **Excluded deck pages/imagery:** p.7 (target group), p.12 (moodboard), pp.38–39 (sponsorships), p.16 (bank/telecom branding), pp.29/31 ("Luster & Luxe"), all hexagon cut-outs and collages (pp.25, 35), p.18 cut-out (Design B), p.10 imagery (low resolution; artworks shown), and the DMK gradient imagery and mock-ups.
- **Construction video:** the first frame (shows dimension figures) is excluded. The stills used are the structural frame (p.16) and the completed building (p.15).

## E. Plans and map: method and limitations

- **Plans (pp.7–10):** redrawn from the vector geometry of `Shrouk Mall 1.pdf`, using its AutoCAD layers (walls, columns, stairs, doors, fixtures, ramp hatch).
  - Removed: title blocks, sheet frames, unit areas and numbers, tenant labels, dimensions, level markers, cars, parking arrows and the architect's phone and e-mail.
  - Geometry is unchanged apart from rotation to the drawn orientation and uniform scaling.
  - Each sheet is fitted to its panel. The source sheets use different paper scales, so the plans are labelled "not to scale".
  - Labels are generic only (stairs, elevator, plaza, ramp, loading, outdoor parking). Label positions were placed by eye; please check.
- **Map (p.5):** a clean schematic redraw of the Nurv._compressed.pdf p.5 map, keeping the site marker position.
  - The source's map-app interface text ("As Sports academy / Recently Viewed") and road-number shield are omitted.
  - La Vista CASA and Street Side Mall are not on the source map, so their distances appear as figures beneath the map rather than as plotted points.
  - Please confirm the map is acceptable, or supply a local-scale map.

## F. Quality checks performed on the final PDF

- **Banned-term search:** EGP, price, ROI, yield, return, rent, income, instalment, deposit, maintenance, fee, lease, share, fractional, liquidity, sponsorship, equity, regalia, @yahoo, 01060558379 (plus "investment" and "signed") → **0 hits**. Substring hits were removed by rewording: "coherent" → "unified", "designed" → "built"/"conceived".
- **Third floor:** every mention carries "Subject to final approvals." (pp.6, 11, 17).
- **Numbers present:**
  - Location: 30–40 m, 0.6 km, 0.8 km and the site coordinates.
  - Building: 675 sqm, 5 m, 4 m, approximately 11 units.
  - Approved: 1985, 24/7 (security).
  - Running content: 2026 (header), page and section numbers, contact phone.
- **Production checks:**
  - Fonts: Inter Tight Light, Regular, Medium and SemiBold, all embedded and subset.
  - Images: all embedded at their original JPEG data, at 72 ppi or above relative to page points (no upscaling).
  - Every page carries the identical header, footer logo, page number and legal line.
