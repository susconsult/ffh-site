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
import html
import json
import re

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "pages"
PUBLIC = ROOT / "public"
DATA = ROOT / "data"
SITE = "https://folkfestivalham.be"

# Instellingen: festivalmodus aan/uit en de datum in de header (data/instellingen.json)
INST = json.loads((DATA / "instellingen.json").read_text(encoding="utf-8"))
FESTIVAL = bool(INST.get("festivalmodus"))
# Alleen voor de preview: een schakelbalk bovenaan om festivalmodus aan/uit te bekijken.
# Bouwt beide versies; de bezoeker kiest met de schakelaar. NOOIT aanzetten op de live site (main).
PREVIEW = bool(INST.get("preview_schakelaar"))
# Veiligheid: op de live-tak (main) nooit de preview-schakelaar
try:
    import subprocess as _sp
    if _sp.run(["git", "-C", str(ROOT), "branch", "--show-current"], capture_output=True, text=True).stdout.strip() == "main":
        PREVIEW = False
except Exception:
    pass
if PREVIEW:
    FESTIVAL = True
DATUM_FESTIVAL = INST.get("datum_festival", "")
PROGRAMMA = json.loads((DATA / "programma.json").read_text(encoding="utf-8"))
DAGEN = list(PROGRAMMA["dagen"].keys())  # vrijdag, zaterdag, zondag

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

# Menu zoals op de oude site (Home staat apart in header()). Tickets is een aparte knop rechts.
MENU = [
    ("programma", "Festival", f"/{DAGEN[0]}/"),   # alleen in festivalmodus, met de dagen als submenu
    ("over-ons", "Over ons", "/over-ons/"),
    ("praktisch", "Praktisch", "/praktisch/"),
    ("vrijwilligers", "Vrijwilligers", "/vrijwilligers/"),
]
if not FESTIVAL:
    MENU = [m for m in MENU if m[0] != "programma"]

PLAATS = "Genebos, Ham"

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


def header(nav, dag=""):
    actief = ' aria-current="page"'
    regels = []
    for key, label, href in MENU:
        if key == "programma":
            sub = "".join(
                f'<li><a href="/{d}/"{actief if d == dag else ""}>{PROGRAMMA["dagen"][d]["titel"]}</a></li>'
                for d in DAGEN)
            regels.append(
                f'        <li class="heeft-sub alleen-festival"><a href="{href}"{actief if key == nav else ""}>{label}</a>'
                f'<ul class="sub">{sub}</ul></li>')
        elif key == "concerten":
            # Evenementen enkel buiten festivalmodus
            if PREVIEW:
                regels.append(f'        <li class="alleen-normaal"><a href="{href}"{actief if key == nav else ""}>{label}</a></li>')
            elif not FESTIVAL:
                regels.append(f'        <li><a href="{href}"{actief if key == nav else ""}>{label}</a></li>')
        else:
            regels.append(f'        <li><a href="{href}"{actief if key == nav else ""}>{label}</a></li>')
    items = "\n".join(regels)
    tickets_actief = actief if nav == "tickets" else ""
    return f"""<a class="skip" href="#inhoud">Ga naar de inhoud</a>
<header class="site-header">
  <div class="wrap kop">
    <a class="brand" href="/" aria-label="Folkfestival Ham — naar de homepagina">
      <img src="/assets/img/logo.webp" width="800" height="211" alt="Folkfestival Ham">
    </a>
    <nav class="nav" id="hoofdmenu" aria-label="Hoofdmenu">
      <ul>
        <li><a href="/"{actief if nav == "home" else ""}>Home</a></li>
{items}
      </ul>
      <div class="nav-extra">
        <a class="btn btn-groen" href="/tickets/">Tickets</a>
        {SOCIALS}
      </div>
    </nav>
    <div class="menu-scherm" aria-hidden="true"></div>
    <div class="kop-rechts">
      <a class="btn btn-tickets" href="/tickets/"{tickets_actief}>Tickets</a>
      <button class="menu-knop" type="button" aria-expanded="false" aria-controls="hoofdmenu" aria-label="Menu"><span class="hamburger" aria-hidden="true"></span></button>
    </div>
  </div>
</header>"""


# Vlaggetjeslijn bovenaan de footer. De lijn hangt door in bogen van 6 vlaggetjes (240px);
# elk vlaggetje krijgt de hoogte van de lijn op zijn plek en wiegt zachtjes.
VLAG_KLEUREN = ["var(--rood)", "var(--wit)", "var(--blauw)", "var(--groen-donker)", "var(--bruin)"]  # kleuren van het mannetje


