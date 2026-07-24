import argparse
import concurrent.futures
import csv
import glob
import hashlib
import json
import mimetypes
import re
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENRICHED = Path("/tmp/bird-enriched-bookmarks.json")
DECISIONS = ROOT.parent / "bookmarks_organized"
OUTPUT = ROOT / "public" / "assets"
MANIFEST = ROOT / "src" / "data" / "asset-map.json"
BIRDCLAW_MEDIA = ROOT.parent / ".birdclaw" / "media" / "originals"


def decisions():
    result = {}
    for path in glob.glob(str(DECISIONS / ".manual_bucket_decisions*.tsv")):
        if path.endswith("_81_850.tsv"):
            continue
        for row in csv.DictReader(open(path), delimiter="\t"):
            result[row["tweet_id"]] = row["bucket"]
    return result


def user_result(raw):
    result = (((raw or {}).get("core") or {}).get("user_results") or {}).get("result") or {}
    return result.get("result") or result


def avatar(record):
    user = user_result(record.get("_raw") or {})
    handle = record.get("author", {}).get("username")
    url = (user.get("avatar") or {}).get("image_url")
    if not url:
        legacy = user.get("legacy") or {}
        url = legacy.get("profile_image_url_https")
    return handle, url


def media_entries(record):
    raw = record.get("_raw") or {}
    legacy = raw.get("legacy") or {}
    extended = (legacy.get("extended_entities") or {}).get("media") or []
    if extended:
        return extended
    normalized = []
    for item in record.get("media") or []:
        normalized.append({
            "id_str": hashlib.sha256(item.get("url", "").encode()).hexdigest()[:24],
            "media_url_https": item.get("url"),
            "type": item.get("type"),
            "original_info": {"width": item.get("width"), "height": item.get("height")},
            "video_info": {
                "duration_millis": item.get("durationMs"),
                "variants": ([{"content_type": "video/mp4", "url": item["videoUrl"]}] if item.get("videoUrl") else []),
            },
        })
    return normalized


def extension(url, content_type=None):
    suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4"}:
        return ".jpg" if suffix == ".jpeg" else suffix
    guessed = mimetypes.guess_extension(content_type or "")
    return ".jpg" if guessed in {None, ".jpe"} else guessed


def choose_variant(entry):
    variants = [
        variant for variant in (entry.get("video_info") or {}).get("variants") or []
        if variant.get("content_type") == "video/mp4" and variant.get("url")
    ]
    if not variants:
        return None
    variants.sort(key=lambda item: item.get("bitrate") or 0)
    affordable = [variant for variant in variants if (variant.get("bitrate") or 0) <= 950_000]
    return (affordable or variants[:1])[-1]


def archived_target(value):
    path = value.get("path") if isinstance(value, dict) else value
    if not isinstance(path, str) or not path.startswith("/assets/"):
        return None
    return ROOT / "public" / path.lstrip("/")


def valid_archive_file(target):
    if not target.is_file() or target.stat().st_size <= 100:
        return False
    with target.open("rb") as source:
        header = source.read(16)
    suffix = target.suffix.lower()
    return {
        ".jpg": header.startswith(b"\xff\xd8\xff"),
        ".jpeg": header.startswith(b"\xff\xd8\xff"),
        ".png": header.startswith(b"\x89PNG\r\n\x1a\n"),
        ".webp": header.startswith(b"RIFF") and header[8:12] == b"WEBP",
        ".gif": header.startswith((b"GIF87a", b"GIF89a")),
        ".mp4": header[4:8] == b"ftyp",
    }.get(suffix, False)


def archived_file(value):
    target = archived_target(value)
    if not target:
        return None
    if not valid_archive_file(target):
        return None
    expected_size = value.get("bytes") if isinstance(value, dict) else None
    return target if not expected_size or target.stat().st_size == expected_size else None


