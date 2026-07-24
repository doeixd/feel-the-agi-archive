# Security, Privacy, and Limitations

## Public Data

This repository and deployed site are public. The archive contains public tweet text, handles, profile pictures, media, timestamps, quoted posts, limited reply context, and captured engagement counts.

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

## Archive Boundaries

- Main and quoted profile pictures, images, posters, and playable videos are locally archived in production.
- Reply-parent previews can still contain an external media URL when that context asset was not part of the selected archive.
- Thumbnail-only future video records depend on the original X post for playback.
- Google Fonts are optional external resources.
- Original tweet links can be deleted, restricted, or changed.

The 2.7 GB binary archive is excluded from Git and must be retained separately. Broken images display a media-unavailable fallback. The repository preserves metadata and manifests, not the binary payload itself.

## Fidelity Limitations

- Profile, verification, and engagement values are historical snapshots.
- Reply context is available for 44 selected records, not every reply.
- Same-author thread positions are available for 32 selected records and do not represent every participant in a conversation.
- Quote depth is limited by source data.
- Repost provenance was normalized away by the authenticated bookmark output; repost counts remain available.
- This project resembles X for historical context but is not affiliated with X.

## Browser Support

The lightbox uses native `<dialog>`, and infinite loading uses `IntersectionObserver`. Current evergreen browsers are supported. The load-more button provides a fallback if automatic intersection loading is unavailable or undesirable.
