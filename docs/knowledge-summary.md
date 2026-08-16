# Accumulated knowledge (review)

**Purpose:** One file you can read end-to-end. It is the digest of the
long Verae / Peergos / DataCube / ops session (through 2026-08-16).

**Not in this file:** passwords, bootstrap tokens, or private keys. Those
stay on ns1 in `0600` secret files.

**Companion:** [session-dialog-2026-08.md](session-dialog-2026-08.md) is
the turn-by-turn dialog archive.

**Handbook home:** [../README.md](../README.md)

---

## 1. What we are building

Verae runs **hosted Peergos desktops** plus **DataCube applications**.
Peergos is the encrypted filesystem and app sandbox. DataCubes are an
append-only cube (directory tree + SQLite), not Postgres. Iceberg here
is a **CID catalog**, not the cube format.

Skip (explicit): LiquidAI, llamafile, mangos, K9, llama.c++,
datacube-ai-proxy.

Source of truth for Peergos patches: **peergos-resources** merged as
`Verae-Peergos`.

## 2. Repos (GitHub org `DataCube-Modules`)

| Repo | Role |
| --- | --- |
| `Verae-DataCube-Solution-Pieces` | Plan / pieces index |
| `verae-repo-template` | New product repo template |
| `verae-nats-bus` | JetStream subjects `verae.<domain>.<resource>.<action>` |
| `verae-datacube-core` | Cube core (append-only, dual SHA-256+BLAKE3) |
| `verae-timestamp` | Local / Shared / Global; Global via `api.veraetime.net` |
| `Verae-Peergos` | Hosted Peergos + OrgTool + org-admin + example-apps |
| `verae-app-sdk` | hello-cube + `peergos-data` / `outbox` / `share-wizard` |
| `verae-app-itad` / `wine` / `signatures` | Domain apps |
| `verae-ipfs-iceberg` | CID catalog + pin/hydrate |
| `verae-desktop-host` | Desktop host; connectors watch `.apps/*/outbox` |
| `verae-deploy` / `verae-ops` | Inspect-first deploy, Prometheus, Caddy, SSO |
| **`verae-peergos-app-handbook`** | **This repo** — app-building docs + skill |

SSH to GitHub uses `~/.ssh/id_ed25519_grok_macbook` (comment
`Grok-Macbook-ssh-key`), `IdentitiesOnly` on `github.com`.

Creating **new org repos** needs a credential with org admin; `gh` is
often logged out. SSH push works once the empty repo exists.

## 3. Live edge

| Host | IP | Role |
| --- | --- | --- |
| ns1 | `70.88.205.138` (`marchon@`, passwordless sudo) | Primary: Caddy, Docker, Peergos CT 501–504, Prometheus, Authentik, Grafana |
| ns2 | `70.88.205.137` | DNS secondary + fail2ban + blackbox; Caddy HTTP `/healthz` only (no ACME) |

Peergos CTs: **501 PKI**, **502 peergos-a** (`10.10.10.12:8000`,
`peergos.georgelambert.org`), **503 peergos-b** (secret links),
**504 MinIO**.

Do **not** put TSDB on storage4 when it is ~92% full. Do **not** restart
PKI (501) without a second operator.

HTTPS SSH tunnel: `ssh.georgelambert.org` via wstunnel v10.6.2,
restrict-to `127.0.0.1:22`, path prefix `verae-ssh`.

## 4. Ops / SLO

- Target: **99.9%** (~43.2 min error budget / 30 days).
- Prometheus + Alertmanager; Grafana **11.5.2** on `127.0.0.1:3001`,
  auth proxy `X-Authentik-Username`.
- Consoles: `https://ops.georgelambert.org` (switcher) plus
  auth / prometheus / alerts / probe / grafana / ui hostnames → ns1.
- Backends bind **localhost**; nft `inet verae_sso` drops WAN to those
  ports.
- Authentik **2025.8.4** domain forward-auth + embedded outpost.
  Admin user `akadmin`. Bootstrap password is in
  `/opt/verae-ops/sso/.env` on ns1 — do not copy it into git.
- Google OAuth still needs `GOOGLE_CLIENT_ID` / `SECRET`.
- ErrorBudgetBurnFast/Slow must join `up` and require enough
  `count_over_time(up[1d])` or young/stale series false-fire.
- file_sd downs: do not scrape public IPs for 9090/9093/8099 after
  localhost bind.
- NATS metrics: exporter `:7777` (NATS `/metrics` is 404).
- Iceberg health: `/healthz` and empty `/v1/` JSON ok.

## 5. Peergos identity and empty Apps

- PKI user **`peergos`** owns `/peergos/recommended-apps/`.
  Password is CT 501 `PEERGOS_PASSWORD` (`peergos.password`). Must
  differ from `pki.keygen.password`.
- Web **admin-usernames** on 502:
  `admin`, `marchon-gmail-com`, `admin-verae-com`, `billing-bot`.
  Those web passwords were **not** recovered.
- `pki-init` writes `recommended-apps/index.html` as `<html></html>`
  (**13 bytes**). The launcher only opens the gallery if that file is
  **> 20 bytes**. Combined with empty `/.apps/`, Apps looked empty.
