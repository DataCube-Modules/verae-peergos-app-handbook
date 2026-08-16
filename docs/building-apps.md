# How to build a Peergos app

A Peergos app is a folder of HTML, JavaScript, and CSS plus a
`peergos-app.json` manifest. At runtime the assets are served on a **unique
subdomain** (`sha256(app path).$public-domain`) in a separate browser process
with a locked-down Content-Security-Policy. Network calls never leave the
sandbox: a service worker turns them into `postMessage`s that the main Peergos
tab checks against the permissions the user granted.

Install apps only from authors you trust. Until browsers implement WebRTC CSP,
a malicious app could theoretically open a WebRTC channel.

Official chapter (full REST tables):
[protocol/peergos-book-apps.md](../protocol/peergos-book-apps.md)
and https://book.peergos.org/features/apps.html.

## 0. Pick a pattern first

Do not start from a blank page. Copy one pattern from
[existing-apps-architecture.md](existing-apps-architecture.md):

| If you need | Copy |
| --- | --- |
| DataCube + timestamp / append | `hello-cube` (pattern A) |
| Edit a Drive file | `texteditor` (pattern B) |
| Play a folder | `audio-player` (pattern C) |
| Shared album / chat | `album` (pattern D) |
| Convert a file | `doc2html` (pattern E) |
| Wrap WASM/JS | luckysheet / weboffice (pattern F) |
| Instance admin | `org-admin` (pattern G) |

What to build next: [additional-apps-plan.md](additional-apps-plan.md).

## 1. Folder layout

```
my-app/
  peergos-app.json      # required manifest
  assets/
    index.html          # required entry point
    icon.png            # optional, referenced as appIcon
    empty.note          # optional placeholder for newFileExtensions
    ...                 # css, js, wasm, fonts
```

After **Install App**, Peergos copies this into the user’s space:

```
/<username>/.apps/<app-name>/
  peergos-app.json      # manifest plus a "source" path
  assets/               # copy of your assets
  data/                 # private store if STORE_APP_DATA is granted
```

The installer also writes `peergos-app-previous.json` into `data/` when you
update.

Do **not** put `.git`, Go sources, or docs in the published folder. The
Verae publisher keeps only `peergos-app.json` and `assets/`.

## 2. Manifest (`peergos-app.json`)

| Field | Notes |
| --- | --- |
| `schemaVersion` | Always `1` |
| `displayName` | ≤ 25 chars, letters, numbers, dash, underscore |
| `version` | `Major.Minor.Patch[-suffix]`, e.g. `0.1.0` |
| `description` | ≤ 100 chars |
| `author` | ≤ 32 chars |
| `launchable` | Show on the Apps launcher |
| `folderAction` | Offer in a folder context menu |
| `fileExtensions` | e.g. `["cube","docx"]` — Drive “Open with” |
| `mimeTypes` | e.g. `["application/vnd.peergos-todo"]` |
| `fileTypes` | `image`, `video`, `audio`, `text` |
| `appIcon` | File name inside `assets/` |
| `newFileExtensions` | `[{ "extension": "cube", "name": "Verae DataCube" }]` |
| `template` | `messaging` (multi-instance, shareable) or `messaging-instance` (one install) |
| `permissions` | See [sandbox-api.md](sandbox-api.md) |

Minimal launchable app:

```json
{
  "schemaVersion": 1,
  "displayName": "Hello",
  "description": "does something",
  "version": "0.1.0",
  "author": "Verae",
  "launchable": true
}
```

Verae DataCube apps typically request
`STORE_APP_DATA`, `EDIT_CHOSEN_FILE`, and `READ_CHOSEN_FOLDER`. Org Admin
also needs `ADMIN_INSTANCE` (instance operators only).

Set `launchable: true` while developing so Drive can **Run App** on the
manifest without a full install.

## 3. Sandbox rules

- The app origin is **not** `peergos.georgelambert.org`. It cannot read the
  user’s cookies or talk to the Peergos REST API with the user’s session
  cookie.
- Default permissions: **none**. The app can only read its own `assets/`.
- `fetch("/peergos-api/v0/...")` is intercepted by
  `web-ui/assets/apps/sandbox/sw-sandbox.js`. FormData POSTs become JSON.
- External `fetch` to the public internet is blocked by CSP.
- Detect dark mode and the launched file/folder:

