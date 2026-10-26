// Leest alle categorieën en producten uit de Ecwid-winkel op de live site
// en schrijft hun adressen naar data/ecwid-paginas.json (voor de sitemap).
// Gebruik: node tools/ecwid-paginas.js && python3 tools/build.py
const {chromium} = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  const start = 'https://folkfestivalham.be/tickets/';
  const gezien = new Set(), todo = [start], gevonden = new Set();
  while (todo.length) {
    const u = todo.shift(); if (gezien.has(u)) continue; gezien.add(u);
    await p.goto(u); await p.waitForTimeout(6000);
    const links = await p.evaluate(() => [...document.querySelectorAll('.winkel a[href]')].map(a => a.href));
    for (const l of links) {
      const m = l.split('?')[0].split('#')[0];
      if (/\/tickets\/[^/]+-[cp]\d+$/.test(m) && !gevonden.has(m)) { gevonden.add(m); if (/-c\d+$/.test(m)) todo.push(m); }
    }
  }
  await b.close();
  const paden = [...gevonden].map(u => new URL(u).pathname).sort();
  fs.writeFileSync(path.join(__dirname, '..', 'data', 'ecwid-paginas.json'), JSON.stringify(paden, null, 2) + '\n');
  console.log(paden.length + " Ecwid-pagina's:\n" + paden.join('\n'));
})();
