# Folkfestival Ham — folkfestivalham.be

Wolfpakket-site (SUS Consult) voor **Folkfestival Ham**, georganiseerd door **The Celtic Art Gallery vzw**, Genebosstraat 4, 3945 Genebos.
Vervangt de oude WordPress/Elementor-site. Gewone statische HTML, geen framework.

## Pagina's

| Adres | Inhoud |
|---|---|
| `/` | Home: "Bedankt! Tot volgend jaar", drie blokken, volg-ons-band, zonnebloem |
| `/over-ons/` | Duurzaamheid, meewerken |
| `/praktisch/` | Route, camping, overnachten (logies-logo's), FAQ (`/praktisch/#faq`) |
| `/medewerkers/` | Oproep medewerkers, mail naar medewerkers@folkfestivalham.be |
| `/tickets/` | Ecwid-winkel (tickets) |
| `/vrijdag/`, `/zaterdag/`, `/zondag/` | Dagprogramma — alleen in festivalmodus |
| `/voorwaarden/`, `/privacy/` | Overgenomen van de oude site (nodig voor de ticketverkoop) |
| `/whiskytasting` | Korte link naar de verborgen Whiskytasting in de winkel |
| `/404.html` | Eigen foutpagina |

## Opbouw en stijl (afgekeken van grote festivals)

- **Header:** zwarte topbalk (datum · plaats · socials), groene band met logo, wit menu dat blijft plakken.
- **Menu:** Home · Line-up (Vr/Za/Zo, alleen festivalmodus) · Info · Over ons · Meewerken, en rechts altijd de groene knop **Tickets**.
- **Elke pagina:** groene titelband → inhoud → zwarte oproep-band (festivalmodus: Tickets + Line-up; anders: volg ons) → sponsors → footer. Overslaan met `cta: geen` bovenaan een pagina.
- **Knoppen:** `btn btn-groen` = hoofdactie (tickets), `btn btn-zwart` = gewone actie, `btn btn-licht` = op donker/foto. Oranje alleen als accent (uren, label Bal tent). Geen oranje knoppen meer.
- Pagina "Praktisch" heet in het menu **Info**, "Medewerkers" heet **Meewerken** (adressen blijven /praktisch/ en /medewerkers/).

## Festivalmodus (de schakelaar)

In `data/instellingen.json`:

```json
{ "festivalmodus": true, "datum_festival": "14 - 15 - 16 augustus 2026" }
```

- **Aan** (`true`): homepage met de line-up per dag — line-up en blokkenschema in één (`pages/home-festival.html`), menu-item "Line-up", en de dagpagina's `/vrijdag/`, `/zaterdag/`, `/zondag/`.
- **Uit** (`false`): homepage "Bedankt! Tot volgend jaar" (`pages/home.html`), geen dagpagina's; `/vrijdag/` enz. sturen naar de homepage.
- Daarna `python3 tools/build.py`, committen en pushen. Of vraag Claude: "zet festivalmodus aan/uit".

**Programma** staat in `data/programma.json`: per dag de artiesten met naam, vlag, tijd, `bal` (true = label "Bal tent", false = "Grote tent"), website, YouTube-code, foto en tekst. Foto's in `public/assets/img/artiesten/` (16:9). Video's laden pas na een klik (youtube-nocookie), dus geen cookiebanner nodig.

## Hoe aanpassen

- Teksten staan in `pages/*.html`. Header, menu, sponsors en footer staan in `tools/build.py`.
- Na een wijziging: `python3 tools/build.py` — dat schrijft alles in `public/`. **Commit `public/` mee**; Cloudflare bouwt zelf niets.
- Festivaldatum in de header: `DATUM_FESTIVAL` bovenaan `tools/build.py`.
- Sponsors: lijst `SPONSORS` in `tools/build.py`, logo's in `public/assets/img/sponsors/`.
- Push naar `main` = automatisch live na 2–4 minuten.

## Onderdelen

- **Tickets: Ecwid** (winkel-ID `68281592`). Producten, prijzen en bestellingen beheer je in het Ecwid-dashboard, niet hier. Ecwid toont zelf een cookiemelding.
- **Whiskytasting staat niet in het categorie-overzicht** (CSS-regel in `style.css`, categorie 142997555), maar is wel bereikbaar via de directe link `folkfestivalham.be/whiskytasting` (doorverwijzing in `_redirects`). Weer tonen in het overzicht: de CSS-regel weghalen.
- **Doorverwijzingen** (oude winkel-adressen, `/whiskytasting`, dagpagina's buiten festivalmodus) worden door `tools/build.py` in `public/_redirects` geschreven — niet met de hand aanpassen.
- **Lettertypes** (Jost, Roboto) staan lokaal in `public/assets/fonts/` — geen Google Fonts.
- **Google Maps** is ingesloten op `/praktisch/` (gewone embed, geen API-sleutel nodig).
- **Geen** meetcodes, Google Tag Manager of Facebook-pixel.
- Geen formulieren, geen database, geen variabelen in Cloudflare.

## Wat staat waar

| Wat | Waar | Login |
|---|---|---|
| Code | github.com/susconsult/ffh-site | GitHub susconsult |
| Hosting | Cloudflare Worker `ffh-site` (ffh-site.pieter-2d7.workers.dev) | pieter@susconsult.be |
| Tickets | Ecwid, winkel 68281592 | (nog noteren) |
| Domein / DNS | folkfestivalham.be — staat al achter Cloudflare, account nog na te kijken | (nog noteren) |
| E-mail | info@ en medewerkers@folkfestivalham.be | (nog noteren) |

## Bron oude site

`bron-oude-site/` bevat de gescrapete teksten van de WordPress-site (incl. Media/foto's 2018–2023 en "Hoeveelheden en weetjes"). Niet gepubliceerd; alleen ter referentie.

## Open punten

- [ ] Domein aan de Worker hangen (en `www` doorverwijzen) — eerst nakijken in welk Cloudflare-account het domein zit en waar de mail loopt.
- [ ] In Ecwid de winkel-URL op `https://folkfestivalham.be/tickets/` laten staan (links in bevestigingsmails).
- [ ] Nieuwsbrief: het oude formulier bewaarde inschrijvingen in WordPress. Beslissen: weg laten, of opnieuw (bv. naar een Google Sheet). Nu staat er een "volg ons"-band.
- [ ] Oude nieuwsbrief-inschrijvingen uit WordPress exporteren vóór WordPress weggaat.
- [ ] Line-up en datum 2027 zodra gekend.
