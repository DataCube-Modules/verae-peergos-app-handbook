# Architecture of existing Peergos apps

This is the code-level map of what is already built. Use it before writing a
new app: copy the **pattern**, not a random folder.

Runtime (all apps): unique app hostname → service worker
(`web-ui/assets/apps/sandbox/sw-sandbox.js`) → `postMessage` to
`AppSandbox.vue` → permission check → Peergos filesystem or admin API.
The iframe gets `{type:'init', username, theme, appPath, chatId, props}`.

Launch context arrives as query params: `path` (chosen file or folder),
`theme` (`dark-mode` or empty), `username` (org-admin).

## Pattern catalog

| Pattern | Who uses it | Permissions | How I/O works |
| --- | --- | --- | --- |
| **A. DataCube + outbox** | hello-cube, itad, wine, signatures | `STORE_APP_DATA` (+ folder/file as needed) | `PUT /peergos-api/v0/data/cubes/...` and `/outbox/*.json`. Never NATS. |
| **B. Chosen-file editor** | texteditor, notes, tldraw, drawio, luckysheet, paintz, jspaint | `EDIT_CHOSEN_FILE` (some add `CSP_UNSAFE_EVAL`) | `fetch(pathFromQuery)` GET then PUT. No `/data/` prefix. |
| **C. Folder action** | audio-player, image-slideshow, album | `READ_CHOSEN_FOLDER` | `GET` the folder JSON `{files, subFolders}`, then GET each child. |
| **D. Messaging template** | album, photoroll, forum, chat | `EXCHANGE_MESSAGES_WITH_FRIENDS` + `template: messaging` | Chat v0/v1; multiple installs; Share on the launcher icon. |
| **E. Converter** | doc2html, html2doc, file2pdf, heic2jpg, pandoc | `EDIT_CHOSEN_FILE` or none; often not launchable | Open on a file, write a sibling via save-picker or chosen-file PUT. |
| **F. Vendor wrap** | luckysheet, weboffice, vlc.js, ck-editor, tiddlywiki | varies; WASM apps need large assets | `assets/` holds the upstream bundle; `index.html` is a thin host. |
| **G. Instance admin** | org-admin | `ADMIN_INSTANCE`, `STORE_APP_DATA` | `POST /peergos-api/v0/admin/<route>` JSON. |
| **H. Gallery** | `recommended-apps/index.html` | none (special `$$app-gallery$$`) | `POST /peergos-api/v0/install-app/` FormData `{path, appName}`. |
| **I. API demo** | chat-api, file-picker, folder-picker | minimal | Teaching samples; not shipped in the Verae gallery skip-list for pickers. |

Built-in (not `peergos-app.json`): Calendar, PDF, image/video, hex, social, Drive.

---

## Verae DataCube apps (pattern A)

All four product apps share `hello-cube/assets/sdk.js` (inlined `VeraeSDK`):

| Function | Does |
| --- | --- |
| `createClient()` | `PUT`/`GET` `/peergos-api/v0/data` + path |
| `cubePaths(id)` | `/cubes/<id>/` + `manifest.json` |
| `makeEnvelope(subject, payload, reply_file)` | Connector job |
| `enqueue(client, name, env)` | `PUT /outbox/<name>.json` |
| `SHARE_MODES` / `validateShare` | A proofs / B + metadata / C + files |

The **module** form lives in `verae-app-sdk/src/` (`peergos-data.js`,
`outbox.js`, `share-wizard.js`) and is tested with a fake `fetch`. The
sandbox cannot use ES modules from that path unless you bundle; that is
why each app copies `sdk.js` into `assets/`.

A desktop-host **connector** watches
`/<user>/.apps/<app>/data/outbox/` and publishes JetStream
`verae.<domain>.<resource>.<action>`. Replies land in `data/inbox/`.

### hello-cube (`verae-app-sdk/hello-cube/`)

- Manifest: launchable + folderAction; `fileExtensions: ["cube"]`;
  `newFileExtensions` for “Verae DataCube”.
