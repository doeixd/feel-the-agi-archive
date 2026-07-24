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

## Current Video Limitation

The current Birdclaw sync has 972 records containing video-related data, but their `media_json` entries only contain JPEG thumbnail URLs such as:

```text
https://pbs.twimg.com/amplify_video_thumb/.../img/...jpg
```

There are no `video_info` objects, MP4 variants, or downloaded MP4/WebM files in the current cache. Consequently, these records cannot be honestly autoplayed from archive data.

The UI handles this in two ways:

1. Thumbnail-only video records show a play affordance and open the original post on X.
2. If a future Birdclaw export includes `type: video` plus MP4 `variants`, the site renders a native video element.

## Native Video Lifecycle

Playable videos use `preload="none"`, `muted`, `playsinline`, and controls. An `IntersectionObserver` mounts the highest-bitrate MP4 and starts muted playback when at least 55% of the video enters view. On exit it pauses, removes the source, and reloads the empty element, preventing dozens of off-screen decoders and network streams from remaining active.

Autoplay can still be denied by browser policy; controls remain available.

## Future Video Backfill

Birdclaw's importer supports media records with `video_info.variants`, but the live bookmark payload used here did not provide them. A future refresh should:

1. Use a live transport that returns full extended media entities.
2. Verify `media_json` contains `type: video` and MP4 variants.
3. Run `birdclaw media fetch --include-video`.
4. Re-run `npm run prepare-data`.
5. Verify MP4 URLs or local media paths are represented in `public/tweets.json`.

Do not label a thumbnail as a playable archived video unless a real source exists.
