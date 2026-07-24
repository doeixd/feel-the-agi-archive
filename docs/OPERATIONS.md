# Operations and Archive Refreshes

## Routine Content Refresh

1. Synchronize bookmarks and regenerate `/tmp/all_bookmarks.json`.
2. Capture a full authenticated export in `/tmp/bird-enriched-bookmarks.json`.
3. Fetch context for selected new reply posts into `/tmp/opencode/feel-the-agi-threads/`.
4. Manually classify all new records in the decision ledger.
5. Run `npm run archive-assets` and `npm run prepare-data`.
6. Review counts, missing local references, and representative records.
7. Run Astro checks and build.
8. Deploy the complete `dist/`, including the Git-ignored binary asset tree, to exe.dev.
9. Verify HTML, CSS, JSON, avatars, galleries, video ranges, and source links publicly.
10. Commit and push only after verification.

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
- A nonexistent `/assets/` file returns HTTP 404.
- A nonexistent fallback `/avatars/` file returns HTTP 404.
- A known avatar returns `image/jpeg` and a ranged video request returns HTTP 206 with `video/mp4`.
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

The site is static. Source and metadata recovery consists of cloning the public repository, installing dependencies, and building. Full visual recovery also requires the separately retained `public/assets/` binary archive, which is too large for this Git repository. The private Birdclaw database and credentials are not required to serve an already assembled deployment.