- Click **Create cube + stamp** → write `manifest.json` + `note.json` →
  enqueue `verae.ts.request` `{hash, cube_id, scope:"local"}`.
- Smallest complete DataCube loop. Copy this first.

### itad (`verae-app-itad/`)

- Same SDK. Domain events: pickup → wipe → disposition.
- Writes `assets/server.json` and `wipe-cert.json`. Share-mode **C** is
  required to export the wipe cert (A would drop it).
- **Part-out** enqueues `verae.cube.append` with
  `{event_type:"parted_out", parent, parts}`.
- Go sources (`itad/`) are **not** in the published Peergos folder.

### wine (`verae-app-wine/`)

- Same SDK. Assets like `bottle.json` `{asset_type, vintage}`.
- ISO proof export is **out of sandbox**: `index.html` + `chain.json`
  assembled by xorriso on the host. The app only creates the cube + stamp.

### signatures (`verae-app-signatures/`)

- Not cube-rooted. Paths:
  `/signatures/valid/<id>.json` and `/signatures/revoked/<id>.json`.
- Sign records `{object_sha256, signer, created_at}` and stamps the hash.
- Revoke writes the revoked record; verification (Go, ed25519) is host-side.
- No K9/REQL.

### Wave-2 apps (pattern A)

| App | Repo | I/O |
| --- | --- | --- |
| Cube Browser | `verae-app-cube-browser` | Reads `data/cubes/*` only. No outbox. |
| Share Wizard | `verae-app-share-wizard` | Writes `share-plan.json` into the cube. |
| TS Inbox | `verae-app-timestamp-inbox` | Lists `data/inbox/*` receipts. |
| ISO Export | `verae-app-iso-export` | Enqueues `verae.cube.export` `{cube_id, format, share_mode}`. |
| ITAD Board | `verae-app-itad-board` | Kanban UI; appends via `verae.cube.append`. |
| Sig Verify | `verae-app-sig-verify` | Lists valid/revoked; enqueues `verae.sig.verify`. |
| Conn Status | `verae-app-connector-status` | Counts outbox pending vs inbox acked. |

Host connector (`Verae-Peergos/services/connectors/cube-nats`) watches
`.apps/*/outbox` and `.apps/*/data/outbox`, Request-replies
`verae.cube.export` (xorriso or zip named `.iso`) and `verae.sig.verify`
(valid vs revoked records). Share A keeps only manifest/chain/receipt/hash/share-plan.

### Cube file layout these apps assume

```
/.apps/<app>/data/
  cubes/<cube-id>/
    manifest.json      # cube_id, kind, share_mode
    <domain files>     # note.json, wipe-cert.json, assets/*.json
  outbox/<job>.json    # {subject, payload, reply_file?}
  inbox/<reply>.json   # written by the connector, not the app
  signatures/          # signatures app only
    valid/
    revoked/
```

---

## org-admin (pattern G)

Single file: `org-admin/assets/index.html` (~71 KiB). No framework.

```js
var API = '/peergos-api/v0/admin/';
function adminCall(route, body) {
  return fetch(API + route, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body || {})
  }).then(/* require res.ok */);
}
```

| Route | Body | Use |
| --- | --- | --- |
| `users` | `{}` | List local users |
| `user-details` | `{username}` | Quota, MFA, usage |
| `set-quota` | `{username, quota}` | Bytes (k/m/g/t parsed in UI) |
| `delete-mfa-credential` | `{username, credentialIdHex}` | |
| `delete-user` | `{username}` | |
| `create-tokens` | `{count}` | Signup tokens |
| `space-requests` | `{}` | Pending quota asks |
| `approve-space-request` | `{index}` | |
| `audit-log` | `{since}` | |

`username` comes from `?username=` (sandbox init). Non-admins get a
“not an admin” screen. Billing settings optionally persist at
`/peergos-api/v0/data/org-admin-billing.json` (`STORE_APP_DATA`).