def vlaggetjes(aantal=66):
    import math
    vlaggen = []
    for i in range(aantal):
        k = i % 6
        y = round(14 * math.sin(math.pi * (k * 40 + 18) / 240), 1)
        kleur = VLAG_KLEUREN[(i * 3) % len(VLAG_KLEUREN)]
        vlaggen.append(f'<i style="--y:{y}px;--k:{kleur};--d:{(i % 7) * -0.37:.2f}s"></i>')
    return '<div class="vlaggetjes" aria-hidden="true">' + "".join(vlaggen) + "</div>"


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
    return f"""<footer class="site-footer textuur">
  {vlaggetjes()}
  <section class="sponsors" aria-label="Partners en sponsors">
    <p class="sponsors-titel">Met dank aan onze partners</p>
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
  <div class="footer-in">
    <img class="logo" src="/assets/img/logo.webp" width="800" height="211" alt="Folkfestival Ham" loading="lazy">
    {SOCIALS}
    <ul class="contact">
      <li>{ICON['huis']}<a href="https://www.celticartgallery.be">The Celtic Art Gallery vzw</a></li>
      <li>{ICON['pin']}<a href="https://maps.google.com/?q=Genebosstraat+4,+3945+Ham">Genebosstraat 4, 3945 Genebos</a></li>
      <li>{ICON['mail']}<a href="mailto:info@folkfestivalham.be">info@folkfestivalham.be</a></li>
      <li>{ICON['tel']}<a href="tel:+3213671373">+32 (0)13 67 13 73</a></li>
    </ul>
  </div>
  <div class="footer-onder">
    <p class="klein">© {jaar} The Celtic Art Gallery vzw · BE 0458.144.856 · Foto's: Jeroen De Bie · <a href="/voorwaarden/">Voorwaarden</a> · <a href="/privacy/">Privacy</a></p>
    <a class="naar-boven" href="#" aria-label="Terug naar boven"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5 4 13l1.4 1.4L11 8.8V20h2V8.8l5.6 5.6L20 13z"/></svg></a>
  </div>
</footer>
<script>
  (function () {{
    var kop = document.querySelector('.site-header'), knop = document.querySelector('.menu-knop');
    var zetMenu = function (open) {{
      kop.classList.toggle('open', open);
      document.body.classList.toggle('menu-open', open);
      knop.setAttribute('aria-expanded', open ? 'true' : 'false');
      knop.setAttribute('aria-label', open ? 'Menu sluiten' : 'Menu');
    }};
    if (knop) {{
      knop.addEventListener('click', function () {{ zetMenu(!kop.classList.contains('open')); }});
      var scherm = document.querySelector('.menu-scherm');
      if (scherm) scherm.addEventListener('click', function () {{ zetMenu(false); }});
      document.addEventListener('keydown', function (ev) {{ if (ev.key === 'Escape') zetMenu(false); }});
    }}
    // Ankerlinks (#fotos, #line-up ...): spring naar het zichtbare exemplaar (in de preview staan beide versies op de pagina)
    document.addEventListener('click', function (ev) {{
      var a = ev.target.closest && ev.target.closest('a[href^="#"]');
      if (!a || a.getAttribute('href').length < 2) return;
      var doel = [].slice.call(document.querySelectorAll('[id="' + a.getAttribute('href').slice(1) + '"]')).filter(function (el) {{ return el.offsetParent; }})[0];
      if (doel) {{ ev.preventDefault(); doel.scrollIntoView({{ behavior: 'smooth' }}); history.replaceState(null, '', a.getAttribute('href')); }}
    }});
    // Schaduw onder de kop zodra je scrolt
    var zet = function () {{ kop.classList.toggle('gescrold', window.scrollY > 8); }};
    window.addEventListener('scroll', zet, {{ passive: true }}); zet();
    // Video's laden pas na een klik (youtube-nocookie), zodat er niets van YouTube laadt zonder actie
    document.querySelectorAll('.video[data-yt]').forEach(function (v) {{
      v.addEventListener('click', function () {{
        var f = document.createElement('iframe');
        f.src = 'https://www.youtube-nocookie.com/embed/' + v.dataset.yt + '?autoplay=1&rel=0';
        f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
        f.allowFullscreen = true; f.title = v.getAttribute('aria-label') || 'Video';
        var w = document.createElement('div'); w.className = 'video video-actief'; w.appendChild(f);
        v.replaceWith(w);
      }});
    }});
  }})();
</script>"""


