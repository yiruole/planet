# Ruole Yi — Portfolio Website Progress

**Last updated:** 2026-06-04  
**Branch:** main  
**Remote:** https://github.com/yiruole/planet.git  
**Live URL:** https://yiruole.github.io/planet/

---

## Project Overview

Multi-page HTML/CSS portfolio for Ruole Yi. Vanilla HTML — no framework. Shared `style.css`, each section is a separate HTML page. Pure white theme. Google Fonts: Cormorant Garamond + DM Sans.

---

## File Structure

```
web/
├── index.html              ← homepage (name, physicist/artist, bio, section links)
├── oil-painting.html       ← 17 oil paintings with descriptions + lightbox
├── digital-art.html        ← 2 works (local .MOV files with controls)
├── experimental-film.html  ← placeholder
├── photography.html        ← placeholder
├── music.html              ← placeholder
├── style.css               ← shared: nav, footer, reveal, mobile menu, page header
├── PROGRESS.md             ← this file
├── 油画/                   ← 17 JPGs (0–15, 00)
├── 数字艺术/               ← output_16x9.MOV (Work I), 111.MOV (Work II)
└── 摄影/                   ← empty — photos not yet added
```

---

## Completed

### Session 1 — 2026-05-29 — Initial launch
- Single-page portfolio deployed to GitHub Pages

### Session 2 — 2026-06-03 (earlier) — Layout overhaul
- Full artist bio written and translated to English
- 17 oil paintings imported, 2 digital art videos imported
- Multi-section single-page layout with lightbox

### Session 3 — 2026-06-03 — Full multi-page rebuild
- Converted from single-page to multi-page (6 HTML pages + shared style.css)
- Full white theme, fixed nav, mobile hamburger menu, scroll reveal animations
- Homepage: name, "Physicist · Artist", bio, section links
- Oil Painting: 17 paintings, alternating A/B/C layouts, ghost numbers, lightbox
- Digital Art: 2-column video grid
- Experimental Film / Photography / Music: "Works forthcoming." placeholders

### Session 4 — 2026-06-03 — Push & polish
- Committed and pushed all files to GitHub Pages
- Updated painting descriptions and dates

### Session 5 — 2026-06-04 — Digital art + oil painting sizing
- Work I: switched to local file output_16x9.MOV (with controls)
- Work II (111.MOV): removed muted/autoplay, added controls so sound plays
- Oil painting images scaled to 65% of previous size (Layout A: max-width 559px, B/C: max-width 832px)

---

## Painting Descriptions Status

| # | File | Title | Description |
|---|------|-------|-------------|
| 01 | 0.jpg | The Bonds of Id | ✓ |
| 02 | 1.jpg | Mirror — Balance | ✓ |
| 03 | 2.jpg | The Non-Existent Atom | ✓ |
| 04 | 3.jpg | Mental Breakdown Caused by Uncertainty | ✓ |
| 05 | 4.jpg | Anxiety Cured My Existential Emptiness | ✓ |
| 06 | 5.jpg | Structure Exceeds Appearance | ✓ |
| 07 | 6.jpg | Threshold: The Residual Darkness at the Edge of Jouissance | ✓ |
| 08 | 7.jpg | Untitled | (no description) |
| 09 | 8.jpg | Untitled | ✓ |
| 10 | 9.jpg | Untitled | ✓ |
| 11 | 10.jpg | Untitled | ✓ |
| 12 | 11.jpg | Untitled | (no description, missing canvas size) |
| 13 | 12.jpg | Solar Sphere | ✓ |
| 14 | 13.jpg | Overhead | ✓ |
| 15 | 14.jpg | The Summit | ✓ |
| 16 | 15.jpg | Untitled | ✓ |
| 17 | 00.jpg | The Room of the Split Subject | ✓ |

---

## Not Yet Done

- [ ] Description + title for painting 08 (7.jpg)
- [ ] Description + canvas size for painting 12 (11.jpg)
- [ ] Real Instagram URL (currently placeholder `https://instagram.com/`)
- [ ] Populate photography section (摄影/ folder is empty)
- [ ] Populate experimental film section
- [ ] Populate music section
- [ ] Social preview meta tags (og:image, og:description, twitter:card)
- [ ] Favicon

---

## Design System

| Token | Value |
|---|---|
| `--bg` | `#ffffff` |
| `--text` | `#111111` |
| `--muted` | `#888888` |
| `--faint` | `#e2e2e2` |
| Display font | Cormorant Garamond 300 |
| Body font | DM Sans 300/400 |
| Description color | `#555` |
