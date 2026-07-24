# Development and Verification

## Requirements

- Node.js 20 or newer
- npm
- Python 3 for the data export
- Access to the shared bookmark exports, thread captures, decision ledgers, and binary asset archive when regenerating data

## Commands

```bash
npm install
npm run dev
npm run archive-assets
npm run prepare-data
npx astro check
npm run build
npm run preview
```

The development server normally runs at `http://localhost:4321`.

## Final Verification Checklist

1. `npm run prepare-data` exports the expected number of records and enrichment counts.
2. `npx astro check` reports zero errors and warnings.
3. `npm run build` succeeds.
4. `dist/index.html` references an existing `/_astro/*.css` asset.
5. `dist/tweets.json` parses and contains the expected count.
6. Latest, earliest, and random modes return distinct valid orderings.
7. Search finds main and quoted authors.
8. Infinite scroll appends without replacing expanded cards.
9. One-, two-, three-, and four-image galleries render correctly.
10. Main and quoted images open in the lightbox.
11. Archived MP4 records mount only in view and open with controls in the lightbox.
12. Dark and light themes work on desktop and mobile.
13. Search and sorting controls scroll away naturally.
14. Every local JSON asset reference resolves to a file under `public/assets/`.
15. A representative MP4 request returns HTTP 206 when a byte range is requested.

## Performance Model

Only 30 tweet cards are included in initial HTML. The complete JSON archive is fetched lazily. Infinite scroll appends 30 records at a time, and images use native lazy loading. Off-screen native videos are fully unmounted.

Google Fonts are loaded with preconnect hints. The site remains readable with fallback fonts if Google Fonts is unavailable.