def oproep(modus=None):
    """Vaste band onderaan elke pagina (boven de sponsors)."""
    if PREVIEW and modus is None:
        return (f'<div class="alleen-festival">{oproep("festival")}</div>'
                f'<div class="alleen-normaal">{oproep("normaal")}</div>')
    if (modus or ("festival" if FESTIVAL else "normaal")) == "festival":
        return f"""<section class="oproep" aria-label="Tickets">
  <div class="wrap oproep-in">
    <div><strong>Folkfestival Ham</strong><span>{e(DATUM_FESTIVAL)} · {PLAATS}</span></div>
    <div class="knoppen"><a class="btn btn-groen" href="/tickets/">Tickets</a><a class="btn btn-licht" href="/{DAGEN[0]}/">Line-up</a></div>
  </div>
</section>"""
    return f"""<section class="oproep" aria-label="Volg ons">
  <div class="wrap oproep-in">
    <div><strong>Tot volgend jaar!</strong><span>Volg ons en hoor als eerste de nieuwe line-up.</span></div>
    <div class="knoppen"><a class="btn btn-licht" href="https://www.facebook.com/FolkfestivalHam/">{ICON["facebook"]}Facebook</a><a class="btn btn-licht" href="https://www.instagram.com/FolkfestivalHam/">{ICON["instagram"]}Instagram</a></div>
  </div>
</section>"""


def schakelbalk():
    if not PREVIEW:
        return ""
    return """<div class="schakelbalk" role="region" aria-label="Preview-instelling">
  <span class="schakelbalk-label">Preview</span>
  <span class="schakelbalk-tekst">Festival mode</span>
  <button class="schakelaar" type="button" role="switch" aria-checked="true"><span class="schakelaar-knop"></span><span class="schakelaar-aan">ON</span><span class="schakelaar-uit">OFF</span></button>
  <span class="schakelbalk-uitleg">Enkel zichtbaar op de preview</span>
</div>
<script>
(function () {
  var r = document.documentElement, k = 'ffh-preview-modus', m = 'festival';
  try { m = localStorage.getItem(k) || 'festival'; } catch (e) {}
  r.dataset.modus = m;
  var b = document.querySelector('.schakelaar');
  var zet = function (x) { r.dataset.modus = x; b.setAttribute('aria-checked', x === 'festival' ? 'true' : 'false'); try { localStorage.setItem(k, x); } catch (e) {} };
  zet(m);
  b.addEventListener('click', function () { zet(r.dataset.modus === 'festival' ? 'normaal' : 'festival'); });
})();
</script>"""


def kleur_secties(body):
    """Zet afwisselend wit/groen op de secties (na hero of titel eerst wit). Per variant apart geteld."""
    def per_stuk(stuk):
        n = [0]
        def zet(m):
            tag = m.group(0)
            if re.search(r'class="[^"]*(hero|paginatitel|oproep)', tag):
                n[0] = 0
                return tag
            n[0] += 1
            kl = "vlak-wit" if n[0] % 2 else "vlak-groen"
            return re.sub(r'class="', f'class="{kl} ', tag, count=1) if 'class="' in tag else tag.replace("<section", f'<section class="{kl}"', 1)
        return re.sub(r"<section\b[^>]*>", zet, stuk)
    delen = re.split(r'(<div class="alleen-(?:festival|normaal)">)', body)
    return "".join(d if d.startswith('<div class="alleen-') else per_stuk(d) for d in delen)


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
{schakelbalk()}
{header(meta.get('nav', ''), meta.get('dag', ''))}
<main id="inhoud">
{kleur_secties(body.strip())}
{"" if meta.get("cta") == "geen" else oproep()}
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


# ---------- Festivalmodus: programma, line-up en dagpagina's ----------

def e(t):
    return html.escape(t or "", quote=True)


def artiest_id(a):
    import re, unicodedata
    t = unicodedata.normalize("NFKD", a["naam"]).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


TICKETS_FESTIVAL = "/tickets/#!/Festival/c/126605753"

ICON["klok"] = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16zm.5-13H11v6l5.2 3.1.8-1.2-4.5-2.7z"/></svg>'
ICON["bal"] = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16zm0-12a4 4 0 1 0 0 8 4 4 0 0 0 0-8z"/></svg>'
ICON["web"] = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm6.9 6h-2.9a15.7 15.7 0 0 0-1.4-3.6A8 8 0 0 1 18.9 8zM12 4c.8 1.2 1.5 2.5 1.9 4h-3.8c.4-1.5 1.1-2.8 1.9-4zM4.3 14a8.2 8.2 0 0 1 0-4h3.4a16.5 16.5 0 0 0 0 4zm.8 2h2.9c.3 1.3.8 2.5 1.4 3.6A8 8 0 0 1 5.1 16zM8 8H5.1a8 8 0 0 1 4.3-3.6C8.8 5.5 8.4 6.7 8 8zm4 12c-.8-1.2-1.5-2.5-1.9-4h3.8c-.4 1.5-1.1 2.8-1.9 4zm2.3-6H9.7a14.7 14.7 0 0 1 0-4h4.6a14.7 14.7 0 0 1 0 4zm.3 5.6c.6-1.1 1.1-2.3 1.4-3.6h2.9a8 8 0 0 1-4.3 3.6zm1.7-5.6a16.5 16.5 0 0 0 0-4h3.4a8.2 8.2 0 0 1 0 4z"/></svg>'


