# Operations and Archive Refreshes

## Routine Content Refresh

1. Synchronize bookmarks with Birdclaw.
2. Export or regenerate `/tmp/all_bookmarks.json`.
3. Manually classify all new records in the decision ledger.
4. Run `npm run prepare-data`.
5. Review the count and a sample of new records.
6. Run Astro checks and build.
7. Deploy `dist/` to exe.dev.
8. Verify HTML, CSS, JSON, galleries, and source links publicly.
9. Commit and push only after verification.

## Deployment Refresh

Always clear or replace the remote document root, copy all of `dist/`, then run:

```bash
chmod -R a+rX /var/www/feel-the-agi
sudo nginx -t
sudo systemctl reload nginx
```

Do not copy only `index.html`; Astro's hashed CSS filename changes between builds.

## Health Checks

- Public HTML returns HTTP 200.
- Current CSS asset returns HTTP 200 and `text/css`.
- A nonexistent `/_astro/` asset returns HTTP 404.
- `/tweets.json` returns 1,483 records or the newly expected count.
- Nginx is enabled and active on the VM.
- exe.dev share status is public and points to port 8000.

## Git Workflow

Before committing:

```bash
git status --short
git diff --stat
git diff
git log --oneline -10
```

Then stage only intended files, commit, and push `main`.

## Recovery

The site is static. Recovery consists of cloning the public repository, installing dependencies, building, and copying `dist/` to any static web server. The curated source JSON is committed, but the private Birdclaw database and credentials are not required to serve the existing archive.
