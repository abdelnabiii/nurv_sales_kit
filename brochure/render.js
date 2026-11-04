// Render build/brochure.html to PDF (Chromium embeds the fonts) and optional per-page PNG previews.
// Usage: node render.js [out.pdf] [previewDir]
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const root = __dirname;
  const src = 'file://' + path.join(root, 'build', 'brochure.html');
  const out = process.argv[2] || path.join(root, '..', 'output', 'nurv_Investor_Brochure_2026.pdf');
  const prev = process.argv[3];
  fs.mkdirSync(path.dirname(out), { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(src, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true });

  if (prev) {
    fs.mkdirSync(prev, { recursive: true });
    // 1980 x 1080 pt = 2640 x 1440 CSS px
    const v = await browser.newPage({ viewport: { width: 2640, height: 1440 }, deviceScaleFactor: 1 });
    await v.goto(src, { waitUntil: 'networkidle' });
    await v.evaluate(() => document.fonts.ready);
    const els = await v.$$('section.page');
    for (let i = 0; i < els.length; i++) {
      await els[i].screenshot({ path: path.join(prev, `p${String(i + 1).padStart(2, '0')}.png`) });
    }
  }
  await browser.close();
  console.log('pdf', out);
})();
