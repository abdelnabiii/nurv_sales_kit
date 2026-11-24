// node render_study.js <html> <out.pdf>
const { chromium } = require('playwright'); const path = require('path');
(async () => { const [h, o] = process.argv.slice(2); const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + path.resolve(h), { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: o, preferCSSPageSize: true, printBackground: true }); await b.close(); console.log('pdf', o); })();
