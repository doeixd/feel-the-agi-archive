# Architecture and Data Flow

## Stack

- Astro 7 static site generation
- TypeScript in strict mode
- Plain browser JavaScript for filtering, sorting, infinite scroll, and lightbox behavior
- HugeIcons free core icon set
- Nginx on an exe.dev VM

## Data Flow

```text
X bookmarks
  -> Birdclaw live sync
  -> ~/.birdclaw/birdclaw.sqlite
  -> /tmp/all_bookmarks.json
  -> manual bucket decision TSV files
  -> scripts/prepare_data.py
  -> src/data/tweets.json (Astro build input)
  -> public/tweets.json (lazy browser data)
  -> dist/ (static deployment)
```

`scripts/prepare_data.py` joins the full bookmark export to the manual curation ledger and emits only records assigned to `feel_the_agi`.

The script currently expects the shared workspace paths:

- `/tmp/all_bookmarks.json`
- `/home/Patrick/bookmarks_organized/.manual_bucket_decisions*.tsv`

The superseded `.manual_bucket_decisions_81_850.tsv` is intentionally excluded because the range was later split and reviewed again.

## Rendering Strategy

The first 30 cards are server-rendered for immediate content and no-JavaScript readability. The full 1,483-record JSON payload is fetched only when the visitor searches, sorts, filters, or approaches the infinite-scroll boundary.

Subsequent pages append 30 cards at a time. Sorting or changing filters replaces the current result set. A load-more button remains as a keyboard-accessible fallback to the `IntersectionObserver`.

## Important Files

- `src/pages/index.astro`: page shell and client interactions
- `src/components/TweetCard.astro`: server-rendered tweet card
- `src/components/TweetText.astro`: safe links, mentions, and hashtags
- `src/components/HugeIcon.astro`: HugeIcons SVG renderer
- `src/styles/global.css`: responsive themes and gallery layouts
- `scripts/prepare_data.py`: curated data export
- `public/tweets.json`: browser archive payload

## Tweet Data Contract

Each archive record contains:

- Tweet ID, timestamp, text, likes, and reply status
- Author display name, handle, avatar URL or generated hue
- URL entities
- Up to four media records
- Optional quoted tweet with its own author, text, URLs, and media

Engagement values are snapshots from synchronization time, not live values.
