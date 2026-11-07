# AVIA frontend design spec

Covers every page in `web/`. Tokens live in `web/app/globals.css`, and this file explains how to use them. `DESIGN.md` records the same system in the Impeccable format.

## Concept

Apple boxes carry their count on the end. AVIA earns that number from video, so the site is a box end and the count is the stamp. Working pages use label paper, and the only apples shown are real tracked footage.

Three rules follow from this:

1. **Show the result first.** The home page opens on tracked video and a working upload.
2. **Every number says how it was measured.** Anything unmeasured reads "pending". There are no estimates.
3. **One colour means "current or failed".** On paper, red marks what is happening now or what went wrong: the playhead, active step, current row, selected filter, progress fill, failed step and error text. On blue, straw does that job.

## Tokens

| Token | Value | Use |
|---|---|---|
| `--label` | `#14296b` | Blue ground: header, footer, page heads, hero |
| `--label-raised` | `#1c3a8c` | Primary button on paper, hover on blue |
| `--label-rule` | `#5f7bc9` | Rules and dropzone border |
| `--on-label` | `#f4f6fa` | Text on blue |
| `--on-label-soft` | `#cfd9f0` | Secondary text on blue |
| `--straw` | `#f7d65c` | Wordmark, count plate, primary action on blue, current marker on blue |
| `--straw-deep` | `#e6bd2e` | Straw hover, notice border |
| `--paper` | `#f4f6fa` | Page ground (cool, not cream) |
| `--paper-raised` | `#ffffff` | Dropzone, count box, tooltip |
| `--rule` | `#cdd5e6` | Table and section rules (baseline bars use `--label-rule`, for 3:1 on paper) |
| `--ink` | `#101d4d` | Text on paper |
| `--ink-soft` | `#46527a` | Secondary text on paper |
| `--apple` | `#c8201a` | Current state on paper, errors |
| `--wash` | `#fdf2c4` | AVIA's table row, notices, hover on quiet buttons |
| `--series-1` | `#2a55c8` | Chart: counted so far; AVIA's bar |
| `--series-2` | `#c2570c` | Chart: in view |
| `--grid` | `#dfe4ef` | Chart grid, progress track |

The site has one light theme and no dark mode. People use it in daylight, on a laptop or phone at the orchard. The chart pair passed the palette validator against `--paper`: lightness band, chroma, colour-vision separation and 3:1 contrast.

## Type

| Role | Face | Size |
|---|---|---|
| Display `h1` | Stardos Stencil 700, uppercase | `clamp(2.5rem, 6.4vw, 5.25rem)`, line height 0.98 |
| Section `h2` | Stardos Stencil 700, uppercase | `clamp(1.75rem, 3.4vw, 2.75rem)`. The count box `h2` is Libre Franklin 700 at 1rem |
| Count roller | Stardos Stencil 700 | `clamp(2.75rem, 6vw, 4.5rem)`; `clamp(3.5rem, 7vw, 5rem)` in the count box; 2.5rem on the plate at 520px and below |
| Lede | Libre Franklin | `clamp(1.125rem, 1.7vw, 1.3125rem)`, 56ch |
| Body | Libre Franklin 400 | 1.0625rem / 1.55, 52ch (about 75 characters in this face) |
| Small print | Libre Franklin | 0.875rem |

Both faces load through `next/font/google`, which self-hosts them at build time. All numbers use tabular figures.

## Shape and space

- Corners are square everywhere.
- Frames are ruled. The picture window is a 2px straw rule, a 7px gap, then the video.
- The content width is 1200px with a gutter of `clamp(16px, 4vw, 40px)`.
- Bands use `clamp(56px, 8vw, 104px)` of vertical padding.
- The chart tooltip is the only element with a shadow.

## Motion

The signature interaction is the count roller (`components/Roller.tsx`). It runs on the home hero and the run page, driven by the video's playhead.

- Each digit is a 0–9 column that moves in whole line-heights, 180ms, `cubic-bezier(0.16, 1, 0.3, 1)`. The step is shorter than the video's 250ms time updates, so digits land and can be read during playback.
- Digits are zero-padded to the total's width, so the plate never changes size.
- Screen readers get one real number, and the digit columns are hidden from them.
- Nothing fades in. A state change is one physical step, and a failed step stops where it is and says why.
- `prefers-reduced-motion` removes transitions and leaves the numbers correct.

## Pages

### Shared layout

The header carries the wordmark and three links. The current page has a 2px straw underline. The footer keeps the dataset credit, DOI link and a line saying where the example footage comes from.

### Home (`/`, Persuade)

