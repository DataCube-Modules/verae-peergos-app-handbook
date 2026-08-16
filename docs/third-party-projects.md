# Third-party Peergos app projects

Peergos apps are HTML5. Most “third party” work is either (1) a folder in
[Peergos/example-apps](https://github.com/Peergos/example-apps) that wraps
an existing MIT/Apache project, or (2) a Verae DataCube app that uses the
same `peergos-app.json` contract.

This repo vendors the official collection at
[example-apps/](../../example-apps/) (same tree as upstream).

## Official collection (installable)

Grouped the way the live gallery lists them. Folder name is the
`appName` you pass to Install.

### Documents and office

| Folder | Upstream | License note |
| --- | --- | --- |
| `ck-editor` | https://github.com/ckeditor/ckeditor5 | Rich text → `.html` |
| `doc-viewer` | docxjs + xwiki office-converters | Default `.docx`/`.odt` viewer |
| `doc2html` | mammoth.js + office-converters | `.docx`/`.odt` → `.html` |
| `html2doc` | html-to-docx-js-client-demo | `.html` → `.docx` |
| `luckysheet` | Luckysheet + office-converters | `.sheet`, import `.xlsx`/`.ods` |
| `luckysheet2excel` | Luckyexcel | `.sheet` → `.xlsx` (experimental) |
| `weboffice` | allotropia/zetajs LibreOffice | Full office suite (large WASM) |
| `file2pdf` | zetajs convertpdf | Office → PDF (large WASM) |
| `pandoc` | tweag/pandoc-wasm | Universal converter (large WASM) |
| `notes` | Editor.js | `.note` block editor |
| `tui-markdown-editor` | nhn/tui.editor | WYSIWYG markdown |
| `texteditor` | textarea | Minimal |
| `pretty-diff` | prettydiff | Diff two text files |
| `ebookreader` | epub.js | `.epub` |
| `docx-to-html` | XSweet | Needs SaxonJS for full function |

### Drawing and diagrams

| Folder | Upstream |
| --- | --- |
| `tldraw` | tldraw v1 (MIT, 2021–22) — `.tldr` |
| `drawio` | jgraph/drawio 21.2.7 — `.drawio` |
| `mindmaps` | mindmaps |
| `paintz` | ZMYaro/paintz |
| `jspaint` | 1j01/jspaint |
| `tui-image-editor` | nhn/tui.image-editor |
| `mini-photo-editor` | xdadda/mini-photo-editor |

### Media

| Folder | Upstream |
| --- | --- |
| `audio-player` | Luna music player |
| `webamp` | captbaritone/webamp |
| `vlc.js` | Krowemoh/vlc.js (WASM) |
| `image-slideshow` | Luna gallery |
| `img-viewer` | pwa-haven img-viewer |
| `album` | disintegration/quiet |
| `photoroll` | quiet (single-instance + HEIC) |
| `device-capture` | getUserMedia wrapper |
| `heic2jpg` | strukturag/libheif |
| `exiftool` | uswriting/exiftool WASM |
| `media-metadata-scrubber` | mini-exif |

### Notes, wiki, tasks

| Folder | Upstream |
| --- | --- |
| `tiddlywiki` | TiddlyWiki 5 |
| `feather-wiki` | Alamantus/FeatherWiki |
| `projectify` | thaddeusjiang/projectify |
| `todo` | DumbKan |
| `tasks` | Peergos sample |
| `todoMVC` | Vanilla TodoMVC 2022 |

### Mail, chat, forums

| Folder | Upstream |
| --- | --- |
| `email` | Peergos mailbox API sample |
| `chat` | Chat API v1 sample |
| `forum` | disintegration/bebop |
| `chat-api` | Tiny chat-API demo |

### Games and extras

| Folder | Upstream |
| --- | --- |
| `chess` | webxdc/ChessBoard.xdc |
| `tictactoe` | webxdc/tictactoe.xdc |
| `go` | ish.go |
| `sudoku` | raravi/sudoku |
| `doom` | jsdosbox shareware |
| `skymap` | IK-Pegasi |
| `calculator` | intel/webapps-scientific-calculator |
| `audio-recorder` | wavesurfer — upstream marks incomplete |

Skipped in the Verae gallery: `file-picker`, `folder-picker` (API tests),
`gwt-vue-min` (source only).

## Verae DataCube apps (this org)

| Folder / repo | What |
| --- | --- |
| `verae-app-sdk/hello-cube` | Create cube, append, local timestamp |
| `verae-app-itad` | IT asset disposition cube |
| `verae-app-wine` | Beverage provenance cube |
| `verae-app-signatures` | Sign / revoke object identities |
| `Verae-Peergos/org-admin` | Instance admin (`ADMIN_INSTANCE`) |

SDK: `verae-app-sdk` (`peergos-data.js`, `outbox.js`, `share-wizard.js`).
Apps never open NATS.

## Other Peergos GitHub projects (not HTML apps)

These are part of the Peergos ecosystem but are **not** `peergos-app.json`
packages:

| Project | Role |
| --- | --- |
| https://github.com/Peergos/Peergos | Server + client (Java) |
| https://github.com/Peergos/web-ui | Vue web interface + sandbox |
| https://github.com/Peergos/book | Tech book source |
| https://github.com/Peergos/nabu | Embedded IPFS |
| https://github.com/Peergos/example-apps | This collection |
| `email-bridge/` (this repo) | SMTP/IMAP bridge for the Email app |
| `rust-peergos-client/` | Rust client |

## How to add another third-party app

1. Wrap it as `assets/index.html` + `peergos-app.json` (see
   [building-apps.md](building-apps.md)).
2. Prefer an OSI license (MIT, Apache-2.0, MPL) and keep the upstream
   URL in `description`.
3. Drop the folder under `example-apps/<name>/` or a Verae app repo.
4. Add a row to `verae-ops/modules/peergos-apps/catalog.json`.
5. Run `publish.sh` so `/peergos/recommended-apps/<name>` is public.
