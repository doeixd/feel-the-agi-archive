# Security, Privacy, and Limitations

## Public Data

This repository and deployed site are public. The archive contains public tweet text, handles, media URLs, timestamps, quoted posts, and captured like counts.

## Secrets

Never commit:

- X `auth_token` or `ct0` cookies
- Browser cookie databases
- GitHub tokens
- Birdclaw's SQLite database
- Private DMs or non-bookmark exports
- SSH private keys

Authentication remains in Windows credential stores and browser profiles.

## Link and HTML Safety

Tweet text is escaped before dynamic HTML insertion. Links are restricted to HTTP and HTTPS. Mentions and hashtags are mapped to X URLs. Media URLs are protocol-checked on the client.

## External Dependencies

- Images currently hotlink `pbs.twimg.com` and may disappear, rate-limit, or be blocked.
- Thumbnail-only video records depend on the original X post for playback.
- Google Fonts are optional external resources.
- Original tweet links can be deleted, restricted, or changed.

Broken images display a media-unavailable fallback. The repository preserves metadata, not guaranteed permanent copies of every media object.

## Fidelity Limitations

- Most synced profiles did not include real avatar URLs, so generated initials are used.
- Like counts are historical snapshots.
- Reply context may be unavailable.
- Quote depth is limited by source data.
- Video thumbnails are not equivalent to archived videos.
- This project resembles X for historical context but is not affiliated with X.

## Browser Support

The lightbox uses native `<dialog>`, and infinite loading uses `IntersectionObserver`. Current evergreen browsers are supported. The load-more button provides a fallback if automatic intersection loading is unavailable or undesirable.
