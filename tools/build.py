#!/usr/bin/env python3
"""Bouwt de pagina's in public/ uit pages/*.html + de gedeelde header en footer.

Gebruik:  python3 tools/build.py
Elke pagina in pages/ begint met een paar regels instellingen:
    title: ...
    description: ...
    path: /praktisch/
    nav: praktisch            (welk menu-item actief is, mag leeg)
    ---
Daarna volgt de inhoud (HTML). Het resultaat komt in public/ en wordt mee gecommit,
zodat Cloudflare zelf niets hoeft te bouwen.
"""
from pathlib import Path
import datetime

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "pages"
PUBLIC = ROOT / "public"
SITE = "https://folkfestivalham.be"
DATUM_FESTIVAL = "14 - 15 - 16 augustus 2026"

ICON = {
    "facebook": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.5 22v-8h2.7l.4-3.2h-3.1V8.8c0-.9.3-1.5 1.6-1.5h1.7V4.4c-.3 0-1.3-.1-2.4-.1-2.4 0-4 1.5-4 4.1v2.4H7.7V14h2.7v8h3.1z"/></svg>',
    "instagram": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 7.3A4.7 4.7 0 1 0 12 16.7 4.7 4.7 0 0 0 12 7.3zm0 7.7a3 3 0 1 1 0-6 3 3 0 0 1 0 6zm6-7.9a1.1 1.1 0 1 1-2.2 0 1.1 1.1 0 0 1 2.2 0zM21.9 8.2c-.1-1.5-.4-2.8-1.5-3.9S17.9 2.9 16.4 2.8C14.9 2.7 9.1 2.7 7.6 2.8c-1.5.1-2.8.4-3.9 1.5S2.3 6.7 2.2 8.2c-.1 1.5-.1 6.1 0 7.6.1 1.5.4 2.8 1.5 3.9s2.4 1.4 3.9 1.5c1.5.1 7.3.1 8.8 0 1.5-.1 2.8-.4 3.9-1.5s1.4-2.4 1.5-3.9c.1-1.5.1-6.1 0-7.6zm-2 9.5c-.3.8-.9 1.4-1.7 1.7-1.2.5-3.9.4-5.2.4s-4 .1-5.2-.4a3 3 0 0 1-1.7-1.7c-.5-1.2-.4-3.9-.4-5.2s-.1-4 .4-5.2c.3-.8.9-1.4 1.7-1.7 1.2-.5 3.9-.4 5.2-.4s4-.1 5.2.4c.8.3 1.4.9 1.7 1.7.5 1.2.4 3.9.4 5.2s.1 4-.4 5.2z"/></svg>',
    "youtube": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2C.5 9.1.5 12 .5 12s0 2.9.5 4.8a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1c.5-1.9.5-4.8.5-4.8s0-2.9-.5-4.8zM9.7 15.5v-7l6.1 3.5-6.1 3.5z"/></svg>',
    "huis": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 2 11h3v10h6v-6h2v6h6V11h3z"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 5h20v14H2zm2 2v.5l8 5 8-5V7zm16 10V9.8l-8 5-8-5V17z"/></svg>',
    "tel": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15.2 15.2 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1z"/></svg>',
}

SOCIALS = f"""<div class="socials">
        <a href="https://www.facebook.com/FolkfestivalHam/" aria-label="Facebook">{ICON['facebook']}</a>
        <a href="https://www.instagram.com/FolkfestivalHam/" aria-label="Instagram">{ICON['instagram']}</a>
        <a href="https://bit.ly/3628Mtj" aria-label="YouTube">{ICON['youtube']}</a>
      </div>"""

MENU = [
    ("home", "Home", "/"),
    ("concerten", "Concerten", "/tickets/#!/Concerten/c/126605256"),
    ("over-ons", "Over ons", "/over-ons/"),
    ("praktisch", "Praktisch", "/praktisch/"),
    ("medewerkers", "Medewerkers", "/medewerkers/"),
]

SPONSORS = [
    ("dpf-1", "De Pretfabriek", "https://depretfabriek.be?utm_source=FFH"),
    ("pure", "Pure", None), ("cornet", "Cornet", None), ("maes", "Maes", None),
    ("crea", "Sponsor", None), ("wroeter", "Wroeter", None), ("edma", "EDMA", None),
    ("gezinsbond", "Gezinsbond", None), ("bidfood", "Bidfood", None),
    ("jamarnu", "Drukkerij Jamar", None), ("sponsor-nicotours", "Nico Tours", None),
    ("vhs", "Verhofstede", None), ("logo-tes-ham", "Gemeente Tessenderlo-Ham", None),
    ("vertessen", "Vertessen", None), ("aeollus", "Aeollus", None),
    ("ghoos", "Ghoos", None), ("rudi", "Rudi De Scheemaeker Produkties", None),
]


