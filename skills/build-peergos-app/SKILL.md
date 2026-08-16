---
name: build-peergos-app
description: >
  Build, change, or publish a Peergos HTML5 app (peergos-app.json sandbox,
  DataCube outbox, recommended-apps gallery). Use when the user asks to
  create a Peergos app, custom app, DataCube app, installable gallery app,
  Org Admin-style console, or runs /build-peergos-app.
---

# Build a Peergos app

Docs live in this handbook repo (`verae-peergos-app-handbook`). Read the
ones you need; do not invent APIs.

If this checkout is at `~/research/verae-peergos-app-handbook`:

- `docs/skillset.md`
- `docs/building-apps.md`
- `docs/sandbox-api.md`
- `docs/existing-apps-architecture.md`
- `docs/additional-apps-plan.md`
- `docs/lectures-and-talks.md`
- `docs/third-party-projects.md`
- `protocol/peergos-book-apps.md`

GitHub: https://github.com/DataCube-Modules/verae-peergos-app-handbook

## Rules

1. **Pick one pattern** (A–I) from `docs/existing-apps-architecture.md` and say it.
   Copy hello-cube (A) or texteditor (B) unless another pattern fits better.
2. **Minimum permissions.** Every `fetch` target must match a granted token.
3. **No NATS, no raw TCP, no `https://` fetches** from the iframe. Pattern A
   writes `/outbox/<job>.json` only. New `subject` values need a connector
   change first.
4. Publish tree is **`peergos-app.json` + `assets/`** only (`index.html` required).
5. Bump SemVer. Add a gallery card + `docs/catalog.json`. Publish with
   `OrgTool put-dir`/`put-catalog` + `make-public` as user `peergos`.
6. Calendar, PDF, social, Drive are built-in — do not reimplement.
7. After the app exists, add a short section to
   `docs/existing-apps-architecture.md` and push this handbook.

## Pattern A (Verae default)

Inlined `assets/sdk.js` (`VeraeSDK`): `createClient`, `cubePaths`,
`makeEnvelope`, `enqueue`. Data under `/cubes/<id>/`. Connector watches
`/.apps/<name>/data/outbox/`.

## Do not

- Grant `ADMIN_INSTANCE` except org-admin clones for instance operators.
- Ship `.git`, Go, or docs inside the Peergos folder.
- Skip `version` or gallery Install.
