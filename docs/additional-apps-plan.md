# Plan: additional Peergos apps

How to decide what to build next, which pattern to copy, and when an app
is done. Architecture of current apps:
[existing-apps-architecture.md](existing-apps-architecture.md).

## Decision tree

```
Need to talk to NATS / timestamps / Iceberg?
  yes → Pattern A (DataCube + outbox). Never fetch those services.
Need to edit a user-picked file in Drive?
  yes → Pattern B (chosen-file). Ask EDIT_CHOSEN_FILE.
Need to play/list a folder?
  yes → Pattern C. Ask READ_CHOSEN_FOLDER.
Need shared membership / chat?
  yes → Pattern D. template: messaging (+ messaging-instance if only one).
Need convert-and-download?
  yes → Pattern E. Prefer save-picker over silent writes.
Wrapping an existing JS/WASM project?
  yes → Pattern F. Thin host only; keep upstream license in description.
Instance operators only?
  yes → Pattern G. ADMIN_INSTANCE. Do not recommend to all users.
```

If two answers are yes, **split into two apps** or one app with two
entry points (launchable + file association). Do not grant every
permission “just in case”.

## Verae backlog (recommended order)

These fill gaps the current cubes leave in the UI. **Wave 2 (2026-08-16)
built all seven** as independent repos; each `make certify` passed.

| # | App | Pattern | Why |
| --- | --- | --- | --- |
| 1 | **Cube browser** | A + C | Open a `.cube` folder, list objects, show dual hashes, no NATS. hello-cube is write-only. |
| 2 | **Share wizard** | A | UI for modes A/B/C using `validateShare`; write a share plan into the cube. Logic already in `share-wizard.js`. |
| 3 | **Timestamp inbox** | A | Read `data/inbox/*.json` replies from the connector; show Local/Shared/Global. |
| 4 | **Receipts / ISO packager trigger** | A | Enqueue `verae.cube.export` so the host runs xorriso; wine already documents this as host-side. |
| 5 | **ITAD pipeline board** | A | Kanban over pickup/wipe/sale events (extend itad; still outbox for append). |
| 6 | **Signature verify** | A | Read `signatures/valid` + `revoked`; enqueue verify job; show pass/fail from inbox. |
| 7 | **Connector status** | A | List outbox (pending) vs inbox (acked). Ops-facing. |

Do **not** rebuild Calendar, PDF, or social. Those are built-in.

Do **not** wrap another office suite until file2pdf/weboffice have been
used in production; they already cover ZetaJS/LibreOffice.

## Build sequence for any new app

1. **Name** the folder (`[a-z0-9-]+`) — this is `appName` in the gallery.
2. **Pick one pattern** from the tree. Write it in the PR/commit.
3. **Manifest first.** `peergos-app.json` with the *minimum* permissions.
4. **Scaffold** from hello-cube (A) or texteditor (B). Keep `assets/index.html`
   as the only entry.
5. **No network except `/peergos-api` and relative assets.**
6. **Outbox subjects** if Pattern A — reuse existing:
   `verae.ts.request`, `verae.cube.append`, or add one subject and teach
   the connector before shipping the app.
7. **Run App** from Drive on the manifest (set `launchable: true`).
8. **Install App** into a test user. Confirm `/.apps/<name>/`.
9. **Bump `version`.** Add a card to
   `verae-ops/modules/peergos-apps/catalog.json` and `gallery/index.html`.
10. **`publish.sh`** (or `OrgTool put-dir` + `make-public`).
11. **Update** [third-party-projects.md](third-party-projects.md) and
    [existing-apps-architecture.md](existing-apps-architecture.md).

## Acceptance checklist

- [ ] `assets/index.html` exists; no `.git` in the published tree
- [ ] Manifest `version` is SemVer; `description` ≤ 100 chars
- [ ] Permissions match actual `fetch` targets
- [ ] Works with `theme=dark-mode`
- [ ] Chosen-file apps handle missing/unwritable `path`
- [ ] DataCube apps never import NATS; outbox JSON is the only side effect
- [ ] Gallery Install opens the permission wizard
- [ ] **Update** in Apps sees the new version after publish

## Connector contract (Pattern A)

```json
{ "subject": "verae.ts.request",
  "payload": { "hash": "sha256:…", "cube_id": "…", "scope": "local" },
  "reply_file": "optional-name.reply.json" }
```

Write to `/outbox/<job>.json`. The host connector must understand
`subject` before you ship. New subjects need a connector change **first**.

## Skill

Agents building apps for Verae should load `/build-peergos-app`
(see `.grok/skills/build-peergos-app/SKILL.md`). Humans follow this file
and [building-apps.md](building-apps.md).