# Icoontjes voor de inhoudspagina's: in een pagina schrijf je {{ICOON:naam}}
ICOONTJES = {
    "blad": "M17 8C8 10 5.9 16.2 3.8 21.3l1.9.7.9-2.3c.5.2 1 .3 1.4.3C19 20 22 3 22 3c-1 2-8 2.3-13 3.3S2 11.5 2 13.5s1.8 3.8 1.8 3.8C7 8 17 8 17 8z",
    "wortel": "M16 3c-1 0-2 .6-2.5 1.5C13 3.6 12 3 11 3c0 1.3.8 2.4 2 2.8l-.2.2C10 8.9 4 19 4 19s10.1-6 13-8.8l.2-.2c.4 1.2 1.5 2 2.8 2 0-1-.6-2-1.5-2.5.9-.5 1.5-1.5 1.5-2.5-1 0-2 .6-2.5 1.5V8.5c0-1-.6-2-1.5-2.5.9-.5 1.5-1.5 1.5-2.5z",
    "hart": "M12 21.4 10.6 20C5.4 15.4 2 12.3 2 8.5 2 5.4 4.4 3 7.5 3c1.7 0 3.4.8 4.5 2.1C13.1 3.8 14.8 3 16.5 3 19.6 3 22 5.4 22 8.5c0 3.8-3.4 6.9-8.6 11.5z",
    "fles": "M7 2h10v2H7zm2 3h6l2 4v11a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2V9zm-.6 5L3 4.4 4.4 3l17 17-1.4 1.4z",
    "bord": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zm0 15a6 6 0 1 1 0-12 6 6 0 0 1 0 12zM2 2h2v8H2zm18 0h2v20h-2z",
    "fiets": "M5 20.5A3.5 3.5 0 1 1 5 13.5a3.5 3.5 0 0 1 0 7zm0-5.5a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm14 5.5a3.5 3.5 0 1 1 0-7 3.5 3.5 0 0 1 0 7zm0-5.5a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM15.5 5.5a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM12 7l-4 4 3 3v5h2v-6l-2.2-2 2.3-2.3L14.8 11H18V9h-2.5z",
    "auto": "M18.9 6c-.2-.6-.8-1-1.4-1h-11c-.7 0-1.2.4-1.4 1L3 12v8c0 .6.4 1 1 1h1c.6 0 1-.4 1-1v-1h12v1c0 .6.4 1 1 1h1c.6 0 1-.4 1-1v-8zM6.5 16a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm11 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zM5 11l1.5-4.5h11L19 11z",
    "bus": "M4 16c0 .9.4 1.7 1 2.2V20c0 .6.4 1 1 1h1c.6 0 1-.4 1-1v-1h8v1c0 .6.4 1 1 1h1c.6 0 1-.4 1-1v-1.8c.6-.5 1-1.3 1-2.2V6c0-3.5-3.6-4-8-4s-8 .5-8 4zm3.5 1a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm9 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm1.5-6H6V6h12z",
    "tent": "M12 2 1 21h22zm0 4.2L19.6 19H15l-3-6-3 6H4.4z",
    "bed": "M7 13a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm12-6h-8v7H3V5H1v15h2v-3h18v3h2v-9a4 4 0 0 0-4-4z",
    "vraag": "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm1 17h-2v-2h2zm2.1-7.8-.9.9c-.7.7-1.2 1.3-1.2 2.9h-2v-.5c0-1.1.4-2.1 1.2-2.8l1.2-1.3a2 2 0 1 0-3.4-1.4H8a4 4 0 1 1 7.1 2.2z",
    "pin": "M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z",
    "ticket": "M22 10V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v4a2 2 0 0 1 0 4v4a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-4a2 2 0 0 1 0-4zm-7 7.5h-2v-2h2zm0-4.5h-2v-2h2zm0-4.5h-2v-2h2z",
    "glas": "M7.5 7 5.8 2h12.4l-1.7 5zM5 2h14l-2 18a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2z",
    "shirt": "M16 3h-1.2a3 3 0 0 1-5.6 0H8L2 6l2 5 3-1v11h10V10l3 1 2-5z",
    "mensen": "M16 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-8 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0 2c-2.3 0-7 1.2-7 3.5V19h14v-2.5C15 14.2 10.3 13 8 13zm8 0c-.3 0-.6 0-1 .1 1.2.8 2 1.9 2 3.4V19h6v-2.5c0-2.3-4.7-3.5-7-3.5z",
    "ster": "M12 17.3 18.2 21l-1.6-7L22 9.2l-7.2-.6L12 2 9.2 8.6 2 9.2 7.5 14l-1.7 7z",
    "muziek": "M12 3v10.6A4 4 0 1 0 14 17V7h4V3z",
    "hamer": "M2 19.6 13.4 8.2l2.4 2.4L4.4 22zM14.8 2.4l6.8 6.8-2.8 2.8-1.4-1.4-1.4 1.4-4.2-4.2 1.4-1.4L11.8 5z",
    "kind": "M12 6a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm7 3h-5.5v13h-2v-6h-3v6h-2V9H1V7h18z",
}


