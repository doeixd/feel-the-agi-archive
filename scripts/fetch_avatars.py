import concurrent.futures
import json
import mimetypes
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/tmp/all_bookmarks.json")
OUTPUT = ROOT / "public" / "avatars"
MANIFEST = ROOT / "src" / "data" / "avatar-map.json"
WORKERS = 3
REQUEST_INTERVAL = 0.25
MAX_BYTES = 5 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
request_lock = threading.Lock()
last_request = 0.0


def safe_name(handle: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", handle.lower())


def fetch(handle: str):
    global last_request
    url = f"https://unavatar.io/x/{urllib.parse.quote(handle)}?fallback=false"
    request = urllib.request.Request(url, headers={"User-Agent": "FeelTheAGIArchive/1.0"})
    for attempt in range(3):
        try:
            with request_lock:
                delay = REQUEST_INTERVAL - (time.monotonic() - last_request)
                if delay > 0:
                    time.sleep(delay)
                last_request = time.monotonic()
            with urllib.request.urlopen(request, timeout=30) as response:
                content_type = response.headers.get_content_type()
                if content_type not in ALLOWED_TYPES:
                    return handle, None
                body = response.read(MAX_BYTES + 1)
                if len(body) < 100 or len(body) > MAX_BYTES:
                    return handle, None
                extension = mimetypes.guess_extension(content_type) or ".jpg"
                if extension == ".jpe":
                    extension = ".jpg"
                filename = f"{safe_name(handle)}{extension}"
                (OUTPUT / filename).write_bytes(body)
                return handle, f"/avatars/{filename}"
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return handle, False
            if error.code == 429 or error.code >= 500:
                time.sleep(2 ** attempt)
                continue
            return handle, False
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2 ** attempt)
    return handle, None


def main():
    records = json.loads(SOURCE.read_text())
    decisions = {}
    for path in (ROOT.parent / "bookmarks_organized").glob(".manual_bucket_decisions*.tsv"):
        if path.name.endswith("_81_850.tsv"):
            continue
        for line in path.read_text().splitlines()[1:]:
            tweet_id, bucket, *_ = line.split("\t")
            decisions[tweet_id] = bucket
    records = [tweet for tweet in records if decisions.get(tweet.get("id")) == "feel_the_agi"]
    handles = {
        author.get("handle")
        for tweet in records
        for author in [tweet.get("author") or {}, (tweet.get("quotedTweet") or {}).get("author") or {}]
        if author.get("handle")
    }
    existing = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    def available(path):
        if not isinstance(path, str) or not path.startswith("/avatars/"):
            return False
        return (ROOT / "public" / path.lstrip("/")).is_file()

    pending = sorted(
        handle for handle in handles
        if existing.get(handle) is not False and not available(existing.get(handle))
    )
    OUTPUT.mkdir(parents=True, exist_ok=True)

    completed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {executor.submit(fetch, handle): handle for handle in pending}
        for future in concurrent.futures.as_completed(futures):
            handle, path = future.result()
            existing[handle] = path
            completed += 1
            if completed % 50 == 0:
                MANIFEST.write_text(json.dumps(existing, indent=2, sort_keys=True))
                print(f"Fetched {completed}/{len(pending)} avatar lookups")
            time.sleep(0.03)

    MANIFEST.write_text(json.dumps(existing, indent=2, sort_keys=True))
    found = sum(available(path) for path in existing.values())
    print(f"Avatar manifest: {found}/{len(existing)} available")


if __name__ == "__main__":
    main()
