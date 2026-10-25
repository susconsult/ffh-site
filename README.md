# Folkfestival Ham — folkfestivalham.be

Wolfpakket-site (SUS Consult) voor **Folkfestival Ham**, georganiseerd door **The Celtic Art Gallery vzw**, Genebosstraat 4, 3945 Genebos.
Vervangt de oude WordPress/Elementor-site. Gewone statische HTML, geen framework.

## Pagina's

| Adres | Inhoud |
|---|---|
| `/` | Home: "Bedankt! Tot volgend jaar", volgende evenementen, drie blokken, fotogalerij (+ link naar alle foto's op Facebook) |
| `/over-ons/` | Duurzaamheid, meewerken |
| `/praktisch/` | Route, camping, overnachten (logies-logo's), FAQ (`/praktisch/#faq`) |
| `/vrijwilligers/` | Oproep vrijwilligers, mail naar medewerkers@folkfestivalham.be (oud adres /medewerkers/ stuurt door) |
| `/tickets/` | Ecwid-winkel (tickets) |
| `/vrijdag/`, `/zaterdag/`, `/zondag/` | Dagprogramma — alleen in festivalmodus |
| `/voorwaarden/`, `/privacy/` | Overgenomen van de oude site (nodig voor de ticketverkoop) |
| `/whiskytasting` | Korte link naar de verborgen Whiskytasting in de winkel |
| `/404.html` | Eigen foutpagina |

## Opbouw en stijl (redesign, tak `redesign`)

- **Affiche-stijl** (laatste blok in `style.css`): de site volgt de festivalaffiche. Overal de groene textuur, **zwarte vette letters op groen**, weinig wit. Kaarten zijn licht doorschijnend wit. Rood (pilletje van de affiche) = Tickets en accenten, zwart = gewone knoppen. Secties wisselen af: wit, groen, wit, groen (eerste sectie na titel of foto is wit). Partners in een witte strook boven de footer.

- **Kop:** één balk op de groene textuur die blijft plakken (witte menutekst, actieve pagina donkergroen): logo links, menu (Home · Festival · Evenementen · Over ons · Praktisch · Vrijwilligers; Festival enkel in festivalmodus, Evenementen enkel daarbuiten), groene **Tickets**-knop rechts. Op gsm een menuknop.
- **Elke pagina:** titel op een foto met donkere filter (per pagina een eigen foto, `TITELFOTO` in `tools/build.py`, of `titelfoto: naam` bovenaan een pagina) → inhoud → zonnebloem-band met oproep → footer.
- **Footer:** vlaggetjes (enkel hier), partners in een witte kaart, logo, "Tot in Genebos!", socials, contact, donkergroene onderbalk.
- **Eén kaartstijl:** wit, afgerond (14px), zachte schaduw; op witte secties een dun randje i.p.v. schaduw.
- **Foto's:** organische vormen (geschilderde look), geen schaduw of blok erachter.
- **Menu-indicator:** klein mannetje uit het logo vóór het actieve menu-item (`assets/img/mannetje.webp`).
- **Line-up (homepage, festivalmodus):** timetable zoals een agenda: per dag een kolom met twee banen (Grote tent: groen patroon, zwarte tekst; Bal tent: hetzelfde patroon in roestkleur, witte tekst — `achtergrond-roest.webp`), blokken op hun uur. Duur = tot het volgende optreden (max 1u45), laatste 1u30; een vaste eindtijd kan met het veld `"eind": "21u00"` per artiest in `data/programma.json`. Op gsm één dag tegelijk met dagknoppen.
- **Knoppen:** pilvorm. `btn-groen` = tickets/hoofdactie (witte tekst), `btn-zwart` = gewone actie, `btn-licht` = op foto.
- **Kleurenschema "Mannetje"** (afgeleid van het logo-mannetje en de groene achtergrond; variabelen bovenaan `style.css`): groen `#A2CD4F` (textuur) · donkergroen `#4A7A1F` (knoppen, menu, witte tekst) · rood `#CA4B22` (pilletje op de affiche: Tickets, Bal tent) · blauw `#1A67A9` (broek: Grote tent, links) · bruin `#AB6848` (haar: kleine kopjes) · crème `#FAF1E7` (lichte secties) · zwart · wit.
- **Letterschaal:** 7 maten (`--fs-hero` … `--fs-mini`). Altijd een van die maten gebruiken.

## Festivalmodus (de schakelaar)

**Preview-schakelaar (enkel tak `redesign`):** met `"preview_schakelaar": true` in `data/instellingen.json` bouwt de site beide versies en staat er bovenaan een zwarte balk **FESTIVAL MODE ON/OFF** om te wisselen (de keuze wordt onthouden in de browser). Op de tak `main` wordt die balk altijd uitgeschakeld, ook als de instelling er staat. Voor livegang: instelling weghalen of op `false`.

In `data/instellingen.json`:

```json
{ "festivalmodus": true, "datum_festival": "14 - 15 - 16 augustus 2026" }
```

- **Aan** (`true`): hero met een mozaïek van alle artiestfoto's als achtergrond en één traag lint met namen en ronde foto's onderaan (pauzeert bij hover), homepage met de line-up per dag — line-up en blokkenschema in één (`pages/home-festival.html`), menu-item "Festival", en de dagpagina's `/vrijdag/`, `/zaterdag/`, `/zondag/`.
- **Uit** (`false`): homepage "Bedankt! Tot volgend jaar" met de focus op **Volgende evenementen**: live uit de Ecwid-categorie Concerten (126605256) — nieuwe evenementen verschijnen vanzelf als ze daar in de winkel staan (`pages/home.html`). Dagpagina's bestaan dan niet: `/vrijdag/` enz. sturen naar de homepage, staan niet in de sitemap, er linkt niets naartoe en `robots.txt` verbiedt ze voor zoekmachines.
- Daarna `python3 tools/build.py`, committen en pushen. Of vraag Claude: "zet festivalmodus aan/uit".

**Programma** staat in `data/programma.json`: per dag de artiesten met naam, vlag, tijd, `bal` (true = label "Bal tent", false = "Grote tent"), website, YouTube-code, foto en tekst. Foto's in `public/assets/img/artiesten/` (16:9). Video's laden pas na een klik (youtube-nocookie), dus geen cookiebanner nodig.

## Foto's

- Recente festivalfoto's staan in `public/assets/img/2026/` (© Jeroen De Bie, credit in de footer en onder de galerij).
- Galerij op de homepage: lijst `GALERIJ` in `tools/build.py` (bestandsnaam, alt-tekst, vorm `breed`/`hoog`/leeg). Klik = foto groot.

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
