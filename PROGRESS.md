# Ruole Yi — Portfolio Website Progress

**Last updated:** 2026-06-03  
**Branch:** main

---

## Project Overview

Single-page HTML/CSS/JS artist portfolio for Ruole Yi. No framework — pure vanilla HTML with Google Fonts (Cormorant Garamond + DM Sans). Hosted locally; intended for eventual deployment.

---

## File Structure

```
web/
├── index.html          ← main page (all HTML + CSS + JS in one file)
├── PROGRESS.md         ← this file
├── .gitignore
├── 油画/               ← oil painting images (17 JPGs: 0–15, 00)
├── 数字艺术/           ← digital art videos (000.mov, 111.MOV)
├── 摄影/               ← photography (currently empty)
└── 不要的/             ← discarded assets (not tracked in git)
```

---

## Completed

### Session 1 — Initial build (before 2026-06-03)
- Dark-themed single-page portfolio with grain overlay, custom gold cursor
- Fixed nav with scroll-triggered frosted glass effect
- Hero section with animated name reveal
- Mixed gallery section (oil paintings + moving image)
- About section with placeholder bio
- Contact section (email + Instagram)
- Lightbox for image zoom
- Mobile responsive with hamburger menu

### Session 2 — 2026-06-03 — Full layout restructure
- **Restructured into 6 independent sections** with proper `id` anchors:
  - `#about` — full artist bio (right after hero)
  - `#oil-painting` — dedicated section for oil works
  - `#digital-art` — dedicated section for video works
  - `#moving-image` — placeholder
  - `#photography` — placeholder
  - `#music` — placeholder
- **Updated navigation** — 6 links (Oil Painting · Digital Art · Moving Image · Photography · Music · About); mobile hamburger updated to match
- **Artist bio rewritten** — original Chinese bio translated to natural English; split into two-column layout: large pull quote on left (sticky on desktop), body paragraphs on right; last paragraph styled large italic
- **Oil Painting section** — masonry grid, all 17 images from `油画/` folder, lightbox on click
- **Digital Art section** — 2-column video grid, both `.mov` files from `数字艺术/`, autoplay muted loop
- **Placeholder sections** — Moving Image, Photography, Music each show a tasteful "Works forthcoming" state (horizontal rule + italic text)
- **Removed broken references** — old root-level `IMG_*.jpg` and screen recording (deleted files) no longer referenced
- Section numbering labels (01–05) for work sections

---

## Not Yet Done

- [ ] Add titles to individual oil paintings (currently all labeled "Oil on canvas")
- [ ] Fill in actual Instagram URL in Contact section (`href` is a placeholder)
- [ ] Populate Moving Image section with video content
- [ ] Populate Photography section (摄影/ folder is empty)
- [ ] Populate Music section (no audio files yet)
- [ ] Deploy to a live URL (no hosting configured)
- [ ] Add `<meta og:*>` social preview tags
- [ ] Favicon

---

## Known Issues / Notes

- **Chinese folder names** (`油画/`, `数字艺术/`) in `src` attributes — work fine in modern browsers on macOS (UTF-8 filesystem), but may need URL-encoding (`%E6%B2%B9%E7%94%BB/` etc.) if deployed to a server with non-UTF-8 path handling
- **Video autoplay** — `数字艺术/000.mov` and `111.MOV` use `autoplay muted loop`; Safari on iOS should respect this but test on device
- **Hero background** — currently pure dark (the original hero images were deleted/reorganized); could add one painting as a subtle parallax background later
- **摄影 folder** is empty — Photography section shows placeholder until images are added

---

## Design System

| Token | Value |
|---|---|
| `--bg` | `#090f17` |
| `--bg-2` | `#0a141e` |
| `--gold` | `#c4a35a` |
| `--text` | `#ede9e3` |
| `--muted` | `#6e8494` |
| Display font | Cormorant Garamond (Google Fonts) |
| Body font | DM Sans (Google Fonts) |