```js
const url = new URL(window.location.href);
const filePath = url.searchParams.get("path");
const theme = url.searchParams.get("theme"); // "dark-mode" or ""
```

## 4. What the app is allowed to do

See [sandbox-api.md](sandbox-api.md) for every endpoint. Common patterns:

| Want | Permission | API |
| --- | --- | --- |
| Private files for this app | `STORE_APP_DATA` | `GET/PUT/POST/PATCH/DELETE /peergos-api/v0/data/...` |
| HTML form → file | `STORE_APP_DATA` | `POST /peergos-api/v0/form/...` |
| Edit the file the user opened | `EDIT_CHOSEN_FILE` | `PUT` that file (no `/data/` prefix) |
| List the folder the user opened | `READ_CHOSEN_FOLDER` | `GET` the folder |
| Chat with friends | `EXCHANGE_MESSAGES_WITH_FRIENDS` | `/peergos-api/v0/chat/` or `/v1/chat/` |
| Email | `USE_MAILBOX` | `/peergos-api/v0/mailbox/` |
| Friend avatars | `ACCESS_PROFILE_PHOTO` | `/peergos-api/v0/profile/:user?thumbnail=true` |
| Save-as dialog | (none extra) | `POST /peergos-api/v0/save/name.txt` |
| File / folder picker | (none extra) | `GET /peergos-api/v0/file-picker`, `/folders` |
| `eval` / compile-to-JS | `CSP_UNSAFE_EVAL` | only if you must |

Apps **cannot** open NATS, raw TCP, or the host filesystem. Verae DataCube
apps write an envelope to `data/outbox/` and a **connector** on the desktop
host publishes it. See `verae-app-sdk`.

## 5. Local development loop

1. Put the folder in your Peergos Drive (drag-and-drop or `OrgTool put-dir`).
2. Context menu on `peergos-app.json` → **Run App** (launchable) or **Install App**.
3. Edit `assets/`, re-upload, Run App again. Install replaces `assets/` and
   merges `data/`.
4. Bump `version` when you publish so **Apps → Update** sees a newer source.

CLI (needs `Peergos.jar` + Java 21):

```bash
java -cp Peergos.jar:classes OrgTool install-app \
  https://peergos.georgelambert.org "$USER" "$PASS" hello-cube ./hello-cube
```

`install-app` writes `/.apps/<name>/` the same way the web wizard does.

## 6. Publish to the instance gallery

The launcher **Custom** button opens `/peergos/recommended-apps/index.html`
if that file is larger than 20 bytes. `pki-init` writes a 13-byte stub.

On ns1, with the PKI user `peergos` password (CT 501 `PEERGOS_PASSWORD`):

```bash
# from verae-ops
export JAR=/tmp/Peergos.jar RESEARCH=$HOME/research
# 0600 file, no echo
./modules/peergos-apps/publish.sh
```

That stages every official `example-apps` folder plus the Verae apps, uploads
with `OrgTool put-catalog`, and `make-public`s each child.

Users still click **Install** once. Installed copies live in their `.apps/`.

## 7. Recommended first apps to read

| Path | Why |
| --- | --- |
| `verae-app-sdk/hello-cube/` | Smallest Verae DataCube app |
| `example-apps/texteditor/` | Tiny launchable editor |
| `example-apps/notes/` | `newFileExtensions` + `STORE_APP_DATA` |
| `example-apps/chat/` | Chat API v1 |
| `example-apps/email/` | Mailbox API |
| `org-admin/` | `ADMIN_INSTANCE` |

## 8. Verae DataCube extras

- Cubes are a **directory tree + append-only SQLite**, not Postgres.
- Dual hashes SHA-256 + BLAKE3; share modes A / B / C.
- Timestamps: Local / Shared / Global (`api.veraetime.net` for Global).
- Do not call NATS from the sandbox. Use `verae-app-sdk` `outbox.js`.
- Iceberg in this stack is a **CID catalog**, not the cube format.

## 9. Where the rest lives

- Lectures and slides: [lectures-and-talks.md](lectures-and-talks.md)
- Third-party wrappers: [third-party-projects.md](third-party-projects.md)
- API tables: [sandbox-api.md](sandbox-api.md)
- Protocol book: `book/` (mdbook → https://book.peergos.org)
- Matrix: https://matrix.to/#/#peergos-chat:matrix.org
