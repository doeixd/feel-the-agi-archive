import csv
import glob
import html
import json
from datetime import datetime
from pathlib import Path


WORKSPACE = Path("/home/Patrick")
ROOT = WORKSPACE / "feel-the-agi"
BOOKMARK_DIR = WORKSPACE / "bookmarks_organized"
ENRICHED_PATH = Path("/tmp/bird-enriched-bookmarks.json")
THREAD_DIR = Path("/tmp/opencode/feel-the-agi-threads")


def load_decisions():
    files = [
        Path(path)
        for path in glob.glob(str(BOOKMARK_DIR / ".manual_bucket_decisions*.tsv"))
        if not path.endswith("_81_850.tsv")
    ]
    return {
        row["tweet_id"]: row["bucket"]
        for path in files
        for row in csv.DictReader(path.open(), delimiter="\t")
    }


def user_result(raw):
    result = (((raw or {}).get("core") or {}).get("user_results") or {}).get("result") or {}
    return result.get("result") or result


def metrics(record):
    raw = record.get("_raw") or {}
    legacy = raw.get("legacy") or {}
    views = raw.get("views") or {}
    return {
        "replyCount": record.get("replyCount") or legacy.get("reply_count") or 0,
        "repostCount": record.get("retweetCount") or legacy.get("retweet_count") or 0,
        "quoteCount": legacy.get("quote_count") or 0,
        "bookmarkCount": legacy.get("bookmark_count") or 0,
        "viewCount": int(views.get("count") or 0),
    }


def author(record, fallback, assets, avatar_manifest):
    normalized = record.get("author") or {}
    raw_user = user_result(record.get("_raw") or {})
    handle = normalized.get("username") or fallback.get("handle") or "unknown"
    verification = raw_user.get("verification") or {}
    return {
        "handle": handle,
        "displayName": normalized.get("name") or fallback.get("displayName") or handle,
        "avatarUrl": assets.get("avatars", {}).get(handle) or avatar_manifest.get(handle) or fallback.get("avatarUrl"),
        "avatarHue": fallback.get("avatarHue") or 220,
        "verified": bool(raw_user.get("is_blue_verified") or verification.get("verified")),
    }


def media(record, assets):
    result = []
    for item in (record.get("media") or [])[:4]:
        original_url = item.get("url") or ""
        local_media = assets.get("media", {}).get(original_url)
        local_video = assets.get("videos", {}).get(original_url)
        kind = "gif" if item.get("type") == "animated_gif" else "video" if item.get("type") == "video" else "image"
        entry = {
            "type": kind,
            "url": local_media or original_url,
            "thumbnailUrl": local_media or item.get("previewUrl") or original_url,
            "width": item.get("width"),
            "height": item.get("height"),
            "durationMs": item.get("durationMs"),
        }
        video_url = local_video.get("path") if local_video else item.get("videoUrl")
        if video_url:
            entry["variants"] = [{
                "url": video_url,
                "contentType": "video/mp4",
                "bitRate": (local_video or {}).get("bitRate"),
            }]
        result.append(entry)
    return result


def compact_context(record, assets, avatar_manifest):
    normalized_author = record.get("author") or {}
    fallback_author = {
        "handle": normalized_author.get("username") or normalized_author.get("handle"),
        "displayName": normalized_author.get("name") or normalized_author.get("displayName"),
    }
    return {
        "id": record.get("id"),
        "text": html.unescape(record.get("text") or ""),
        "createdAt": record.get("createdAt"),
        "author": author(record, fallback_author, assets, avatar_manifest),
        "media": media(record, assets)[:1],
        "metrics": metrics(record),
    }


def parse_date(value):
    if not value:
        return ""
    try:
        return datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y").isoformat()
    except ValueError:
        return value


decisions = load_decisions()
base_records = json.loads(Path("/tmp/all_bookmarks.json").read_text())
enriched_records = json.loads(ENRICHED_PATH.read_text()).get("tweets", []) if ENRICHED_PATH.exists() else []
enriched_by_id = {record.get("id"): record for record in enriched_records}
asset_path = ROOT / "src" / "data" / "asset-map.json"
assets = json.loads(asset_path.read_text()) if asset_path.exists() else {"avatars": {}, "media": {}, "videos": {}}
avatar_path = ROOT / "src" / "data" / "avatar-map.json"
avatar_manifest = json.loads(avatar_path.read_text()) if avatar_path.exists() else {}

thread_context = {}
for path in THREAD_DIR.glob("*.json") if THREAD_DIR.exists() else []:
    records = json.loads(path.read_text())
    current_id = path.stem
    current = next((record for record in records if record.get("id") == current_id), None)
    if not current:
        continue
    parent_id = current.get("inReplyToStatusId")
    parent = next((record for record in records if record.get("id") == parent_id), None)
    same_author = sorted(
        [record for record in records if record.get("authorId") == current.get("authorId")],
        key=lambda record: parse_date(record.get("createdAt")),
    )
    position = next((index + 1 for index, record in enumerate(same_author) if record.get("id") == current_id), None)
    thread_context[current_id] = {
        "parent": compact_context(parent, assets, avatar_manifest) if parent else None,
        "thread": ({"position": position, "total": len(same_author)} if len(same_author) > 1 and position else None),
    }

