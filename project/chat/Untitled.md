# Chat UI symbol library — attachments + AI presentation (rev. 2026-09-09b)

**208 symbol masters** on the **Symbols** page of Sketch document `exegia-ui`
(cloud `01945ba6-1dcb-4f55-bc46-c0cf4d09aa7c`): 43 themed atoms ×2, 42 neutral atoms (icons +
thumbnails), 30 components ×2, 7 blocks ×2. Showcase frames (instances only) live on the
**Chat UI** page (`AB61527D-69F8-4CB2-91DC-E417036DF74B`): `Chat Attachments — Light|Dark`
(y 455) and `AI Presentation — Light|Dark` (y 1520), to the right of the user's empty
`Attachment` frame.

Design language: the `Exegia / *` chat symbols in `corpora - claude` (see `claude/chat-blocks.md`),
the ReUI `ai-chat-6` attachment card, and — for the presentation components — the
**Beautiful-UI** primitives (beautifului.dev: cool neutrals, hairline borders, radii chip 6 /
control 8 / card 10 / window 14, Inter + JetBrains Mono, single blue accent, semantic
green/orange/red used sparingly). Beautiful-UI structure and spacing were kept; colours were mapped
onto the Exegia token set. Type is **TikTok Sans** (UI) and **Menlo** (mono; JetBrains Mono isn't
installed on this Mac — swap the font family if it gets installed).

## Layering rule

- **Atom** — single-purpose primitive; may nest an Icon.
- **Component** — composed only of atoms (+ text).
- **Block** — composed of atoms **and** components.

Every themed master exists as a `— light` / `— dark` pair. Dark masters are generated from the
light ones by swatch remap (`Light / *` → `Dark / *`) + nested-instance re-pointing, so both trees
share layer names and override paths.

## Naming

| Layer | Masters |  |  |  |  |
| --- | --- | - | - | - | - |
| `Atom / Icon / <lucide-name>` (40, theme-neutral, tint on instance) | image, film, audio-lines, file-text, text-quote, reply, at-sign, link, x, play, download, external-link, paperclip, book-open, globe, plus, copy, share, list-plus, thumbs-up, thumbs-down, refresh-cw, corner-down-left, chevron-down, chevrons-up-down, check, code, eye, zap, split, sparkles, calendar, users, list-filter, file-code, maximize, pin, chart-column, quote, pencil |  |  |  |  |
| `Atom / Thumbnail / Small|Large` (neutral, image override) | |  |  |  |
| `Atom / … — light|dark` (43×2) | Icon Tile · Avatar / Handle 20 · Button / Remove, Play, Send, Add, Ghost, Primary Pill, Secondary Pill · Icon Button · Badge / File Type, Agent · Favicon · Waveform · Quote Rail · Duration Pill · Pill · Tag / Amber, Purple, Blue, Green · Dot / Success, Warning, Info, Danger, Neutral, Accent, Brand, Series 3, Series 4 · Signal / High, Medium, Low · Checkbox / Empty, Checked · Segmented Toggle (+ `/ Right`) · Legend Item · Source Chip · Avatar Stack · Stat / Negative, Positive · Follow-up Row |  |  |  |
| `Component / Attachment / <Type> / Default|Preview — light|dark` (15×2) | Image, Media (+ `Preview Audio`), Document, Text Selection, Chat Reply, Username Handle, URL Link |  |  |
| `Component / Chart / Pie|Area|Line|Bar — light|dark` (4×2) | 320×244 card: title/subtitle, type pill, plot (SVG-imported shapes, swatch-bound), x-labels, legend |
| `Component / Markdown / Preview|Markup — light|dark` | rendered markdown vs raw source, `Preview | Markup` toggle, copy/expand |  |
| `Component / Research Answer — light|dark` | content, Source (corpus), Date, Author(s), controls: Copy citation · Share · Add to list · 👍/👎 |  |  |  |
| `Component / <Beautiful-UI> — light|dark` (8×2) | Streaming Text (inline source chip, caret, actions, sources panel, follow-ups) · Recommendation Card · Context Cards · Code Block · Filter Table · Records Table · Flowchart · Insight Cards (nests chart plot + stats) |  |  |  |
| `Block / Message / … — light|dark` (3×2) | Sender + Attachment, Recipient + Attachment, Composer / With Attachments |  |  |  |
| `Block / AI Bubble / … — light|dark` (4×2) | Markdown, Research Answer, Chart, Streaming — agent header (sparkles tile · `Exegia` · Agent badge · time) + content |  |  |  |

