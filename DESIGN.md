---
name: AVIA
description: Segment, track and count apples in orchard video.
colors:
  label: "#14296b"
  label-raised: "#1c3a8c"
  label-rule: "#5f7bc9"
  on-label: "#f4f6fa"
  on-label-soft: "#cfd9f0"
  straw: "#f7d65c"
  straw-deep: "#e6bd2e"
  apple: "#c8201a"
  paper: "#f4f6fa"
  paper-raised: "#ffffff"
  rule: "#cdd5e6"
  ink: "#101d4d"
  ink-soft: "#46527a"
  wash: "#fdf2c4"
  series-1: "#2a55c8"
  series-2: "#c2570c"
  grid: "#dfe4ef"
typography:
  display:
    fontFamily: "Stardos Stencil, Libre Franklin, Arial, sans-serif"
    fontSize: "clamp(2.5rem, 6.4vw, 5.25rem)"
    fontWeight: 700
    lineHeight: 0.98
    letterSpacing: "0.005em"
  headline:
    fontFamily: "Stardos Stencil, Libre Franklin, Arial, sans-serif"
    fontSize: "clamp(1.75rem, 3.4vw, 2.75rem)"
    fontWeight: 700
    lineHeight: 1.04
    letterSpacing: "0.005em"
  count:
    fontFamily: "Stardos Stencil, Libre Franklin, Arial, sans-serif"
    fontSize: "clamp(2.75rem, 6vw, 4.5rem)"
    fontWeight: 700
    lineHeight: 1
  tally:
    fontFamily: "Stardos Stencil, Libre Franklin, Arial, sans-serif"
    fontSize: "clamp(2rem, 4.4vw, 3.25rem)"
    fontWeight: 700
    lineHeight: 1
  wordmark:
    fontFamily: "Stardos Stencil, Libre Franklin, Arial, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "0.06em"
  lede:
    fontFamily: "Libre Franklin, Franklin Gothic Medium, Arial, sans-serif"
    fontSize: "clamp(1.125rem, 1.7vw, 1.3125rem)"
    fontWeight: 400
    lineHeight: 1.42
  body:
    fontFamily: "Libre Franklin, Franklin Gothic Medium, Arial, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Libre Franklin, Franklin Gothic Medium, Arial, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 600
  button:
    fontFamily: "Libre Franklin, Franklin Gothic Medium, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 700
    lineHeight: 1.2
  small:
    fontFamily: "Libre Franklin, Franklin Gothic Medium, Arial, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.45
rounded:
  none: "0px"
spacing:
  gutter: "clamp(16px, 4vw, 40px)"
  width: "1200px"
  band: "clamp(56px, 8vw, 104px)"
  page-head: "clamp(28px, 4vw, 48px)"
  section: "clamp(40px, 6vw, 64px)"
  window-gap: "7px"
  tile-gap: "5px"
