# nurv Investor Brochure — Open Questions and Notes

Deliverable: `nurv_Investor_Brochure_2026.pdf` (18 pages, 1980 x 1080 pt, fonts embedded).
Editable source: `brochure/` (HTML/CSS + SVG; rebuild with `python3 build.py && node render.js`).

## A. Open items

| # | Item | Status |
|---|---|---|
| A1 | **Basement image (p.8).** Per your instruction, p.8 shows an underground loading bay. No official basement render exists, so this is an illustrative image generated for the brochure (Higgsfield, GPT Image model; no text, logos or people), captioned "Illustrative image of a basement loading bay; not the nurv basement." | Replace with an official render when available. |
| A2 | **Legal disclaimer page removed** at your request. The short legal line remains in every page footer: "For information only. Not an offer or a contract. Visuals are artist's impressions; plans, areas and specifications are indicative and subject to change." | Confirm that the footer line is sufficient, or supply approved legal text. |
| A3 | **Google Maps content (p.6).** The map is a genuine Google Maps capture (Map data ©2026 Google), with Google's attribution kept. Google's map shows third-party place pins (schools, shops, a gym and others), which cannot be switched off in a standard Google map. | Confirm this is acceptable, or ask for a satellite view without labels. |

## B. Brand and asset requests

| # | Item | Notes |
|---|---|---|
| B1 | **Aeonik font files (licensed).** | The brochure uses Inter Tight (SIL OFL), as approved. Switching to Aeonik is a one-line change to the `@font-face` rules. |
| B2 | **Original vector logos.** | Logos were traced to vector from raster sources. Per your edit, the nurv. wordmark is now all white. The logo row on the Contact page has been removed. |
| B3 | **Higher-resolution exterior renders.** | Every image is placed at or below its native size. The best available exterior views are 1010–1441 px wide; higher-resolution renders would allow full-bleed pages. |
| B4 | **Home comfort imagery (1st floor, p.10).** | Uses the armchair cropped from the deck's home comfort page (360x290 px). A proper render would be better. |

## C. Decisions and data applied

1. **Design:** only the "nurv. + RESTAURANT" design (Design A) is used. The REGALIA-associated render set is excluded.
2. **Areas:**
   - Basement 1,100 sqm.
   - Ground, 1st and 2nd 675 sqm each.
   - 3rd 675 sqm, Subject to final approvals.
   - On-Air Track (rooftop) 200 sqm.
3. **Floor heights:** ground 5 m; basement, 1st, 2nd and 3rd 4 m.
4. **Units:** approximately 11 per floor (ground, 1st, 2nd).
5. **Meadis Group:** described as Jalour's retail and commercial expertise partner, managing nurv.
6. **Founding year:** "1985" is used. No other historic figures.
7. **Third floor:** shows the second-floor layout as the typical plan (p.12). Every mention carries "Subject to final approvals."
8. **Roof plan (p.13):** redrawn from `Roof - Updated.pdf`. The roof sheet's area table is not used.
9. **Contents (p.2):** every section is numbered 01–11, and the numbers match the section openers.

## D. Images: sources and exclusions

- **Cover (p.1):** the completed building at dusk, a 1920x1080 frame from the construction video, shown in full (zoomed out).
- **p.4:** the full daytime ("morning") view of the building, cropped above the cars so the Audi badge is excluded.
- **p.5, The Building:**
  - the evening restaurant frontage with the nurv. sign (Audi cropped out);
  - the Wellness Arena;
  - the On-Air Track.
- **p.9 (Ground floor):** a wider daytime view of the restaurant frontage, terraces and nurv. sign (Audi cropped out).
- **p.14:** the evening façade and restaurant frontage.
- **Excluded:**
  - the REGALIA images (WhatsApp image, 3.webp, 4.webp) and 2.webp;
  - deck target-group, moodboard, sponsorship, bank/telecom and "Luster & Luxe" imagery;
  - hexagon cut-outs and collages;
  - the first video frame, which shows dimension figures.

## E. Plans: method

- **Sources and redraw:** plans for the basement to 2nd floor and the roof are redrawn from the CAD files' own layers, with geometry unchanged.
- **Removed:** title blocks, unit areas and numbers, tenant labels, dimensions, cars, parking arrows and the architect's contact details.
- **Labels:** generic only. Label positions were placed by eye; please check.

## F. Quality checks on the final PDF

- **Banned-term search:** EGP, price, ROI, yield, return, rent, income, instalment, deposit, maintenance, fee, lease, share, fractional, liquidity, sponsorship, equity, regalia, @yahoo, 01060558379, investment, signed → **0 hits**.
- **Numbers present:**
  - Location: 30–40 m, 0.6 km, 0.8 km and the site coordinates.
  - Building: 1,100 / 675 / 200 sqm, 5 m, 4 m, approximately 11 units.
  - Approved: 1985, 24/7 (security).
  - Running content: 2026, page and section numbers, contact phone.
- **Production checks:**
  - Fonts: all embedded.
  - Images: none upscaled.
  - Every page carries the identical header, footer logo, page number and legal line.