def header(nav):
    actief = ' aria-current="page"'
    items = "\n".join(
        f'        <li><a href="{href}"{actief if key == nav else ""}>{label}</a></li>'
        for key, label, href in MENU
    )
    return f"""<a class="skip" href="#inhoud">Ga naar de inhoud</a>
<header class="site-header">
  <div class="textuur">
    <div class="wrap top">
      <a class="brand" href="/">
        <img src="/assets/img/logo.webp" width="800" height="211" alt="Folkfestival Ham">
        <span class="datum">{DATUM_FESTIVAL}</span>
      </a>
      <div class="top-rechts">
      {SOCIALS}
        <a class="btn btn-oranje" href="/tickets/">Tickets</a>
      </div>
    </div>
  </div>
  <nav class="nav" aria-label="Hoofdmenu">
    <button class="menu-knop" type="button" aria-expanded="false">Menu</button>
    <ul>
{items}
    </ul>
  </nav>
</header>"""


def footer():
    logos = "\n".join(
        (f'      <a href="{url}" target="_blank" rel="noopener"><img src="/assets/img/sponsors/{f}.webp" alt="{alt}" loading="lazy"></a>'
         if url else f'      <img src="/assets/img/sponsors/{f}.webp" alt="{alt}" loading="lazy">')
        for f, alt, url in SPONSORS
    )
    jaar = datetime.date.today().year
    # Carousel: de logo's staan twee keer na elkaar zodat de band naadloos doorloopt.
    # De tweede reeks is verborgen voor schermlezers en niet aanklikbaar met tab.
    kopie = logos.replace('<a href=', '<a tabindex="-1" href=')
    return f"""<section class="sponsors" aria-label="Partners en sponsors">
  <div class="carousel">
    <div class="carousel-band">
      <div class="carousel-reeks">
{logos}
      </div>
      <div class="carousel-reeks" aria-hidden="true">
{kopie}
      </div>
    </div>
  </div>
</section>
<footer class="site-footer textuur">
  <img class="logo" src="/assets/img/logo.webp" width="800" height="211" alt="Folkfestival Ham" loading="lazy">
  {SOCIALS}
  <ul class="contact">
    <li>{ICON['huis']}<a href="https://www.celticartgallery.be">The Celtic Art Gallery vzw</a></li>
    <li>{ICON['pin']}Genebosstraat 4, 3945 Genebos, België</li>
    <li>{ICON['mail']}<a href="mailto:info@folkfestivalham.be">info@folkfestivalham.be</a></li>
    <li>{ICON['tel']}<a href="tel:+3213671373">+32 (0)13 67 13 73</a></li>
  </ul>
  <p class="klein">© {jaar} The Celtic Art Gallery vzw</p>
</footer>
<script>
  (function () {{
    var nav = document.querySelector('.nav'), knop = nav && nav.querySelector('.menu-knop');
    if (knop) knop.addEventListener('click', function () {{
      var open = nav.classList.toggle('open');
      knop.setAttribute('aria-expanded', open ? 'true' : 'false');
    }});
  }})();
</script>"""


def page(meta, body):
    title = meta["title"]
    full_title = "Folkfestival Ham" if title == "Folkfestival Ham" else f"{title} – Folkfestival Ham"
    robots = '\n  <meta name="robots" content="noindex">' if meta.get("noindex") else ""
    canonical = "" if meta.get("noindex") else f'\n  <link rel="canonical" href="{SITE}{meta["path"]}">'
    return f"""<!doctype html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{full_title}</title>
  <meta name="description" content="{meta['description']}">{canonical}{robots}
  <meta property="og:title" content="{full_title}">
  <meta property="og:description" content="{meta['description']}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{SITE}{meta['path']}">
  <meta property="og:image" content="{SITE}/assets/img/hero-bedankt.webp">
  <meta name="theme-color" content="#80C04E">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/png" href="/icon-192.png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="preload" href="/assets/fonts/jost.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
{header(meta.get('nav', ''))}
<main id="inhoud">
{body.strip()}
</main>
{footer()}
</body>
</html>
"""


def read(path):
    raw = path.read_text(encoding="utf-8")
    head, body = raw.split("\n---\n", 1)
    meta = {}
    for line in head.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, body


def main():
    urls = []
    for src in sorted(PAGES.glob("*.html")):
        meta, body = read(src)
        p = meta["path"]
        out = PUBLIC / "404.html" if p == "/404" else PUBLIC / p.strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(meta, body), encoding="utf-8")
        if not meta.get("noindex"):
            urls.append(p)
        print("gebouwd:", out.relative_to(ROOT))
    today = datetime.date.today().isoformat()
    sm = "\n".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>" for u in sorted(urls))
    (PUBLIC / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}\n</urlset>\n',
        encoding="utf-8")
    (PUBLIC / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print("gebouwd: sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
