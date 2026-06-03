# Ruole Yi — Portfolio Website Progress

**Last updated:** 2026-06-03  
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
├── digital-art.html        ← 2 videos
├── experimental-film.html  ← placeholder (was "Moving Image")
├── photography.html        ← placeholder
├── music.html              ← placeholder
├── style.css               ← shared: nav, footer, reveal, mobile menu, page header
├── PROGRESS.md             ← this file
├── chat-log-2026-06-03.md  ← full session transcript
├── 油画/                   ← 17 JPGs (0–15, 00)
├── 数字艺术/               ← 2 videos (000.mov, 111.MOV)
├── 摄影/                   ← empty — photos not yet added
└── 不要的/                 ← discarded (not tracked)
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

**Architecture**
- Converted from single-page to multi-page (6 HTML pages + shared style.css)
- Each section lives at its own URL (e.g. `/oil-painting.html`)

**Design overhaul**
- Full white theme (`--bg: #fff`, `--text: #111`)
- Removed grain overlay and custom cursor
- Navigation: fixed frosted-glass on scroll, active-link underline
- All pages share: nav, mobile hamburger menu, footer, scroll reveal animations

**Homepage (index.html)**
- Name in large Cormorant Garamond
- "Physicist · Artist" subtitle
- Full artist bio in English
- Section links at bottom

**Oil Painting page (oil-painting.html)**
- 17 paintings in alternating A/B/C layouts (centered / image-left / image-right)
- Ghost numbers (01–17) as subtle background typography
- Lightbox on image click (white overlay)
- 13 paintings have full translated English descriptions
- 4 paintings (10–13 / 9.jpg, 10.jpg, 11.jpg, 12.jpg) — no descriptions yet

**Navigation rename**
- "Moving Image" → "Experimental Film" across all pages

**Digital Art (digital-art.html)**
- 2-column video grid, both .mov files

**Placeholder pages**
- experimental-film.html, photography.html, music.html — "Works forthcoming."

### Session 4 — 2026-06-03 (this session)
- Committed and pushed all session 3 files to GitHub (previously untracked)
- Updated PROGRESS.md and chat-log

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
| 10 | 9.jpg | Untitled | ✗ needed |
| 11 | 10.jpg | Untitled | ✗ needed |
| 12 | 11.jpg | Untitled | ✗ needed |
| 13 | 12.jpg | Untitled | ✗ needed |
| 14 | 13.jpg | Overhead | ✓ |
| 15 | 14.jpg | The Summit | ✓ |
| 16 | 15.jpg | Untitled | ✓ |
| 17 | 00.jpg | The Room of the Split Subject | ✓ |

---

## Not Yet Done

- [ ] Descriptions + titles for paintings 10–13 (9.jpg–12.jpg)
- [ ] Title + description for painting 08 (7.jpg, currently "Untitled" with no text)
- [ ] Real Instagram URL (currently placeholder `href="#"`)
- [ ] Populate photography section (摄影/ folder is empty)
- [ ] Populate experimental film section
- [ ] Populate music section
- [ ] Social preview meta tags (og:image, og:description, twitter:card)
- [ ] Favicon
- [ ] Test video autoplay on iOS Safari

---

## Known Issues

- Chinese folder names (`油画/`, `数字艺术/`) work locally but may need URL-encoding on some servers
- Video autoplay: untested on iOS Safari
- `.mov` files — consider converting to `.mp4` for broader browser compatibility

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
