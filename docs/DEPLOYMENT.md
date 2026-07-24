# exe.dev Deployment

## Current Production

- VM: `feel-the-agi.exe.xyz`
- Public URL: `https://feel-the-agi.exe.xyz`
- Proxy port: `8000`
- Web server: Nginx
- Document root: `/var/www/feel-the-agi`
- GitHub: `https://github.com/doeixd/feel-the-agi-archive`

The exe.dev VM was created from Windows PowerShell because Windows holds the SSH keys:

```powershell
ssh exe.dev new --name=feel-the-agi --json
```

## Nginx

Nginx listens on port 8000. Hashed Astro files and archived `/assets/` and fallback `/avatars/` files are cached immutably; HTML and `tweets.json` use a short cache. All three asset locations return real 404s instead of falling back to `index.html`.

Install and prepare the VM:

```powershell
ssh feel-the-agi.exe.xyz `
  "sudo apt-get update -qq && sudo apt-get install -y nginx"
```

Copy the build from Windows PowerShell using the WSL UNC path:

```powershell
$dist = "\\wsl.localhost\archlinux\home\Patrick\feel-the-agi\dist\*"
scp -r $dist feel-the-agi.exe.xyz:/var/www/feel-the-agi/
ssh feel-the-agi.exe.xyz "chmod -R a+rX /var/www/feel-the-agi"
```

The explicit permission command is essential. A previous deploy created `/_astro` with mode `700`, causing Nginx to return HTML for the stylesheet URL and making the site appear unstyled.

The current complete build is approximately 2.7 GB because `dist/assets/videos/` contains the binary video archive. For a large refresh, packaging `dist/` into one tar file, verifying its SHA-256 after transfer, extracting into a staging directory, and atomically swapping document roots is faster and safer than copying thousands of files directly. Keep the old root until public verification succeeds.

Expose the site:

```powershell
ssh exe.dev share port feel-the-agi 8000
ssh exe.dev share set-public feel-the-agi
ssh exe.dev share show feel-the-agi --json
```

## Production Verification

```bash
curl -I https://feel-the-agi.exe.xyz
curl -I https://feel-the-agi.exe.xyz/_astro/<current-css-file>.css
curl https://feel-the-agi.exe.xyz/tweets.json | jq length
curl -I https://feel-the-agi.exe.xyz/assets/avatars/<known-avatar>.jpg
curl -I -H 'Range: bytes=0-1023' https://feel-the-agi.exe.xyz/assets/videos/<known-video>.mp4
```

The stylesheet must return `200` with `Content-Type: text/css`, and the ranged MP4 request must return `206` with `Content-Type: video/mp4`.

## GitHub Publication

The repository is public. GitHub CLI authentication lives on Windows; pushes from WSL use the repository's configured `origin`. Never embed the GitHub token in a remote URL or committed file.
