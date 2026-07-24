# Media and Video Behavior

## Images

Image galleries follow X-like arrangements:

- One image: natural aspect ratio with a maximum display height
- Two images: two equal columns
- Three images: one large left cell and two stacked right cells
- Four images: 2x2 grid

Multi-image cells use `object-fit: contain` to avoid clipping charts, screenshots, and text-heavy images. The surrounding cell may letterbox unusual aspect ratios. Clicking an image opens the full-screen lightbox, where media is always contained rather than cropped.

Quoted-post media uses the same rules at a smaller gallery height.

## Lightbox

The native dialog lightbox supports:

- Previous and next buttons
- Left and right arrow keys
- Escape to close
- Backdrop click to close
- Image count announcements
- Contextual image labels
- Native video playback and controls

## Local Archive

Authenticated enrichment supplied full profile and extended media metadata. `scripts/archive_assets.py` selected a moderate MP4 rendition at or below 950 Kbit/s when available and archived the selected collection under:

- `public/assets/avatars/`: 1,169 profile pictures
- `public/assets/media/`: 1,510 image originals and video posters
- `public/assets/videos/`: 472 unique MP4 files, referenced 485 times by main and quoted posts

The binary tree is approximately 2.7 GB and is excluded from Git. `src/data/asset-map.json` is the committed mapping from original handles/media URLs to local paths. A complete deployment must restore or copy both the Git build and this binary tree.

## Video Fallback

The selected archive currently resolves every main or quoted playable-video reference to a local MP4. If future records lack a playable variant, thumbnail-only video records show a play affordance and open the original post on X rather than pretending that a JPEG is playable.

## Native Video Lifecycle

Playable videos use `preload="none"`, `muted`, `playsinline`, and controls. An `IntersectionObserver` mounts the archived MP4 and starts muted playback when at least 55% of the video enters view. On exit it pauses, removes the source, and reloads the empty element, preventing dozens of off-screen decoders and network streams from remaining active.

Autoplay can still be denied by browser policy; controls remain available.

## Refreshing Assets

A future refresh should:

1. Generate a new authenticated full bookmark export.
2. Update the manual curation ledger.
3. Run `npm run archive-assets`.
4. Run `npm run prepare-data`.
5. Verify all `/assets/` references in both JSON payloads exist before building.

Do not label a thumbnail as a playable archived video unless a real source exists.
