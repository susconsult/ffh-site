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
    ("gezinsbond", "Gezinsbond", None),
    ("sponsor-nicotours", "Nico Tours", None),
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
    <p class="klein">© {jaar} The Celtic Art Gallery vzw · BE 0458.144.856 · Foto's: Jeroen De Bie · <a href="/voorwaarden/">Voorwaarden</a> · <a href="/privacy/">Privacy</a> · <a class="sus-credit" href="https://susconsult.be/" target="_blank" rel="noopener" aria-label="Made with love by SUS Consult"><span>Made with</span><span class="sus-credit-h" aria-hidden="true">♥</span><span>by</span><svg viewBox="0 0 1695 343" aria-hidden="true"><path class="sus-credit-m" fill-rule="evenodd" pathLength="1" d="M182.0 337.7C181.9 335.9 181.8 326.3 181.7 316.2C181.5 304.5 181.8 297.6 182.5 297.1C184.5 295.5 305.4 234.5 307.1 234.2C311.7 233.4 323.2 242.1 326.1 248.5C329.6 256.1 328.4 262.3 322.3 269.1C319.1 272.6 310.9 277.1 267.5 298.7C239.5 312.8 208.7 328.0 199.2 332.6L182.0 340.9L182.0 337.7ZM101.0 306.6C89.7 300.4 65.2 286.9 46.5 276.6C27.8 266.3 11.0 256.4 9.2 254.7C2.4 248.2 1.9 246.2 2.2 225.0L2.5 206.1L25.5 218.6C38.1 225.5 63.8 239.5 82.5 249.7C153.8 288.6 149.0 285.4 149.0 292.9C149.0 303.1 134.2 318.1 124.3 317.9C122.7 317.9 112.8 313.1 101.0 306.6ZM130.1 265.5L112.8 256.2L112.4 180.3C112.2 138.6 112.3 100.9 112.6 96.4L113.2 88.4L131.1 79.1L149.0 69.8L149.0 172.4C149.0 228.8 148.7 275.0 148.2 274.9C147.8 274.9 139.7 270.6 130.1 265.5ZM181.9 271.8C181.9 270.0 181.9 221.2 181.8 163.5L181.8 58.5L200.2 48.8L218.5 39.1L218.8 147.2C219.0 233.0 218.7 255.7 217.8 256.6C216.6 257.6 183.3 275.0 182.4 275.0C182.2 275.0 182.0 273.5 181.9 271.8ZM328.8 243.3C325.8 238.0 319.1 233.4 294.9 220.4C282.0 213.5 262.4 202.9 251.2 196.8L231.0 185.8L231.0 163.4C231.0 151.1 231.4 141.0 231.8 141.0C232.3 141.0 235.1 142.3 238.1 143.9C299.6 176.8 321.1 188.7 323.8 191.3C330.6 197.8 331.1 200.1 330.8 224.6C330.5 246.0 330.5 246.4 328.8 243.3ZM89.5 199.3C84.0 196.3 64.7 185.7 46.5 175.8C27.1 165.3 12.0 156.4 9.8 154.3C3.2 147.9 3.0 146.8 3.1 121.8C3.1 100.7 3.2 99.6 4.8 102.0C9.3 108.9 15.4 112.9 45.5 129.2C62.6 138.4 82.0 148.9 88.8 152.6L101.0 159.2L101.0 182.1C101.0 194.7 100.7 205.0 100.2 204.9C99.8 204.8 95.0 202.3 89.5 199.3ZM320.0 134.2C307.7 127.4 260.9 101.8 243.3 92.2L231.0 85.5L231.0 62.2L231.0 38.9L234.0 40.5C235.7 41.4 256.0 52.4 279.3 65.1C324.3 89.6 328.7 92.6 330.9 100.6C332.1 105.0 332.4 140.0 331.2 140.0C330.8 139.9 325.8 137.3 320.0 134.2ZM17.0 108.8C8.7 103.7 5.7 99.3 5.2 91.5C4.7 83.6 7.0 78.1 13.3 72.3C16.1 69.7 36.5 58.6 76.0 38.1C108.2 21.4 136.9 6.5 139.8 4.9L145.0 2.0L145.0 24.8L145.0 47.7L122.8 59.0C67.0 87.4 31.3 106.3 27.8 109.0C25.8 110.7 23.7 112.0 23.3 112.0C22.8 112.0 20.0 110.5 17.0 108.8Z"/><path class="sus-credit-w" fill-rule="evenodd" d="M438.8 212.5C431.6 210.7 422.6 206.2 417.6 201.8L413.7 198.4L420.0 191.2C423.4 187.2 426.4 184.0 426.7 184.0C427.0 184.0 428.9 185.3 430.9 186.9C438.3 192.7 444.9 195.3 453.6 195.8C458.5 196.1 463.2 195.8 465.4 195.0C472.3 192.7 475.0 185.9 471.0 180.7C468.9 178.0 462.6 175.6 448.2 172.0C426.2 166.5 418.5 159.2 418.5 144.0C418.6 134.9 421.2 128.7 427.3 123.5C441.2 111.6 472.6 112.5 488.5 125.4L491.4 127.8L485.7 135.4L479.9 143.0L476.7 140.6C471.3 136.6 465.3 134.0 459.3 133.2C447.6 131.6 439.6 135.3 439.8 142.0C440.0 148.0 442.3 149.4 460.9 154.4C468.3 156.4 476.6 159.3 479.3 160.8C491.8 167.5 496.6 179.8 492.5 193.8C490.4 200.7 483.2 208.0 475.3 211.1C467.9 214.0 447.8 214.8 438.8 212.5ZM581.0 212.7C573.4 210.5 568.7 207.8 563.9 202.8C553.6 192.3 552.0 185.0 552.0 146.2L552.0 117.0L562.5 117.0L573.0 117.0L573.0 145.8C573.0 177.4 573.6 182.0 578.7 188.1C586.1 196.8 601.7 197.4 610.3 189.2C616.5 183.4 616.5 183.4 616.8 148.8L617.1 117.0L627.6 117.0L638.1 117.0L637.8 150.2C637.5 182.1 637.4 183.7 635.2 189.1C630.8 200.2 622.8 208.1 612.5 211.5C605.9 213.8 587.2 214.5 581.0 212.7ZM719.3 212.5C712.4 210.6 704.6 206.6 699.2 202.3L695.0 198.8L697.9 195.2C699.5 193.2 702.4 189.7 704.3 187.5L707.7 183.6L711.6 186.7C719.3 192.7 725.8 195.3 734.6 195.8C739.5 196.1 744.2 195.8 746.4 195.0C753.3 192.7 756.0 185.9 752.0 180.7C749.9 178.0 743.8 175.7 729.0 172.0C717.4 169.1 709.6 165.4 705.6 161.0C696.3 150.7 697.0 133.9 707.2 124.4C720.2 112.1 748.1 111.9 766.9 124.0C769.7 125.7 772.0 127.5 772.0 127.8C772.0 128.1 769.5 131.6 766.5 135.6L761.0 143.0L756.1 139.5C749.6 134.8 743.8 132.8 736.0 132.7C726.3 132.6 721.0 135.9 721.0 142.1C721.0 148.1 724.4 150.2 742.0 154.5C762.3 159.6 771.7 166.4 774.0 177.6C777.4 193.9 769.5 207.0 753.3 212.0C745.4 214.4 727.5 214.7 719.3 212.5ZM885.0 211.4C877.9 209.5 871.8 205.8 865.2 199.6C855.2 190.2 851.0 179.7 851.0 164.6C851.0 154.1 852.7 147.1 857.2 139.2C866.7 122.5 886.7 113.0 906.2 115.9C914.9 117.2 925.8 122.3 932.1 127.9L936.5 131.9L933.8 134.6L931.2 137.3L926.3 133.2C913.2 122.2 896.3 119.6 881.8 126.3C865.6 133.8 855.9 152.9 858.9 171.1C862.3 192.0 878.2 206.0 898.5 206.0C909.4 206.0 918.3 202.4 926.8 194.6L931.1 190.6L933.8 193.4L936.5 196.1L931.5 200.5C925.1 206.1 918.9 209.5 911.5 211.5C904.2 213.4 892.3 213.3 885.0 211.4ZM1019.1 211.4C995.3 205.0 980.0 179.2 985.3 154.4C988.5 139.6 998.2 126.5 1010.4 120.7C1030.1 111.1 1051.7 114.6 1066.8 129.6C1074.1 136.9 1077.5 143.6 1079.8 155.2C1084.8 180.9 1068.2 206.7 1043.2 211.9C1036.0 213.4 1025.7 213.2 1019.1 211.4ZM1291.5 212.0C1282.5 210.1 1271.3 204.4 1266.6 199.1C1265.0 197.3 1265.0 197.1 1267.3 194.5L1269.7 191.7L1275.1 196.1C1278.1 198.6 1283.0 201.7 1286.0 203.0C1290.8 205.2 1292.9 205.5 1303.5 205.5C1315.1 205.5 1315.7 205.4 1321.0 202.4C1333.2 195.6 1334.4 181.0 1323.4 174.0C1320.7 172.4 1313.5 169.9 1304.3 167.5C1280.8 161.5 1274.9 158.6 1270.9 150.8C1267.9 144.9 1268.5 133.9 1272.0 128.6C1282.1 113.6 1311.3 111.2 1330.4 123.7C1333.5 125.8 1336.0 127.7 1336.0 128.0C1336.0 128.3 1334.8 129.8 1333.5 131.3L1331.0 134.1L1327.8 131.5C1316.7 122.2 1298.4 119.7 1286.3 125.9C1281.0 128.6 1278.3 131.8 1276.9 137.1C1275.8 141.3 1275.9 142.1 1277.9 146.3C1280.8 152.3 1286.1 154.9 1303.0 158.9C1324.3 163.9 1331.9 167.8 1335.9 175.8C1343.4 190.8 1334.9 206.8 1316.8 211.6C1311.1 213.1 1298.0 213.3 1291.5 212.0ZM1420.7 212.0C1407.0 208.5 1396.4 197.4 1393.1 182.9C1392.5 180.5 1392.0 164.8 1392.0 147.8L1392.0 117.0L1395.5 117.0L1399.0 117.0L1399.0 146.2C1399.0 178.0 1399.7 183.3 1404.3 191.3C1409.8 200.6 1417.9 205.2 1430.0 205.8C1441.4 206.3 1448.3 203.8 1455.6 196.5C1459.8 192.3 1461.2 190.0 1462.9 184.5C1464.8 178.3 1465.0 175.4 1465.0 147.4L1465.0 117.0L1468.6 117.0L1472.1 117.0L1471.8 150.8L1471.5 184.5L1468.2 191.2C1464.1 199.5 1456.2 207.0 1448.2 210.1C1441.8 212.6 1427.2 213.6 1420.7 212.0ZM1133.0 164.6L1133.0 117.0L1136.9 117.0L1140.9 117.0L1162.2 143.8C1173.9 158.6 1188.5 176.9 1194.5 184.6L1205.5 198.5L1205.8 157.8L1206.0 117.0L1209.5 117.0L1213.0 117.0L1213.0 164.5L1213.0 212.0L1209.6 212.0C1206.9 212.0 1205.7 211.3 1203.4 208.2C1200.7 204.7 1175.6 172.9 1152.5 143.6L1141.5 129.8L1141.0 170.6L1140.5 211.5L1136.8 211.8L1133.0 212.1L1133.0 164.6ZM1528.0 164.5L1528.0 117.0L1532.0 117.0L1536.0 117.0L1536.0 161.0L1536.0 205.0L1563.5 205.0L1591.0 205.0L1591.0 208.5L1591.0 212.0L1559.5 212.0L1528.0 212.0L1528.0 164.5ZM1651.7 211.4C1651.3 211.0 1651.0 191.2 1651.0 167.3L1651.0 124.0L1634.0 124.0L1617.0 124.0L1617.0 120.5L1617.0 117.0L1655.0 117.0L1693.0 117.0L1693.0 120.5L1693.0 124.0L1676.0 124.0L1659.0 124.0L1658.9 166.5C1658.8 189.9 1658.7 209.6 1658.6 210.2C1658.5 211.6 1652.9 212.5 1651.7 211.4ZM1044.8 204.2C1063.0 198.5 1074.0 181.6 1072.8 161.1C1071.7 141.9 1057.3 126.0 1038.2 122.9C1021.8 120.3 1004.3 129.4 997.0 144.4C989.1 160.6 991.2 178.8 1002.6 192.7C1011.8 203.9 1029.8 208.8 1044.8 204.2Z"/></svg></a></p>
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
    # Ticketpagina: geen vaste canonical, want elk product/categorie (/tickets/...-p123) is een eigen pagina; Ecwid zet zelf titel en canonical
    canonical = "" if meta.get("noindex") or meta.get("canonical") == "geen" else f'\n  <link rel="canonical" href="{SITE}{meta["path"]}">'
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
  <link rel="stylesheet" href="/sus-credit.css?v=2">
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
    # Ecwid-pagina's (producten en categorieën), bijgehouden met: node tools/ecwid-paginas.js
    ecwid = ROOT / "data" / "ecwid-paginas.json"
    if ecwid.exists():
        urls += json.loads(ecwid.read_text(encoding="utf-8"))
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
