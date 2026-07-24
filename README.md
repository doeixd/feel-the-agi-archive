# Feel The AGI

An interactive museum and time capsule of the scaling era, built with Astro 7 from a manually curated archive of 1,483 tweets.

- Live site: [feel-the-agi.exe.xyz](https://feel-the-agi.exe.xyz)
- Public source: [github.com/doeixd/feel-the-agi-archive](https://github.com/doeixd/feel-the-agi-archive)

## Purpose

Feel The AGI is not an AI news feed. It preserves what it felt like to live through accelerating technological and institutional change: AGI, robotics, medicine, science, surveillance, drones, prediction markets, China's rise, labor displacement, late-stage capitalism, and the ordinary jokes and workflows through which extraordinary change became normal.

## Features

- Reverse-chronological, earliest-first, and randomized reading modes
- Search and year filters across 1,483 curated artifacts
- Infinite scrolling with an accessible load-more fallback
- Tweet attribution, quote posts, links, image galleries, and source URLs
- X-style multi-image layouts and a keyboard-accessible media lightbox
- Viewport-managed native video playback when MP4 variants are available
- Responsive dark and light themes
- Static deployment with a small initial page and lazily fetched archive data

## Quick Start

```bash
npm install
npm run dev
```

Build and validate:

```bash
npm run prepare-data
npx astro check
npm run build
```

The static production output is written to `dist/`.

## Documentation

- [Goals and curatorial principles](docs/GOALS.md)
- [Architecture and data flow](docs/ARCHITECTURE.md)
- [Birdclaw usage](docs/BIRDCLAW.md)
- [Curation process](docs/CURATION.md)
- [Media and video behavior](docs/MEDIA.md)
- [Development and verification](docs/DEVELOPMENT.md)
- [exe.dev deployment](docs/DEPLOYMENT.md)
- [Operations and archive refreshes](docs/OPERATIONS.md)
- [Security, privacy, and limitations](docs/SECURITY_AND_LIMITATIONS.md)
