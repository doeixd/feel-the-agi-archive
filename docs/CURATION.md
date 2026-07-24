# Curation Process

## Method

Every bookmark received one primary destination through content-first review. Keyword scoring was explicitly rejected because an apparently mundane economic, medical, or cultural post can be more historically meaningful than an AI announcement.

The decision ledgers live outside this repository in:

```text
/home/Patrick/bookmarks_organized/.manual_bucket_decisions*.tsv
```

Each row has:

```text
tweet_id    bucket    reason
```

Valid buckets are `feel_the_agi`, `for_later_reference`, and `inspiration`.

## Review Evolution

The first Feel The AGI pass was too narrow and over-weighted explicit model news. Several review passes broadened the definition using user-confirmed examples:

- AI-mediated prescription access
- Middle-class economic change
- Mass AI-literacy deployment
- Surveillance and drones
- Bleak prediction-market speculation
- China's construction and state-capacity advantage
- Cost-of-living and institutional-decay markers

Focused straggler reviews moved overlooked economic, geopolitical, medical, scientific, labor, infrastructure, and cultural records into the archive.

## Assignment Test

Ask: **Would this help a future person understand what it felt like to live through this era?**

- If yes, it belongs in Feel The AGI even when it is also useful reference material.
- If its main value is actionable reuse without historical texture, use For Later Reference.
- If its main value is aesthetic, creative, or personally evocative without telling the era's story, use Inspiration.

## Refreshing Curation

1. Synchronize and export new bookmarks.
2. Review each new record manually.
3. Add exactly one primary decision to the appropriate TSV ledger.
4. Check for duplicate or missing IDs.
5. Run `npm run prepare-data`.
6. Confirm the exported count before building.