1. **Hero on blue.** Heading, lede, working dropzone, and the tracked clip in the picture window with the straw count plate rolling in step. All of it fits in 1440×900. Viewports of 901px and wider that are 820px or shorter move the heading into the left column, which fits 1366×768. The plate shows the finished count until the clip is playing, so it never sits on 000. If `play()` is refused or reduced motion is set, the player's controls appear.
2. **Why tracks.** "Adding up frames overcounts", with a two-row tally of apple outlines against distinct apples. Both numbers come from the lead clip's real data. The copy describes the mechanism and states its limit: a short gap can be bridged, and a longer one can start a new track.
3. **Finished examples.** Video tiles with a straw count stamp.
4. **Evidence.** Measured scores beside the published baselines, naming the scorer.
5. **Closing band on blue.** Links to upload and limits.

The lead clip is the oldest run from a trained model, because the poster is that clip's first frame. With no trained run it falls back to the newest run. If there is no run or the API is down, the hero shows the poster with a plain message. The caption says the model misses some apples and that the grey patches are part of the dataset footage. The evidence table's text says the baselines are published figures.

### Try a video (`/upload`, Operate)

The dropzone comes first, with limits under it and a "You get back" list beside it. While working it shows the steps Upload, Queue and Track with the active one marked, plus file name, progress, percent and a line asking the visitor to keep the page open. On failure the steps and file name stay, the step that failed is marked, the message follows, and the dropzone returns as "Choose another video". A lost event stream counts as a failure, so progress never sits frozen.

### Run result (`/runs/[id]`, Operate)

The video sits beside a count box with the roller, in-view count, frames and model. Until the first play or seek, the roller shows the finished count. Processing speed appears on uploaded runs only: the examples were prepared offline, so their speed means nothing and Benchmarks carries the measured figure. A line under the box defines the count as tracks seen in at least three frames. On examples it says the clip is a labelled test sequence whose count was not compared with the labels. On uploads it says the count has no ground truth. Both link to the benchmarks. Below are the count chart with a table view, events, and all tracks. Events open on the first 25 with a "Show all" button and a filter for each event type, each showing its count, so nothing is cut off silently. The tracks summary states how many tracks were confirmed, which explains why it differs from the count. Each event time is a real button with a 44px target, so seeking works from the keyboard. Rows also seek on click, and a seek brings the video into view. Processing speed keeps two decimals below 1 fps.

### Benchmarks (`/benchmarks`, Read)

Single-series sMOTSA bars with direct labels, the full score table with AVIA's row in wash, a per-sequence table, and how the scores were measured. Mask HOTA shows "pending" until it exists. If AVIA is unscored, its cells read "pending" and a notice explains why.

### About (`/about`, Read)

A blue head, then a 52ch reading column. How it works and Limits describe what the system does and where it fails, using the same terms as the home page.

## States

| State | Treatment |
|---|---|
| Loading | Plain "Loading…" in muted text; the poster holds the hero |
| Empty | Plain sentence, no illustration |
| Error | `--apple` text on paper, straw on blue, said in a full sentence. The hero fallback uses caption colour |
| Untrained model | Wash notice saying the numbers say nothing about accuracy |
| Hover | Colour step at 160ms, no movement. Example cards use a blue rule, because red means current |
| Focus | 2px ring, blue on paper, straw on blue |
| Disabled | 50% opacity, `not-allowed` cursor |

## Responsive

- At 900px and below, every two-column layout stacks. The home hero order becomes heading, clip, dropzone, lede, and the picture window narrows to 16:10, so the result and the action share the first screen.
- At 520px and below, the count plate tightens and score and track tables tighten their cell padding. The event table moves Basis under the event name, and the per-sequence table drops Frames, so no column needs a sideways scroll.
- Tables scroll inside their own wrapper as a fallback, so the page never scrolls sideways.

## Accessibility

- Text meets 4.5:1 and interface elements 3:1 on their grounds. The progress track and notice border sit below 3:1 on purpose: the fill and the text carry the meaning.
- `aria-current` marks the current nav link, upload step and event row.
- Upload progress sits in a polite live region, and errors use `role="alert"`.
- The chart has a table view.
- Every tracked video is muted and labelled.

## Patterns from real products

| Pattern | Source | Used in |
|---|---|---|
| Live vision result in the opening view | Roboflow | Home hero |
| Plain outcome headline with a how-it-works route | Aerobotics | Home heading and evidence link |
| Framing per unit, tree by tree | Green Atlas | Per-apple counting |
| Demo first, each claim linked to its evidence | Meta SAM 2 | Evidence section, run page link to benchmarks |

## Watermelon UI

Nothing was installed, because `web/` has no Tailwind and the stack rule says not to add it. Two ideas were read from source and rebuilt in plain CSS:

- `pagination`: per-digit overflow columns became the count roller.
- `file-upload-2`: the dropzone and per-file progress row became `UploadForm`.

## Data the design expects

The design adds no endpoints. It reads the existing API, plus the `sequences` and `hardware` fields that `/api/benchmarks` already returns.
