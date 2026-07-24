# Birdclaw Usage

Birdclaw is the local-first Twitter/X workspace used to collect and cache the source bookmarks.

## Key Paths

- Database: `~/.birdclaw/birdclaw.sqlite`
- Downloaded media: `~/.birdclaw/media/originals/`
- Full working export: `/tmp/all_bookmarks.json`
- Authenticated full export: `/tmp/bird-enriched-bookmarks.json`
- Selected reply threads: `/tmp/opencode/feel-the-agi-threads/`

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

Birdclaw's cache supplied many image originals. Authenticated Bird output supplied profile metadata, engagement counts, extended media entities, and MP4 variants used by the archive asset script. See [MEDIA.md](MEDIA.md) for the resulting local archive.

## Authenticated Enrichment

The enrichment snapshot was generated with Bird's full JSON bookmark output:

```bash
bird bookmarks --all --json-full > /tmp/bird-enriched-bookmarks.json
```

Authentication cookies were supplied only as ephemeral process environment variables. Never place their values in shell history, scripts, documentation, manifests, or Git. Selected reply threads were captured separately because the bookmark payload alone does not include parent and conversation context.

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