components:
  button-primary:
    backgroundColor: "{colors.label-raised}"
    textColor: "{colors.on-label}"
    typography: "{typography.button}"
    rounded: "{rounded.none}"
    padding: "10px 22px"
    height: "46px"
  button-primary-hover:
    backgroundColor: "{colors.label}"
  button-primary-on-label:
    backgroundColor: "{colors.straw}"
    textColor: "{colors.ink}"
    typography: "{typography.button}"
    rounded: "{rounded.none}"
    padding: "10px 22px"
    height: "46px"
  button-primary-on-label-hover:
    backgroundColor: "{colors.straw-deep}"
  button-quiet:
    backgroundColor: "transparent"
    textColor: "{colors.label-raised}"
    typography: "{typography.button}"
    rounded: "{rounded.none}"
    padding: "10px 22px"
    height: "46px"
  button-quiet-hover:
    backgroundColor: "{colors.wash}"
  button-quiet-on-label:
    backgroundColor: "transparent"
    textColor: "{colors.straw}"
    typography: "{typography.button}"
    rounded: "{rounded.none}"
    padding: "10px 22px"
    height: "46px"
  button-quiet-on-label-hover:
    backgroundColor: "{colors.label-raised}"
  nav-link:
    textColor: "{colors.on-label}"
    typography: "{typography.label}"
    padding: "8px 0"
  dropzone:
    backgroundColor: "{colors.paper-raised}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "32px 20px"
    height: "260px"
  dropzone-hover:
    backgroundColor: "{colors.wash}"
  dropzone-on-label:
    backgroundColor: "transparent"
    textColor: "{colors.on-label}"
    rounded: "{rounded.none}"
    padding: "18px 16px"
    height: "112px"
  dropzone-on-label-hover:
    backgroundColor: "{colors.label-raised}"
  count-plate:
    backgroundColor: "{colors.straw}"
    textColor: "{colors.ink}"
    typography: "{typography.count}"
    rounded: "{rounded.none}"
    padding: "10px 16px 8px"
  count-stamp:
    backgroundColor: "{colors.straw}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "6px 12px 3px"
  count-box:
    backgroundColor: "{colors.paper-raised}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "16px 18px"
    width: "280px"
  notice:
    backgroundColor: "{colors.wash}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "12px 16px"
  table-row-own:
    backgroundColor: "{colors.wash}"
    textColor: "{colors.ink}"
  chart-tooltip:
    backgroundColor: "{colors.paper-raised}"
    textColor: "{colors.ink}"
    typography: "{typography.small}"
    rounded: "{rounded.none}"
    padding: "6px 10px"
  progress-on-paper:
    backgroundColor: "{colors.apple}"
    height: "10px"
  progress-on-label:
    backgroundColor: "{colors.straw}"
    height: "10px"
---

# Design System: AVIA

## Overview

**Creative North Star: "The Stamped Box End"**

Fruit boxes carry their count on the end, and AVIA earns that number from video. The site is built as that box end: printed blue label bands hold the identity and the action, plain label paper holds the working and reading content, and the count is a straw stamp sitting on real footage. The system is flat, square and ruled, with stencilled headings over a sober Franklin text face.

Density follows the page's job. The home page is poster-sized and breathes in wide bands. The run page is a working surface of video, chart and tables, set tighter and held in hairlines. Reading pages drop to a single measured column. The one light theme suits daylight use on a laptop or phone at the orchard; the paper is cool, never cream.

The only decoration is structure. There are no textures, gradients, illustrations or drawn fruit, and the only apples on screen are real tracked footage. One authored motion carries the personality: digits rolling in whole steps, driven by the video's playhead.

**Key Characteristics:**
- Two grounds only: blue label and cool paper, each with its own full set of foreground colors
- Stencil for headings and earned numbers, Franklin for everything else
- Square corners and ruled frames throughout
- Flat surfaces, with depth from rules and ground changes
- One color at a time means "current": red on paper, straw on blue
- A single signature motion, the count roller

## Colors

Printer's inks on a cool stock: a deep label blue and a warm straw do the identity work, a single apple red does the signalling, and everything else is blue-tinted neutral.