def icoon(naam):
    pad = ICOONTJES.get(naam, ICOONTJES["ster"])
    return f'<span class="icoon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="{pad}"/></svg></span>'


def social_icoon(url):
    u = (url or "").lower()
    if "facebook.com" in u:
        return ICON["facebook"], "Facebook"
    if "instagram.com" in u:
        return ICON["instagram"], "Instagram"
    if "youtube.com" in u or "youtu.be" in u:
        return ICON["youtube"], "YouTube"
    return ICON["web"], "Website"


ICON["ticket"] = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22 10V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v4a2 2 0 0 1 0 4v4a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-4a2 2 0 0 1 0-4zm-7 7.5h-2v-2h2zm0-4.5h-2v-2h2zm0-4.5h-2v-2h2z"/></svg>'


def handle(url):
    """Korte naam voor een social link: @pagina of domeinnaam."""
    from urllib.parse import urlparse, unquote
    u = urlparse(url or "")
    host = u.netloc.lower().removeprefix("www.")
    delen = [unquote(x) for x in u.path.split("/") if x]
    if host in ("facebook.com", "instagram.com", "m.facebook.com"):
        if delen and delen[0] == "people" and len(delen) > 1:
            return delen[1].replace("-", " ")
        return "@" + delen[0] if delen else host
    return host


def media(a):
    """Vierkant beeld zoals op de oude site. Video laadt pas na een klik."""
    if a.get("youtube"):
        return (f'<button class="video" type="button" data-yt="{e(a["youtube"])}" aria-label="Speel video van {e(a["naam"])}">'
                f'<img src="{e(a["foto"])}" alt="" loading="lazy" width="720" height="720"><span class="play" aria-hidden="true"></span></button>')
    if a.get("foto"):
        return f'<img class="artiest-foto" src="{e(a["foto"])}" alt="{e(a["naam"])}" loading="lazy" width="720" height="720">'
    return ""


def dag_tabs(actief):
    items = "".join(
        f'<a href="/{d}/"{" aria-current=\"page\"" if d == actief else ""}>{e(PROGRAMMA["dagen"][d]["titel"])}</a>'
        for d in DAGEN)
    return f'<nav class="dagtabs" aria-label="Festivaldagen">{items}</nav>'


def dagpagina(dag):
    info = PROGRAMMA["dagen"][dag]
    blokken = []
    for a in PROGRAMMA["artiesten"].get(dag, []):
        tekst = "".join(f"<p>{e(t)}</p>" for t in a.get("tekst", []))
        tent = "Bal tent" if a.get("bal") else "Grote tent"
        info_regels = f'<li><span class="tent{" tent-bal" if a.get("bal") else ""}">{tent}</span></li>'
        if a.get("tijd"):
            info_regels += f'<li>{ICON["klok"]}{e(a["tijd"])}</li>'
        social = ""
        if a.get("website"):
            ico, lbl = social_icoon(a["website"])
            social = f'<a class="pil pil-social" href="{e(a["website"])}" target="_blank" rel="noopener" aria-label="{lbl} van {e(a["naam"])}">{ico}<span>{e(handle(a["website"]))}</span></a>'
        blokken.append(f"""<article class="artiest" id="{artiest_id(a)}">
  <div class="artiest-media">{media(a)}</div>
  <div class="artiest-tekst">
    <h2>{e(a["naam"])} <span class="vlag">{a.get("vlag","")}</span></h2>
    {tekst}
    <div class="artiest-voet">
      <ul class="artiest-info">{info_regels}</ul>
      <div class="artiest-acties">{social}</div>
    </div>
  </div>
</article>""")
    body = f"""<section class="paginatitel textuur" style="--titelfoto:url(/assets/img/2026/draailier-accordeon.webp)"><h1>Festival programma</h1></section>
<section class="sectie">
  <div class="wrap">
    {dag_tabs(dag)}
    {"".join(blokken)}
    <p class="dag-tickets"><a class="btn btn-groen btn-groot" href="{TICKETS_FESTIVAL}">{ICON["ticket"]}Tickets voor {e(info["titel"].lower())}</a></p>
  </div>
</section>"""
    meta = {"title": f'Programma {info["titel"].lower()}',
            "description": f'Het programma van Folkfestival Ham op {info["titel"].lower()} {info.get("datum","")}: ' + ", ".join(a["naam"] for a in PROGRAMMA["artiesten"].get(dag, [])) + ".",
            "path": f"/{dag}/", "nav": "programma", "dag": dag}
    return meta, body


