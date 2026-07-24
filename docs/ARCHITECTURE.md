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
  -> Birdclaw working export (/tmp/all_bookmarks.json)
  -> authenticated Bird full export (/tmp/bird-enriched-bookmarks.json)
  -> selected reply threads (/tmp/opencode/feel-the-agi-threads/)
  -> manual bucket decision TSV files
  -> scripts/archive_assets.py
  -> public/assets/ + src/data/asset-map.json
  -> scripts/prepare_data.py
  -> src/data/tweets.json (Astro build input)
  -> public/tweets.json (lazy browser data)
  -> dist/ (static deployment)
```

`scripts/prepare_data.py` joins the working export, authenticated enrichment, selected thread context, asset manifest, and manual curation ledger. It emits only records assigned to `feel_the_agi`.

The script currently expects the shared workspace paths:

- `/tmp/all_bookmarks.json`
- `/tmp/bird-enriched-bookmarks.json`
- `/tmp/opencode/feel-the-agi-threads/`
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
- `scripts/archive_assets.py`: profile, image, poster, and video archiver
- `src/data/asset-map.json`: mapping from source URLs and handles to local assets
- `public/tweets.json`: browser archive payload

## Tweet Data Contract

Each archive record contains:

- Tweet ID, timestamp, text, conversation ID, and reply status
- Author display name, handle, archived avatar, generated hue, and verification state
- Reply, repost, quote, bookmark, like, and view snapshots
- URL entities
- Up to four media records
- Optional quoted tweet with its own author, text, URLs, metrics, and media
- Optional reply-parent preview and same-author thread position

Engagement values are snapshots from synchronization time, not live values.