## Swatches (103 colour variables)

Base: `Background / Page`, `Surface / Card|Subtle|Canvas|Code|Bubble Sender|Bubble Recipient`,
`Border / Default`, `Text / Primary|Secondary|Muted|Inverse`, `Accent / Default|Subtle|Text`,
`Link / Default`, `Icon / Default`, `Overlay / Scrim|On Media`, `Brand / Primary`.
Added this round: `Semantic / Success|Warning|Danger|Info` (+ `Subtle`), `Chart / Series 1–5`,
`Chart / Grid`, `Chart / Area Fill`, `Code / Keyword|String`, `Tag / Amber|Purple|Blue|Green
Text|Fill|Border` — each as `Light / …` and `Dark / …`.

| Role | Light | Dark |
| --- | --- | --- |
| page · card · subtle | `#f4f4f5` · `#ffffff` · `#0000000f` | `#2c2c2c` · `#252525` · `#ffffff14` |
| canvas · code | `#fafafa` · `#f7f7f8` | `#1f1f1f` · `#1b1b1b` |
| border | `#00000020` | `#ffffff1f` |
| text 1/2/3 | `#1a1a1a` / `#6b6b6b` / `#9a9a9a` | `#f2f2f2` / `#b3b3b3` / `#808080` |
| accent / brand | `#a153ff` / `#f7b500` | `#b171ff` / `#f7b500` |
| success / warning / danger / info | `#25a878` / `#f09a2f` / `#e5484d` / `#3b82f6` | `#3fc48f` / `#f5ad4f` / `#f26b6f` / `#6aa1ff` |
| chart series 1–5 | accent, gold, `#3b82f6`, `#25a878`, `#f26d5b` | lighter twins |

## Symbols-page layout

`§ …` text labels mark each row. Light: y 2000/2030 icons · 2080 atoms · 2300 attachment Default ·
2400 Preview · 2700 message blocks · 2900 charts + markdown + research · 3300 Beautiful-UI
components · 3700 flowchart + insights · 4200 AI-bubble blocks. Dark: atoms +900; everything from
2900 onward +1800.

## Sketch MCP traps (keep)

- `swatch.referencingColor` is `undefined` → set `fill.color = swatch.color` **then** `fill.swatch = swatch`.
- **Resizing a Frame after children exist scales the children** (relative sizing by default). Either
  create the frame at its final size, or first set every child's `horizontal/verticalSizing = Fixed`
  and pins to `Min`, then resize. A `Fill` rectangle inside a stack is hit by every later
  `stackLayout.apply()` too — fix its sizing/frame/pins **last**.
- `text.frame = {…}` silently makes the text **fixed-width**; set `fixedWidth = false` afterwards
  for labels that must grow with overrides (tags, pills, legend, buttons).
- Instance overrides don't trigger Smart Layout via the API — size instances explicitly (measure a
  temp Text layer with the same style).
- `doc.getSymbolMasterWithID()` is `undefined` for a non-selected document; use `doc.getSymbols()`.
- SVG import (`createLayerFromData(svg,'svg')`) keeps `id` attributes as layer names — use that to
  bind fills/borders to swatches after import (charts, icons).
- Frame corner radii clip only when uniform; for top-only rounding use a `masksSiblings` rect.
- Duplicating a master regenerates nested layer IDs → re-apply `symbolID`/`stringValue` overrides
  by matching instance **name**, and for multi-override instances match the override `path` against
  the nested layer's id (the Code Block toggle mismatched otherwise).
- JetBrains Mono / Inter aren't installed — Sketch silently falls back to Helvetica; check
  `text.style.fontFamily` after setting it.

## Open items

- Markdown bold/inline-code runs are plain text (no attributed ranges via the JS API).
- Chart plots are static SVG shapes; changing data means re-importing (generator lives in this
  session's scratchpad, easy to regenerate).
- Flowchart dot-grid is 260 tiny ovals in a group — fine, but replace with a pattern fill if it slows the file.
- No agent/user avatar artwork yet; AI bubbles use a sparkles Icon Tile.
- The user's empty `Attachment` frame on Chat UI is untouched.
