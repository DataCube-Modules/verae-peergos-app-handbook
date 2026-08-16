# Wave 2 Peergos apps — plan

### Comments:

Independent installable Peergos apps that close UI gaps after hello-cube /
ITAD / wine / signatures. Each app is its **own git repo**. Apps never
open NATS; they write Peergos files. Connectors on `verae-desktop-host`
watch `/.apps/<name>/data/outbox/` and publish JetStream.

## Integration (Peergos + files + NATS)

```
Sandbox app
  → PUT/GET /peergos-api/v0/data/...     (Cryptree files)
  → PUT /outbox/<job>.json               {subject, payload, reply_file?}
Connector (host, not sandbox)
  → NATS JetStream verae.*
  → PUT /inbox/<reply>.json
App polls or lists /inbox/               (still no NATS)
```

| Subject | Who writes outbox | Payload | Inbox reply |
| --- | --- | --- | --- |
| `verae.ts.request` | timestamp-inbox (re-stamp), others already | hash, cube_id, scope | receipt JSON |
| `verae.cube.append` | itad-board | block | optional ack |
| `verae.cube.export` | iso-export | cube_id, format=iso, share_mode | export path / error |
| `verae.sig.verify` | sig-verify | object_sha256, signature_id | {ok, reason} |

File roots (all under `/.apps/<app>/data/`):

- `/cubes/<id>/manifest.json` + objects
- `/outbox/*.json` pending jobs
- `/inbox/*.json` connector replies
- `/signatures/valid|revoked/*.json`

## Repos, specialists, functions

| Repo | Specialist | Pattern | Functions |
| --- | --- | --- | --- |
| `verae-app-cube-browser` | JS + integrity | A+C | `listCubes`, `listCubeObjects`, `extractHashes` |
| `verae-app-share-wizard` | Frontend + integrity | A | `validateShare`, `buildSharePlan`, `writeSharePlan` |
| `verae-app-timestamp-inbox` | Timestamp + JS | A | `listInbox`, `parseReceipt`, `scopeRank` |
| `verae-app-iso-export` | Storage + wine frontend | A | `enqueueExport`, `parseExportAck` |
| `verae-app-itad-board` | ITAD SME + JS | A | `STAGES`, `columnize`, `enqueueStage` |
| `verae-app-sig-verify` | Crypto + JS | A | `listValid`, `listRevoked`, `isRevoked`, `enqueueVerify` |
| `verae-app-connector-status` | Messaging + host | A | `listOutbox`, `classifyJobs` |

## Peergos compliance (certify)

1. `peergos-app.json`: schemaVersion 1, displayName ≤25, description ≤100, SemVer, launchable, minimum permissions.
2. Published tree = `peergos-app.json` + `assets/` (`index.html` required).
3. Assets never mention `nats.connect`, `ws://`, `wss://`, or absolute `https://` fetches (except comments).
4. All `fetch` targets start with `/peergos-api/` or are relative.
5. Unit tests pass (`make test`).
6. Outbox envelopes use registered subjects only.

## Build / test / docs

Each repo: `src/*.mjs` (specified functions) → `tests/*.test.mjs` →
`assets/` UI → `docs/{SPECS,INSTALL,DEVELOPER}.md` → `make test` +
`make certify`.

Handbook PDFs: `docs/published/` in this wave’s handbook or
`verae-peergos-app-handbook/docs/published/`.