Only instance admins should install this (`admin`, `marchon-gmail-com`,
`admin-verae-com`, `billing-bot` on ns1).

---

## Official example-apps (patterns B–F, D)

Code lives in `example-apps/<name>/assets/`. Manifests are the contract.

### Chosen-file editors (B)

`texteditor/assets/index.html` is the reference (50 lines):

```js
const filePath = new URL(/* frame href */).searchParams.get("path");
fetch(filePath, { method: "GET" }).then(/* fill textarea */);
fetch(filePath, { method: "PUT", body: encoder.encode(contents) });
```

Notes, Tldraw, Draw.io, Luckysheet, PaintZ, JS Paint, TUI editors do the
same: load the chosen file, keep editor state in memory, PUT back.
Luckysheet also sets `CSP_UNSAFE_EVAL` because the spreadsheet bundle
evaluates generated code.

### Folder players (C)

Audio player / slideshow: `GET` the folder listed in `path`, filter by
extension, `GET` each media file as a blob URL.

### Messaging (D)

Album sets `"template": "messaging"` so Peergos creates a shareable
instance and a chat. The app uses Chat API + `READ_CHOSEN_FOLDER` to
attach photos. Photroll is `messaging-instance` (one install).

### Converters and office (E, F)

`file2pdf` / `weboffice` host LibreOffice via ZetaJS (`soffice.wasm` ~
36–37 MiB). `pandoc` hosts `pandoc.wasm.br`. `vlc.js` hosts VLC WASM.
These are **vendor wraps**: do not rewrite the engine; write a thin
`index.html` that feeds Peergos bytes in and out.

`doc-viewer` is not launchable: Drive opens it for `.docx`/`.odt` via
`getRecommendedViewer`.

### Games / extras

Chess and TicTacToe are webxdc ports that speak Chat API for moves.
Doom/skymap/calculator are self-contained launchable HTML.

---

## Gallery (pattern H)

`verae-ops/modules/peergos-apps/gallery/index.html` is **not** installed
into `.apps/`. It *is* `/peergos/recommended-apps/index.html` (must be
>20 bytes). Install posts FormData to `/peergos-api/v0/install-app/`.

Publish path: `OrgTool put-catalog` as user `peergos`, then `make-public`
on each child. See [building-apps.md](building-apps.md) §6.

---

## What *not* to copy

| Trap | Why |
| --- | --- |
| Opening NATS from the iframe | CSP + no sockets; use outbox |
| `fetch("https://…")` | CSP blocks; only `/peergos-api` and relative assets |
| Publishing `.git` / Go / docs | `publish.sh` strips to `peergos-app.json` + `assets/` |
| `window.prompt` in org-admin style apps | Use in-app dialogs (org-admin already does) |
| Assuming `path` is writable | Check init `props.isPathWritable` or PUT 400 |
| Skipping `version` bumps | **Update** compares `Version.parse` on the published source |

---

## File map (where to read the code)

| App | Read first |
| --- | --- |
| hello-cube | `verae-app-sdk/hello-cube/assets/{index.html,sdk.js}` |
| itad / wine / signatures | `verae-app-*/assets/index.html` + same `sdk.js` |
| SDK modules | `verae-app-sdk/src/{peergos-data,outbox,share-wizard}.js` |
| org-admin | `org-admin/assets/index.html` (`adminCall`) |
| texteditor | `example-apps/texteditor/assets/index.html` |
| notes | `example-apps/notes/peergos-app.json` + `assets/index.html` |
| album | `example-apps/album/peergos-app.json` (`template: messaging`) |
| luckysheet | `example-apps/luckysheet/peergos-app.json` |
| gallery | `verae-ops/modules/peergos-apps/gallery/index.html` |
| sandbox | `web-ui/src/components/sandbox/AppSandbox.vue` |
| service worker | `web-ui/assets/apps/sandbox/sw-sandbox.js` |
| install-app handler | `AppSandbox.vue` `handleInstallAppRequest` |