def _minuten(tijd):
    u, m = (tijd or "0u00").lower().replace(":", "u").split("u")
    return int(u) * 60 + int(m or 0)


def hero_artiesten():
    """Festival-hero: mozaïek van alle artiestfoto's als achtergrond + één traag lint met namen en ronde foto's."""
    acts = [(d, a) for d in DAGEN for a in PROGRAMMA["artiesten"].get(d, [])]
    if not acts:
        return ""
    tegels = "".join(f'<span style="background-image:url({e(a["foto"])})"></span>' for d, a in acts if a.get("foto"))
    mozaiek = f'<div class="hero-mozaiek" aria-hidden="true">{tegels}{tegels}</div>'
    def stuk(d, a):
        img = f'<img src="{e(a["foto"])}" alt="" width="720" height="720">' if a.get("foto") else ""
        return (f'<a class="lint-item" href="/{d}/#{artiest_id(a)}" tabindex="-1">{img}'
                f'<span>{e(a["naam"])}</span><i class="vlag">{a.get("vlag","")}</i></a><b class="lint-ster" aria-hidden="true">✦</b>')
    inhoud = "".join(stuk(d, a) for d, a in acts)
    lint = (f'<div class="linten" aria-hidden="true"><div class="lint lint-1"><div class="lint-band">'
            f'<div class="lint-reeks">{inhoud}</div><div class="lint-reeks" aria-hidden="true">{inhoud}</div></div></div></div>')
    return mozaiek + lint


GALERIJ = [
    ("dansen-in-de-tent", "Dansen in de tent", "breed"), ("drummer", "Drummer op het podium", "hoog"),
    ("zandbak", "Kinderen spelen in de zandbak", ""), ("knutselen", "Knutselen in de kinderzone", ""),
    ("duim-omhoog", "Duim omhoog in de tent", ""), ("accordeonist", "Accordeonist op het podium", "hoog"),
    ("plezier", "Plezier tussen vrijwilligers", ""), ("kader-1", "Vrijwilliger met een gouden kader", ""),
]


def galerij_html():
    """Kleine fotogalerij op de homepage, met link naar alle foto's op Facebook. Klik = groter bekijken."""
    tegels = "".join(
        f'<a class="gal-foto {vorm}" href="/assets/img/2026/{f}.webp" data-alt="{e(alt)}"><img src="/assets/img/2026/{f}.webp" alt="{e(alt)}" loading="lazy"></a>'
        for f, alt, vorm in GALERIJ)
    return f"""<section class="sectie galerij" id="fotos">
  <div class="wrap">
    <div class="intro">
      <span class="kicker">Sfeerbeelden</span>
      <h2>Zo voelt Folkfestival Ham</h2>
    </div>
    <div class="gal">{tegels}</div>
    <p class="knoppen midden"><a class="btn btn-zwart" href="https://www.facebook.com/FolkfestivalHam/photos" target="_blank" rel="noopener">{ICON["facebook"]}Bekijk alle foto's op Facebook</a></p>
    <p class="gal-credit">Foto's: Jeroen De Bie</p>
  </div>
</section>
<script>
(function () {{
  // Eén gedeeld fotovenster voor de hele pagina (de galerij kan meerdere keren op de pagina staan)
  if (window.ffhGalerij) return; window.ffhGalerij = true;
  var d = document.createElement('dialog'); d.className = 'gal-groot'; d.setAttribute('aria-label', 'Foto');
  d.innerHTML = '<button type="button" class="gal-sluit" aria-label="Sluiten">×</button><img alt="">';
  document.body.appendChild(d);
  var im = d.querySelector('img');
  document.addEventListener('click', function (ev) {{
    var a = ev.target.closest && ev.target.closest('.gal-foto');
    if (!a) return;
    ev.preventDefault(); im.src = a.href; im.alt = a.dataset.alt || '';
    if (d.showModal) d.showModal(); else window.open(a.href, '_blank');
  }});
  d.addEventListener('click', function (ev) {{ if (ev.target === d || ev.target.classList.contains('gal-sluit')) d.close(); }});
}})();
</script>"""