def download(url, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "FeelTheAGIArchive/1.0"})
    temporary = destination.with_suffix(destination.suffix + ".part")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=90) as response, temporary.open("wb") as output:
                shutil.copyfileobj(response, output, 1024 * 1024)
            temporary.replace(destination)
            if valid_archive_file(destination):
                return destination.stat().st_size
            destination.unlink(missing_ok=True)
            return 0
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
            temporary.unlink(missing_ok=True)
            time.sleep(2 ** attempt)
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()

    selected = {tweet_id for tweet_id, bucket in decisions().items() if bucket == "feel_the_agi"}
    source = json.loads(ENRICHED.read_text()).get("tweets", [])
    records = [record for record in source if record.get("id") in selected]
    nested = [record.get("quotedTweet") for record in records if record.get("quotedTweet")]
    all_records = records + nested
    current = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"avatars": {}, "media": {}, "videos": {}}
    current.setdefault("avatars", {})
    current.setdefault("media", {})
    current.setdefault("videos", {})
    for section in ("avatars", "media", "videos"):
        valid = {}
        for key, value in current[section].items():
            if archived_file(value):
                valid[key] = value
        current[section] = valid

    jobs = []
    seen = set()
    for record in all_records:
        handle, avatar_url = avatar(record)
        if handle and avatar_url and handle not in current["avatars"] and ("avatar", handle) not in seen:
            seen.add(("avatar", handle))
            avatar_url = avatar_url.replace("_normal.", "_200x200.")
            target = OUTPUT / "avatars" / f"{re.sub(r'[^a-z0-9_]', '_', handle.lower())}{extension(avatar_url)}"
            jobs.append(("avatar", handle, avatar_url, target, None))

        for entry in media_entries(record):
            media_url = entry.get("media_url_https") or entry.get("media_url")
            if not media_url:
                continue
            media_id = entry.get("id_str") or hashlib.sha256(media_url.encode()).hexdigest()[:24]
            if ("media", media_id) not in seen and media_url not in current["media"]:
                seen.add(("media", media_id))
                cached = BIRDCLAW_MEDIA / Path(urllib.parse.urlparse(media_url).path).name
                target = OUTPUT / "media" / f"{media_id}{extension(media_url)}"
                jobs.append(("media", media_url, media_url, target, cached if cached.exists() else None))

            variant = choose_variant(entry)
            if variant and media_url not in current["videos"] and ("video", media_id) not in seen:
                seen.add(("video", media_id))
                target = OUTPUT / "videos" / f"{media_id}.mp4"
                info = entry.get("video_info") or {}
                jobs.append(("video", media_url, variant["url"], target, {
                    "bitRate": variant.get("bitrate"),
                    "durationMs": info.get("duration_millis"),
                }))

    video_estimate = sum(
        ((job[4].get("durationMs") or 0) / 1000) * ((job[4].get("bitRate") or 950_000) / 8)
        for job in jobs if job[0] == "video"
    )
    print(f"Records: {len(records)}, jobs: {len(jobs)}, estimated video bytes: {video_estimate / 1e9:.2f} GB")
    if args.dry_run:
        return

    def run(job):
        kind, key, url, target, extra = job
        if kind == "media" and isinstance(extra, Path):
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(extra, target)
            size = target.stat().st_size if valid_archive_file(target) else 0
            if not size:
                target.unlink(missing_ok=True)
        else:
            size = download(url, target)
        return job, size

    completed = 0
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(args.workers, 5))) as executor:
        for future in concurrent.futures.as_completed([executor.submit(run, job) for job in jobs]):
            job, size = future.result()
            kind, key, _, target, extra = job
            if size:
                path = "/" + str(target.relative_to(ROOT / "public"))
                if kind == "avatar":
                    current["avatars"][key] = path
                elif kind == "media":
                    current["media"][key] = path
                else:
                    current["videos"][key] = {"path": path, **(extra or {}), "bytes": size}
            else:
                failures.append(f"{kind}: {key}")
            completed += 1
            if completed % 25 == 0:
                MANIFEST.write_text(json.dumps(current, indent=2, sort_keys=True))
                print(f"Completed {completed}/{len(jobs)}")

    MANIFEST.write_text(json.dumps(current, indent=2, sort_keys=True))
    print(f"Archived avatars={len(current['avatars'])}, media={len(current['media'])}, videos={len(current['videos'])}")
    if failures:
        raise SystemExit(f"Failed to archive {len(failures)} assets:\n" + "\n".join(failures[:20]))


if __name__ == "__main__":
    main()
