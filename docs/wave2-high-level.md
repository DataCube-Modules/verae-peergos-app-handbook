# Wave 2 Peergos apps — high-level description

Seven installable Peergos apps close the UI gaps after hello-cube, ITAD,
wine, and signatures. Each app is its own git repository. They store
state in the Peergos Cryptree via `/peergos-api/v0/data`. They never
open NATS. Connectors on the desktop host watch `outbox/` and publish
JetStream subjects registered in `verae-nats-bus`.

| App | Repo | Specialist | What the user sees |
| --- | --- | --- | --- |
| Cube Browser | verae-app-cube-browser | JS + integrity | List cubes and dual hashes |
| Share Wizard | verae-app-share-wizard | Frontend + integrity | Modes A/B/C → `share-plan.json` |
| TS Inbox | verae-app-timestamp-inbox | Timestamp + JS | Local/Shared/Global receipts |
| ISO Export | verae-app-iso-export | Storage + wine UI | Queue `verae.cube.export` |
| ITAD Board | verae-app-itad-board | ITAD SME + JS | pickup→wipe→sale appends |
| Sig Verify | verae-app-sig-verify | Crypto + JS | valid/revoked + `verae.sig.verify` |
| Conn Status | verae-app-connector-status | Messaging + host | outbox pending vs inbox acked |

Plan: [PLAN-APPS-WAVE2.md](https://github.com/DataCube-Modules/Verae-DataCube-Solution-Pieces/blob/main/PLAN-APPS-WAVE2.md)
in Solution-Pieces (also copied conceptually here).

Peergos-compliant means: valid `peergos-app.json`, `assets/index.html`,
no WebSocket/NATS in the iframe, `fetch` only to `/peergos-api` or
relative files, unit tests green. Certified with `make certify` on
2026-08-16.
