# Wave 2 developer reference

Each repo follows the same layout:

```
peergos-app.json
assets/index.html     # sandbox UI
assets/sdk.js         # browser VeraeSDK
src/peergos-sdk.mjs   # ESM for tests
src/lib.mjs           # specified functions
tests/lib.test.mjs
tests/certify-peergos.sh
docs/SPECS.md         # function I/O + behavior
docs/INSTALL.md
docs/DEVELOPER.md
```

## Function index

| Repo | Functions |
| --- | --- |
| cube-browser | `listCubes`, `listCubeObjects`, `extractHashes` |
| share-wizard | `buildSharePlan`, `writeSharePlan`, `planIncludes` |
| timestamp-inbox | `listInbox`, `parseReceipt`, `scopeRank` |
| iso-export | `enqueueExport`, `parseExportAck` |
| itad-board | `STAGES`, `nextStage`, `columnize`, `enqueueStage` |
| sig-verify | `listValid`, `listRevoked`, `isRevoked`, `enqueueVerify` |
| connector-status | `listOutbox`, `listInbox`, `jobStem`, `classifyJobs` |

See each `docs/SPECS.md` for inputs, outputs, and internal behavior.

## Shared client

`createClient(fetch)`:

- `writeJSON(path, obj)` → PUT `/peergos-api/v0/data`+path
- `readJSON(path)` → GET JSON
- `list(path)` → `{files, subFolders}` (Peergos folder GET)

`makeEnvelope(subject, payload, reply_file?)`  
`enqueue(client, name, envelope)` → `/outbox/<name>.json`

## Compliance

`make certify` fails if assets contain `nats.connect`, `WebSocket`,
`wss://`, or absolute `http(s)` `fetch`. Manifest displayName ≤ 25,
description ≤ 100, schemaVersion 1, launchable true.