archive = []
for base in base_records:
    tweet_id = base.get("id")
    if decisions.get(tweet_id) != "feel_the_agi":
        continue

    enriched = enriched_by_id.get(tweet_id) or {}
    base_author = base.get("author") or {}
    raw = enriched.get("_raw") or {}
    legacy = raw.get("legacy") or {}
    quote_base = base.get("quotedTweet") or {}
    quote_enriched = enriched.get("quotedTweet") or {}
    context = thread_context.get(tweet_id) or {}
    reply_to_id = enriched.get("inReplyToStatusId") or legacy.get("in_reply_to_status_id_str") or base.get("replyToId")

    quote = None
    if quote_enriched or quote_base:
        quote_record = quote_enriched or quote_base
        quote_fallback_author = quote_base.get("author") or {}
        quote = {
            "id": quote_record.get("id"),
            "text": html.unescape(quote_record.get("text") or quote_base.get("text") or ""),
            "createdAt": parse_date(quote_record.get("createdAt") or quote_base.get("createdAt")),
            "author": author(quote_record, quote_fallback_author, assets, avatar_manifest),
            "media": media(quote_record, assets) or quote_base.get("media") or [],
            "urls": (quote_base.get("entities") or {}).get("urls") or [],
            "metrics": metrics(quote_record),
        }

    archive.append({
        "id": tweet_id,
        "createdAt": parse_date(enriched.get("createdAt") or base.get("createdAt")),
        "text": html.unescape(enriched.get("text") or base.get("text") or ""),
        "likeCount": enriched.get("likeCount") or base.get("likeCount") or 0,
        "metrics": metrics(enriched) if enriched else {
            "replyCount": 0, "repostCount": 0, "quoteCount": 0, "bookmarkCount": 0, "viewCount": 0,
        },
        "replyToId": reply_to_id,
        "replyToHandle": legacy.get("in_reply_to_screen_name"),
        "conversationId": enriched.get("conversationId") or tweet_id,
        "thread": context.get("thread"),
        "replyContext": context.get("parent") or (
            compact_context(base.get("replyToTweet"), assets, avatar_manifest) if base.get("replyToTweet") else None
        ),
        "author": author(enriched, base_author, assets, avatar_manifest) if enriched else {
            "handle": base_author.get("handle") or "unknown",
            "displayName": base_author.get("displayName") or "Unknown",
            "avatarUrl": assets.get("avatars", {}).get(base_author.get("handle")) or avatar_manifest.get(base_author.get("handle")) or base_author.get("avatarUrl"),
            "avatarHue": base_author.get("avatarHue") or 220,
            "verified": False,
        },
        "media": media(enriched, assets) if enriched else base.get("media") or [],
        "urls": (base.get("entities") or {}).get("urls") or [],
        "quote": quote,
    })

archive.sort(key=lambda tweet: tweet["createdAt"] or "", reverse=True)


unarchived = []
for tweet in archive:
    owners = [(tweet["id"], tweet)]
    if tweet.get("quote"):
        owners.append((f"{tweet['id']} quote", tweet["quote"]))
    for label, owner in owners:
        avatar_url = owner["author"].get("avatarUrl")
        if not avatar_url or not avatar_url.startswith(("/assets/avatars/", "/avatars/")):
            unarchived.append(f"{label}: avatar")
        for index, item in enumerate(owner.get("media") or []):
            if not item.get("url", "").startswith("/assets/media/"):
                unarchived.append(f"{label}: media {index + 1}")
            if any(
                not variant.get("url", "").startswith("/assets/videos/")
                for variant in item.get("variants") or []
            ):
                unarchived.append(f"{label}: video {index + 1}")
if unarchived:
    raise SystemExit(f"Found {len(unarchived)} unarchived main or quoted assets:\n" + "\n".join(unarchived[:20]))


def local_paths(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from local_paths(child)
    elif isinstance(value, list):
        for child in value:
            yield from local_paths(child)
    elif isinstance(value, str) and value.startswith(("/assets/", "/avatars/")):
        yield value


missing_assets = sorted({
    path for path in local_paths(archive)
    if not (ROOT / "public" / path.lstrip("/")).is_file()
})
if missing_assets:
    sample = "\n".join(missing_assets[:20])
    raise SystemExit(f"Missing {len(missing_assets)} referenced local assets:\n{sample}")

target = ROOT / "src" / "data"
target.mkdir(parents=True, exist_ok=True)
payload = json.dumps(archive, ensure_ascii=True, separators=(",", ":"))
(target / "tweets.json").write_text(payload)
public = ROOT / "public"
public.mkdir(exist_ok=True)
(public / "tweets.json").write_text(payload)
print(
    f"Exported {len(archive)} tweets; "
    f"main-avatars={sum(bool(tweet['author'].get('avatarUrl')) for tweet in archive)}, "
    f"video-refs={sum(bool(item.get('variants')) for tweet in archive for item in tweet['media']) + sum(bool(item.get('variants')) for tweet in archive if tweet.get('quote') for item in tweet['quote']['media'])}, "
    f"reply-context={sum(bool(tweet.get('replyContext')) for tweet in archive)}"
)
