# Development and Verification

## Requirements

- Node.js 20 or newer
- npm
- Python 3 for the data export
- Access to the shared bookmark export and decision ledgers when regenerating data

## Commands

```bash
npm install
npm run dev
npm run prepare-data
npx astro check
npm run build
npm run preview
```

The development server normally runs at `http://localhost:4321`.

## Final Verification Checklist

1. `npm run prepare-data` exports the expected number of records.
2. `npx astro check` reports zero errors and warnings.
3. `npm run build` succeeds.
4. `dist/index.html` references an existing `/_astro/*.css` asset.
5. `dist/tweets.json` parses and contains the expected count.
6. Latest, earliest, and random modes return distinct valid orderings.
7. Search finds main and quoted authors.
8. Infinite scroll appends without replacing expanded cards.
9. One-, two-, three-, and four-image galleries render correctly.
10. Main and quoted images open in the lightbox.
11. Thumbnail-only videos link to X; real MP4 records mount only in view.
12. Dark and light themes work on desktop and mobile.
13. Search and sorting controls scroll away naturally.

## Performance Model

Only 30 tweet cards are included in initial HTML. The complete JSON archive is fetched lazily. Infinite scroll appends 30 records at a time, and images use native lazy loading. Off-screen native videos are fully unmounted.

Google Fonts are loaded with preconnect hints. The site remains readable with fallback fonts if Google Fonts is unavailable.
