import csv
import glob
import html
import json
from pathlib import Path


workspace = Path("/home/Patrick")
bookmark_dir = workspace / "bookmarks_organized"
decision_files = [
    Path(path)
    for path in glob.glob(str(bookmark_dir / ".manual_bucket_decisions*.tsv"))
    if not path.endswith("_81_850.tsv")
]
decisions = {
    row["tweet_id"]: row["bucket"]
    for path in decision_files
    for row in csv.DictReader(path.open(), delimiter="\t")
}

tweets = json.load(open("/tmp/all_bookmarks.json"))
archive = []
for tweet in tweets:
    if decisions.get(tweet.get("id")) != "feel_the_agi":
        continue

    author = tweet.get("author") or {}
    quote = tweet.get("quotedTweet") or None
    archive.append(
        {
            "id": tweet["id"],
            "createdAt": tweet.get("createdAt"),
            "text": html.unescape(tweet.get("text") or ""),
            "likeCount": tweet.get("likeCount") or 0,
            "replyToId": tweet.get("replyToId"),
            "author": {
                "handle": author.get("handle") or "unknown",
                "displayName": author.get("displayName") or "Unknown",
                "avatarUrl": author.get("avatarUrl"),
                "avatarHue": author.get("avatarHue") or 220,
            },
            "media": tweet.get("media") or [],
            "urls": (tweet.get("entities") or {}).get("urls") or [],
            "quote": (
                {
                    "id": quote.get("id"),
                    "text": html.unescape(quote.get("text") or ""),
                    "createdAt": quote.get("createdAt"),
                    "author": {
                        "handle": (quote.get("author") or {}).get("handle") or "unknown",
                        "displayName": (quote.get("author") or {}).get("displayName") or "Unknown",
                    },
                    "media": quote.get("media") or [],
                }
                if quote
                else None
            ),
        }
    )

archive.sort(key=lambda tweet: tweet["createdAt"] or "", reverse=True)
target = workspace / "feel-the-agi" / "src" / "data"
target.mkdir(parents=True, exist_ok=True)
payload = json.dumps(archive, ensure_ascii=True, separators=(",", ":"))
(target / "tweets.json").write_text(payload)
public = workspace / "feel-the-agi" / "public"
public.mkdir(exist_ok=True)
(public / "tweets.json").write_text(payload)
print(f"Exported {len(archive)} Feel The AGI tweets.")