### Primary
- **Crate Label Blue** (#14296b): The ground for the masthead, footer, page heads, home hero and closing band.
- **Pressed Label Blue** (#1c3a8c): The action color on paper: primary button fill, quiet button text and border, dropzone heading, disclosure summaries, focus ring. On blue it is the hover and track step, one notch lighter than the ground.
- **Label Rule Blue** (#5f7bc9): Rules on blue, the dropzone's dashed border on paper, the nav hover underline and the scrollbar thumb. It holds 3.31:1 on the blue ground and 4.07:1 on white.

### Secondary
- **Stamp Straw** (#f7d65c): The stamp color. Wordmark, count plate, count stamps, the picture-window rule, primary action on blue, current marker on blue, errors on blue and text selection.
- **Deep Straw** (#e6bd2e): Hover step for straw fills, and the notice border.

### Tertiary
- **Apple Red** (#c8201a): Current state and failure on paper: the chart playhead, the active step and its progress fill, the selected event filter, the current event row, failed steps and error text. Also the text caret.

### Neutral
- **Label Paper** (#f4f6fa): The page ground.
- **White Stock** (#ffffff): Raised surfaces only: dropzone, count box, chart tooltip.
- **Hairline Blue-Grey** (#cdd5e6): Table rules, list rules and the rule between bands.
- **Stamp Ink** (#101d4d): Text on paper and the text on every straw fill; also the 1px and 2px frames on paper.
- **Soft Ink** (#46527a): Secondary text on paper, table headers, chart axis text and the struck-through wrong tally.
- **Straw Wash** (#fdf2c4): The pale highlight on paper: AVIA's own table row, notices, and hover on quiet buttons, dropzones and seekable rows.
- **Print on Label** (#f4f6fa): Text on blue. Same value as Label Paper, kept as its own token so the two grounds stay independent.
- **Soft Print on Label** (#cfd9f0): Secondary text on blue, ledes on page heads and the footer.

### Data
- **Counted Blue** (#2a55c8): The chart's "counted so far" line and AVIA's bar on Benchmarks.
- **In-View Orange** (#c2570c): The chart's "in view" line.
- **Chart Grid Grey** (#dfe4ef): Chart gridlines and the progress track on paper.

### Named Rules

**The One Current Color Rule.** On paper, Apple Red appears only on what is current or what has failed. On blue, straw does that job. Red is never decoration, and hover states never use it: example tiles hover to a blue rule for exactly this reason.

**The Two Grounds Rule.** Every element is set on either blue label or paper, and each ground has its own text, action, focus and current colors. Placing a component on blue swaps its colors; it never carries its paper colors across.

## Typography

**Display Font:** Stardos Stencil 700 (with Libre Franklin, Arial, sans-serif)
**Body Font:** Libre Franklin, variable (with Franklin Gothic Medium, Arial, sans-serif)

**Character:** A stencilled shipping mark over a plain American gothic. The stencil gives the identity and the numbers their weight; the Franklin stays out of the way so measurements read as exact. Both faces self-host through `next/font/google`.

### Hierarchy
- **Display** (700, clamp(2.5rem, 6.4vw, 5.25rem), 0.98): Page titles, uppercase and balanced. One per page.
- **Headline** (700, clamp(1.75rem, 3.4vw, 2.75rem), 1.04): Section headings, uppercase. The count box is the one exception: its heading is plain Franklin 700 at 1rem, a label for the number under it.
- **Count** (700, clamp(2.75rem, 6vw, 4.5rem), 1): The roller on the home plate. The run page's count box sets it larger, at clamp(3.5rem, 7vw, 5rem), and the plate drops to 2.5rem at 520px and below.
- **Tally** (700, clamp(2rem, 4.4vw, 3.25rem), 1): The large comparison numbers on home.
- **Wordmark** (700, 1.75rem, 1, 0.06em tracking): AVIA in the masthead, in straw.
- **Lede** (400, clamp(1.125rem, 1.7vw, 1.3125rem), 1.42): The opening sentence on the hero and page heads, up to 56ch.
- **Body** (400, 1.0625rem, 1.55): All running text, capped at 52ch, which renders at roughly 75 characters in this face.
- **Label** (600, 0.9375rem): Nav links, step names, event filters and fact rows.
- **Small** (400, 0.875rem, 1.45): Captions, limits, table headers, legends and the footer.

The dropzone heading is a further stencil use, uppercase at clamp(1.5rem, 3vw, 2rem), because choosing a video is the page's main act.

### Named Rules

**The Earned Stamp Rule.** Stencil is reserved for headings, the wordmark, the dropzone heading and counted numbers. Sentences, labels and table data are always Franklin.

**The Fixed Figures Rule.** Numerals never shift as they change. The body sets tabular figures globally, and the roller sets each stencil digit in a fixed 0.66em slot.

## Layout

Content sits in a centered 1200px column with a fluid gutter (clamp(16px, 4vw, 40px)). Full-width ground bands carry the color, and the column stays constant inside them. Sections on paper are separated by 1px hairlines and generous band padding (clamp(56px, 8vw, 104px)); inner sections on working pages use a tighter step (clamp(40px, 6vw, 64px)).

Two-column layouts are asymmetric to suit the content: 1fr and 1.5fr on the home hero, the reverse on upload, 0.8fr and 1.2fr for evidence, and a fluid column beside a fixed 280px count box on the run page. Reading pages use one 52ch column.

Responsive behavior is explicit. At 900px and below every two-column layout stacks, and the home hero runs heading, clip, action, lede so the result and the upload share the first screen. Viewports 901px and wider but 820px or shorter move the home heading into the left column so the clip and the action both fit. Picture windows use 4:3 at full width and 16:10 in both of those cases. At 520px and below the plate tightens, the event table folds Basis under the event name, and the per-sequence table drops Frames. Tables scroll inside their own wrapper as a fallback, so the page itself never scrolls sideways.

## Elevation & Depth

The system is flat. Depth comes from ground changes between blue and paper, a step to White Stock for the few raised surfaces, and ruled frames. The single shadow belongs to the chart tooltip, the only element that floats over content.

### Shadow Vocabulary
- **Tooltip lift** (`box-shadow: 0 4px 14px rgb(16 29 77 / 0.16)`): The chart tooltip only.

### Named Rules

**The Flat Box End Rule.** Printed surfaces do not lift. Nothing on a page takes a shadow, a gradient or a blur unless it genuinely floats over other content while the pointer is on it.

## Shapes

Every corner is square (0px): buttons, inputs, frames, plates, tooltips and progress bars. The chart's 4px playhead dots are the one round form, because they mark a point on a line.

Frames are ruled with a gap, like a printed picture border. The hero's picture window is a 2px straw rule, a 7px gap, then the video. Example tiles use a 1px ink rule and a 5px gap. The count box uses a 2px ink rule with no gap. Dashed 2px rules mean "drop something here" and appear only on the dropzone. Stamps sit flush in a frame's inner corner rather than floating free.

### Named Rules

**The Ruled Frame Rule.** Footage is framed by a rule and a gap, never by a corner radius or a shadow. Rule weight carries rank: 2px for the main object, 1px for repeated ones.

## Components

### Buttons
Heavy, flat and printed, with no movement on interaction.
- **Shape:** Square, 2px border matching the fill, at least 46px tall.
- **Primary:** Pressed Label Blue with Print on Label text on paper; Stamp Straw with Stamp Ink text on blue. Franklin 700 at 1rem, 10px 22px padding.
- **Hover / Focus:** A 160ms color step to the darker fill. Focus is a 2px outline at 2px offset, blue on paper and straw on blue.
- **Quiet:** Transparent with a 2px border and colored text. Hover fills Straw Wash on paper and Pressed Label Blue on blue.
- **Disabled:** 50% opacity with a not-allowed cursor. Styled, though no control sets it today.

### Dropzone
The site's one input, and a working object wherever it appears.
- **Style:** A dashed 2px rule around a stencil call to action, with a plain line under it. White Stock and Label Rule Blue on paper, 260px tall. Transparent with a straw rule on blue, at least 112px tall.
- **Hover / Drag:** The rule steps to Pressed Label Blue over Straw Wash on paper; the ground steps to Pressed Label Blue on blue.
- **Focus:** The same 2px outline, moved to the whole zone because the file input is hidden.
- **Failure:** The steps and file name stay, the failed step is marked, the message follows in a full sentence, and the zone returns as "Choose another video".

### Steps and Progress
- **Steps:** A row of Upload, Queue and Track in label type, with a 2px underline on the active step: Apple Red on paper, straw on blue. Done steps return to full ink.
- **Progress:** A 10px square bar over Chart Grid Grey on paper or Pressed Label Blue on blue, with a red or straw fill. Width steps at 300ms. File name, status words and percent sit around it in a polite live region.

### Notices
- **Style:** Straw Wash with a 1px Deep Straw border, 12px 16px padding, full width. Used only when a result needs a warning before it is read, such as an untrained model.

### Tables and Tallies
- **Tables:** No boxes and no zebra stripes. Bottom hairlines only, a 1px ink rule under the header, Small bold Soft Ink headers, right-aligned numbers.
- **Own row:** AVIA's row is the single Straw Wash row, in bold.
- **Seekable rows:** Rows hover to Straw Wash, and the current row's first cell turns Apple Red. The time in each row is a real button with a 44px target.
- **Event filters:** Plain text buttons with counts, 44px tall, marked by a 2px red underline when selected.
- **Tally:** Label left and stencil number right, between hairlines. The wrong figure is Soft Ink with a 3px strike through it.
- **Facts:** Small definition rows with the label in Soft Ink and the value at 600, right-aligned.

### Navigation
- **Style:** A blue masthead with the straw stencil wordmark at left and three label-weight links at right, closed by a 1px Label Rule Blue line.
- **States:** A transparent 2px underline at rest, Label Rule Blue on hover, straw on the current page. Colors step at 160ms.
- **Mobile:** The row stays and wraps, with gaps tightening and link padding growing to keep the touch target.

### Count Plate and Stamps
The site's signature object.
- **Plate:** A solid straw block flush in the picture window's bottom-right corner, a two-line Franklin label beside the rolling digits.
- **Stamp:** A smaller straw block flush in an example tile's bottom-left corner, stencil at 1.75rem, static.
- **Count box:** On working pages the same number sits in a White Stock box with a 2px ink rule, followed by the fact rows and a plain note on what the count means.

### Count Roller
Each digit is a 0 to 9 column that moves in whole line-heights over 180ms on `cubic-bezier(0.16, 1, 0.3, 1)`, shorter than the video's 250ms time updates so digits land and can be read during playback. Digits are zero-padded to the total's width, so the plate never changes size. Before playback the roller shows the finished count, never zeros. Screen readers get one real number and the digit columns are hidden from them. With reduced motion the transitions drop out and the numbers stay correct.

**The One Physical Step Rule.** A state change is a single physical step. Nothing enters with a fade or a slide, hovers change color without moving, and a failed step stops where it is and says why.

### Count Chart
Two stepped lines on one apple scale, because counts are whole numbers and should not slope. Series are labelled directly at the line ends as well as in a thin legend, three gridlines mark the scale, and a 2px Apple Red playhead follows the video. Clicking seeks. Every chart has a table view in a disclosure under it.

## Do's and Don'ts

### Do:
- **Do** set every new component on one of the two grounds and take its colors from that ground's set.
- **Do** use Apple Red (#c8201a) on paper and straw (#f7d65c) on blue for whatever is current, and for failure.
- **Do** frame footage with a rule and a gap: 2px straw and 7px for the lead picture, 1px ink and 5px for repeated tiles.
- **Do** set counted numbers in Stardos Stencil and give changing digits fixed slots.
- **Do** write "pending" in the value's own place when a figure is unmeasured.
- **Do** keep hover states at a 160ms color step on `cubic-bezier(0.16, 1, 0.3, 1)`, with no movement.
- **Do** give every chart a table view, and label lines and bars directly.
- **Do** keep tap targets at 44px, including small controls inside tables.
- **Do** keep text at 4.5:1 and interface elements at 3:1 on their ground.

### Don't:
- **Don't** add a dark theme. The site has one light theme.
- **Don't** warm the paper toward cream.
- **Don't** use Apple Red for emphasis, links, hover or decoration.
- **Don't** add corner radii to frames, buttons, plates or surfaces.
- **Don't** add shadows outside the chart tooltip.
- **Don't** show drawn or stock fruit. The only apples are real tracked footage.
- **Don't** add textures, gradients or blur to the grounds.
- **Don't** set sentences, labels or table data in the stencil face.
- **Don't** animate entrances. Add new motion only where a value is genuinely changing.
- **Don't** start a counter from zero before playback; show the finished count.