- Gallery is now a real `index.html` (~9.7 KB) plus app folders, all
  `make-public`.
- Install: Apps → **Custom** → Install. Copies to
  `/<user>/.apps/<name>/`.
- Update compares SemVer on published `peergos-app.json`.

## 6. Publishing apps

`OrgTool` (`Verae-Peergos/deploy/tools/OrgTool.java`):
`put`, `put-dir`, `put-catalog`, `make-public`, `install-app`, `ls`.

- `make-public` on an already-public path can throw **Noop pointer
  update** or **CAS** — treat as success.
- Large WASM (`pandoc`, `vlc.js`, `file2pdf`, `weboffice`) **times out
  through Caddy**. Upload via a Host-rewriting proxy
  `127.0.0.1:18000` → `10.10.10.12:8000` with
  `Host: peergos.georgelambert.org`. Direct `:8000` without that Host
  is 404 (`public-domain`).
- `publish.sh` stages only `peergos-app.json` + `assets/`.
- Skip gallery: `file-picker`, `folder-picker`, `gwt-vue-min`.

**Live recommended-apps:** Verae (hello-cube, itad, wine, signatures,
org-admin) + official example-apps set including the four WASM apps.

## 7. How Peergos apps actually work

- App origin is `sha256(path).$public-domain`, separate process, CSP.
- Service worker turns `fetch` into `postMessage`; main tab enforces
  permissions. FormData POSTs become JSON (`formToJSON`).
- Default permissions: **none** (own assets only).
- Until WebRTC CSP exists, only install apps you trust.
- Apps **cannot** open NATS. Pattern A writes
  `/outbox/<job>.json`; desktop-host connector publishes JetStream.

### Patterns (copy one)

| | Pattern | Copy |
| --- | --- | --- |
| A | DataCube + outbox | `hello-cube` |
| B | Chosen-file editor | `texteditor` (`fetch(?path=)` GET/PUT) |
| C | Folder action | audio-player / slideshow |
| D | Messaging template | album (`template: messaging`) |
| E/F | Converter / vendor wrap | file2pdf, weboffice, luckysheet |
| G | Instance admin | org-admin → `POST /peergos-api/v0/admin/<route>` |
| H | Gallery | `recommended-apps/index.html` + install-app |
| I | API demo | chat-api (not product) |

Built-in, do not reimplement: Calendar, PDF, social, Drive.

Drive recommended viewers (once public in recommended-apps):
`.docx`/`.odt` → doc-viewer; `.sheet`/`.xlsx`/`.ods` → luckysheet;
`.tldr` → tldraw; `.drawio` → drawio; `.epub` → ebookreader.

### Verae SDK (inlined `assets/sdk.js`)

`createClient` → `/peergos-api/v0/data`; `cubePaths`; `makeEnvelope`;
`enqueue` → `/outbox/<name>.json`; share modes **A** proofs / **B** +
metadata / **C** + files.

Cube layout: `data/cubes/<id>/manifest.json` + domain files;
`outbox/`; `inbox/` (connector replies). Signatures use
`data/signatures/{valid,revoked}/`.

org-admin routes: `users`, `user-details`, `set-quota`,
`delete-mfa-credential`, `delete-user`, `create-tokens`,
`space-requests`, `approve-space-request`, `audit-log`.

### Permissions (minimum)

`STORE_APP_DATA`, `EDIT_CHOSEN_FILE`, `READ_CHOSEN_FOLDER`,
`EXCHANGE_MESSAGES_WITH_FRIENDS`, `USE_MAILBOX`,
`ACCESS_PROFILE_PHOTO`, `CSP_UNSAFE_EVAL`, `ADMIN_INSTANCE`
(operators only).

## 8. Next apps (backlog)

1. Cube browser (read a `.cube` folder)
2. Share wizard UI (A/B/C)
3. Timestamp inbox (read connector replies)
4. Receipts / ISO packager trigger (enqueue export)
5. ITAD pipeline board
6. Signature verify UI
7. Connector status (outbox vs inbox)

New Pattern A `subject` values need a **connector change first**.

## 9. Lectures (watch first)

1. https://www.youtube.com/watch?v=3i1TtknNw2E — Applications on Peergos
2. https://www.youtube.com/watch?v=oberD75GU8I — Applications deep dive
3. https://www.youtube.com/watch?v=mSElk2jcFqY — User-owned identity

More: [lectures-and-talks.md](lectures-and-talks.md).
Book: [protocol/peergos-book-apps.md](../protocol/peergos-book-apps.md).

## 10. Skill

`/build-peergos-app` — this repo
`.grok/skills/build-peergos-app/SKILL.md` and
`skills/build-peergos-app/SKILL.md`. Also copied to `~/.grok/skills/`.

## 11. Still open

- Google OAuth client id/secret
- Peergos **web** admin passwords (usernames only)
- 30-day SLO needs calendar time
- Older leftover datacubes-* containers
- ns2 Caddy is health-only (no ACME)
- Pre-install into `admin` / `marchon-gmail-com` needs those logins