def lineup_html():
    """Line-up als timetable (zoals een agenda): per dag een kolom met twee banen (Grote tent, Bal tent),
    blokken op hun uur. Duur = tot het volgende optreden die dag (max 1u45), laatste optreden 1u30.
    Een vaste eindtijd kan per artiest met het veld "eind" (bv. "21u00") in data/programma.json."""
    alle = [_minuten(a["tijd"]) for d in DAGEN for a in PROGRAMMA["artiesten"].get(d, []) if a.get("tijd")]
    if not alle:
        return ""
    start = (min(alle) // 60) * 60
    eind = -(-(max(alle) + 90) // 60) * 60
    uren = list(range(start, eind + 1, 60))
    schaal = "".join(f'<span style="--t:{(u - start) / 60}">{u // 60:02d}u</span>' for u in uren)
    lijnen = "".join(f'<i style="--t:{(u - start) / 60}"></i>' for u in uren)
    kolommen = []
    for d in DAGEN:
        info = PROGRAMMA["dagen"][d]
        acts = sorted(PROGRAMMA["artiesten"].get(d, []), key=lambda a: _minuten(a.get("tijd")))
        blokken = []
        for i, a in enumerate(acts):
            t0 = _minuten(a["tijd"])
            if a.get("eind"):
                t1 = _minuten(a["eind"])
            elif i + 1 < len(acts):
                t1 = min(_minuten(acts[i + 1]["tijd"]), t0 + 105)
            else:
                t1 = t0 + 90
            baan = "bal" if a.get("bal") else "groot"
            img = f'<img src="{e(a["foto"])}" alt="" loading="lazy" width="720" height="720">' if a.get("foto") else ""
            blokken.append(
                f'<a class="tt-blok tt-{baan}" href="/{d}/#{artiest_id(a)}" style="--van:{(t0 - start) / 60};--duur:{(t1 - t0) / 60}">'
                f'{img}<span class="tt-tijd">{e(a["tijd"])}</span>'
                f'<span class="tt-naam">{e(a["naam"])} <span class="vlag">{a.get("vlag","")}</span></span></a>')
        kolommen.append(
            f'<div class="tt-dag" data-dag="{d}"><h3><a href="/{d}/">{e(info["titel"])} <span>{e(info.get("datum",""))}</span></a></h3>'
            f'<div class="tt-banen"><span class="tt-baankop">Grote tent</span><span class="tt-baankop tt-baankop-bal">Bal tent</span></div>'
            f'<div class="tt-raster">{lijnen}{"".join(blokken)}</div></div>')
    knoppen = "".join(f'<button type="button" data-dag="{d}"{" aria-pressed=\"true\"" if i == 0 else ""}>{e(PROGRAMMA["dagen"][d]["titel"])}</button>' for i, d in enumerate(DAGEN))
    return (f'<div class="tt" style="--uren:{(eind - start) / 60}">'
            f'<div class="tt-keuze" role="group" aria-label="Kies een dag">{knoppen}</div>'
            f'<div class="tt-in"><div class="tt-schaal" aria-hidden="true">{schaal}</div>{"".join(kolommen)}</div>'
            f'<p class="tt-legende"><span class="tent">Grote tent</span> <span class="tent tent-bal">Bal tent</span> Klik op een optreden voor meer info.</p></div>'
            """<script>(function(){var t=document.querySelector('.tt');if(!t)return;var k=t.querySelectorAll('.tt-keuze button');
function z(d){t.dataset.toon=d;k.forEach(function(b){b.setAttribute('aria-pressed',b.dataset.dag===d?'true':'false');});}
k.forEach(function(b){b.addEventListener('click',function(){z(b.dataset.dag);});});z(k[0].dataset.dag);})();</script>""")


def programma_html():
    kolommen = []
    for d in DAGEN:
        info = PROGRAMMA["dagen"][d]
        rijen = "".join(
            f'<li><span class="tijd">{e(a.get("tijd",""))}</span><span><a href="/{d}/#{artiest_id(a)}">{e(a["naam"])}</a> {a.get("vlag","")}</span>{" <span class=\"tent tent-bal\">Bal tent</span>" if a.get("bal") else " <span class=\"tent\">Grote tent</span>"}</li>'
            for a in PROGRAMMA["artiesten"].get(d, []))
        kolommen.append(f'<div class="dag-kolom"><h3><a href="/{d}/">{e(info["titel"])} {e(info.get("datum",""))}</a></h3><ul>{rijen}</ul></div>')
    return '<div class="programma">' + "".join(kolommen) + "</div>"


def redirects():
    regels = [
        "# Gegenereerd door tools/build.py — niet met de hand aanpassen",
        "# Medewerkers heet nu Vrijwilligers",
        "/medewerkers /vrijwilligers/ 301",
        "/medewerkers/ /vrijwilligers/ 301",

    ]
    if not FESTIVAL:
        regels += ["", "# Festivalmodus uit: dagpagina's sturen naar de homepage"]
        for d in DAGEN:
            regels += [f"/{d} / 302", f"/{d}/ / 302"]
    # Ecwid gebruikt nette adressen (/tickets/Festival-c126605753, /tickets/checkout/...,
    # ook de terugkeer na betaling). Alles onder /tickets/ toont dus de winkelpagina.
    regels += ["", "# Ticketwinkel: elk adres onder /tickets/ toont de winkel (Ecwid leest zelf het adres)",
               "/tickets/* /tickets/ 200"]
    return "\n".join(regels) + "\n"


def main():
    urls = []
    modus = "festival" if FESTIVAL else "normaal"
    # Opkuis: dagpagina's van een vorige build weghalen als de modus uit staat
    for d in DAGEN:
        f = PUBLIC / d / "index.html"
        if f.exists() and not FESTIVAL:
            f.unlink()
            f.parent.rmdir()
    pages = []
    varianten = {}
    for src in sorted(PAGES.glob("*.html")):
        meta, body = read(src)
        if PREVIEW and meta.get("modus"):
            varianten[meta["modus"]] = (meta, body)
            continue
        if meta.get("modus") and meta["modus"] != modus:
            continue
        pages.append((meta, body))
    if PREVIEW and varianten:
        meta = dict(varianten.get("festival", next(iter(varianten.values())))[0])
        body = "".join(f'<div class="alleen-{m}">{b}</div>' for m, (_, b) in varianten.items())
        pages.append((meta, body))
    if FESTIVAL:
        pages += [dagpagina(d) for d in DAGEN]
    for meta, body in pages:
        import re as _re
        body = _re.sub(r"\{\{ICOON:(\w+)\}\}", lambda m: icoon(m.group(1)), body)
        # Paginatitel: foto met filter erachter i.p.v. de groene band
        TITELFOTO = {"/over-ons/": "2026/dansende-armen", "/praktisch/": "camping", "/vrijwilligers/": "2026/kader-2",
                     "/tickets/": "2026/dansen-in-de-tent", "/voorwaarden/": "zonnebloem", "/privacy/": "zonnebloem"}
        foto = meta.get("titelfoto") or TITELFOTO.get(meta["path"], "2026/dansen-in-de-tent")
        body = body.replace('<section class="paginatitel textuur">',
                            f'<section class="paginatitel textuur" style="--titelfoto:url(/assets/img/{foto}.webp)">', 1)
        body = body.replace("{{GALERIJ}}", galerij_html()).replace("{{HERO_ARTIESTEN}}", hero_artiesten()).replace("{{LINEUP}}", lineup_html()).replace("{{PROGRAMMA}}", programma_html()).replace("{{DATUM}}", e(DATUM_FESTIVAL))
        p = meta["path"]
        out = PUBLIC / "404.html" if p == "/404" else PUBLIC / p.strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(meta, body), encoding="utf-8")
        if not meta.get("noindex"):
            urls.append(p)
        print("gebouwd:", out.relative_to(ROOT))
    (PUBLIC / "_redirects").write_text(redirects(), encoding="utf-8")
    today = datetime.date.today().isoformat()
    sm = "\n".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>" for u in sorted(urls))
    (PUBLIC / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}\n</urlset>\n',
        encoding="utf-8")
    # Festivalmodus uit: dagpagina's ook voor zoekmachines afsluiten
    verbod = "" if FESTIVAL else "".join(f"Disallow: /{d}/\nDisallow: /{d}\n" for d in DAGEN)
    (PUBLIC / "robots.txt").write_text(f"User-agent: *\n{verbod}Allow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print(f"gebouwd: _redirects, sitemap.xml, robots.txt  (festivalmodus: {'AAN' if FESTIVAL else 'uit'})")


if __name__ == "__main__":
    main()
