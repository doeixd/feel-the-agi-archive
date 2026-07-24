# Birdclaw Usage

Birdclaw is the local-first Twitter/X workspace used to collect and cache the source bookmarks.

## Key Paths

- Database: `~/.birdclaw/birdclaw.sqlite`
- Downloaded media: `~/.birdclaw/media/originals/`
- Full working export: `/tmp/all_bookmarks.json`

Do not commit authentication cookies, tokens, the Birdclaw database, or private account exports.

## Bookmark Synchronization

The full collection was synchronized with:

```bash
birdclaw sync bookmarks --mode auto --all --json
```

Useful options:

```bash
birdclaw sync bookmarks --help
birdclaw sync bookmarks --mode auto --all --refresh
birdclaw sync bookmarks --mode bird --all
```

`auto` selects the available transport. The current WSL installation reports local mode because `xurl` is not installed. Live synchronization therefore requires valid transport credentials or a working Bird installation.

## Media Cache

The media cache was populated with:

```bash
birdclaw media fetch \
  --include-video \
  --parallel 3 \
  --pacing-ms 500 \
  --video-pacing-ms 1500
```

Inspect without downloading:

```bash
birdclaw media fetch --kind bookmark --include-video --dry-run --json
```

Birdclaw's cache currently contains image originals and video thumbnails. See [MEDIA.md](MEDIA.md) for the video metadata limitation discovered during development.

## Database Inspection

Useful read-only queries:

```bash
sqlite3 ~/.birdclaw/birdclaw.sqlite '.tables'
sqlite3 ~/.birdclaw/birdclaw.sqlite \
  'SELECT COUNT(*) FROM tweets;'
sqlite3 ~/.birdclaw/birdclaw.sqlite \
  "SELECT id, media_json FROM tweets WHERE media_json LIKE '%video_thumb%' LIMIT 5;"
```

The relevant `tweets` columns include `text`, `created_at`, `like_count`, `entities_json`, `media_json`, and `quoted_tweet_id`.

## Authentication Notes

Credentials previously came from a logged-in Windows Edge profile. They are not stored in this repository. WSL cannot transparently decrypt Windows DPAPI browser cookies, and an active Edge process may lock its cookie database. Never paste credentials into project files or Git history.
