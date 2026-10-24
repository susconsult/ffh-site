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
| `/404.html` | Eigen foutpagina |

Menu-item "Concerten" gaat naar de categorie Concerten in de winkel.

## Hoe aanpassen

- Teksten staan in `pages/*.html`. Header, menu, sponsors en footer staan in `tools/build.py`.
- Na een wijziging: `python3 tools/build.py` — dat schrijft alles in `public/`. **Commit `public/` mee**; Cloudflare bouwt zelf niets.
- Festivaldatum in de header: `DATUM_FESTIVAL` bovenaan `tools/build.py`.
- Sponsors: lijst `SPONSORS` in `tools/build.py`, logo's in `public/assets/img/sponsors/`.
- Push naar `main` = automatisch live na 2–4 minuten.

## Onderdelen

- **Tickets: Ecwid** (winkel-ID `68281592`). Producten, prijzen en bestellingen beheer je in het Ecwid-dashboard, niet hier. Ecwid toont zelf een cookiemelding.
- **Oude winkel-adressen** (`/tickets/Concerten-c126605256` enz.) worden doorverwezen via `public/_redirects`.
- **Lettertypes** (Jost, Roboto) staan lokaal in `public/assets/fonts/` — geen Google Fonts.
- **Geen** meetcodes, Google Tag Manager, Facebook-pixel of ingesloten Google Maps → geen eigen cookiebanner nodig. Komt er meting bij, dan wel.
- Geen formulieren, geen database, geen variabelen in Cloudflare.

## Wat staat waar

| Wat | Waar | Login |
|---|---|---|
| Code | github.com/susconsult/ffh-site | GitHub susconsult |
| Hosting | Cloudflare Worker `ffh-site` (ffh-site.pieter-2d7.workers.dev) | pieter@susconsult.be |
| Tickets | Ecwid, winkel 68281592 | (nog noteren) |
| Domein / DNS | folkfestivalham.be — staat al achter Cloudflare, account nog na te kijken | (nog noteren) |
| E-mail | info@ en medewerkers@folkfestivalham.be | (nog noteren) |

## Open punten

- [ ] Domein aan de Worker hangen (en `www` doorverwijzen) — eerst nakijken in welk Cloudflare-account het domein zit en waar de mail loopt.
- [ ] In Ecwid de winkel-URL op `https://folkfestivalham.be/tickets/` laten staan (links in bevestigingsmails).
- [ ] Nieuwsbrief: het oude formulier bewaarde inschrijvingen in WordPress. Beslissen: weg laten, of opnieuw (bv. naar een Google Sheet). Nu staat er een "volg ons"-band.
- [ ] Oude nieuwsbrief-inschrijvingen uit WordPress exporteren vóór WordPress weggaat.
- [ ] Ondernemingsnummer van de vzw toevoegen in de footer.
- [ ] Line-up en datum 2027 zodra gekend.
