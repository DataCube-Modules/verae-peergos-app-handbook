# Lectures, talks, and slides

Official media list (kept in sync with
https://github.com/Peergos/Peergos#media). Watch these before writing an
app; the two **Applications** talks are the lectures that match
[building-apps.md](building-apps.md).

## Applications (start here)

| Talk | Where | URL |
| --- | --- | --- |
| Applications on Peergos | YouTube | https://www.youtube.com/watch?v=3i1TtknNw2E |
| A better web: secure, private p2p apps with user-owned data and identity | YouTube | https://www.youtube.com/watch?v=mSElk2jcFqY |
| Applications deep dive | YouTube | https://www.youtube.com/watch?v=oberD75GU8I |

These cover the sandbox (unique hostname + CSP + service worker),
permissions, `peergos-app.json`, and why the server never sees app assets
in the clear.

## Architecture and protocol

| Talk | Where | URL |
| --- | --- | --- |
| Architecture slides | Speaker Deck | https://speakerdeck.com/ianopolous/peergos-architecture |
| Deep dive — IPFS Camp 2024 | YouTube | https://www.youtube.com/watch?v=yDU4GHsEo34 |
| Deep dive — Devstaff Crete | YouTube | https://www.youtube.com/watch?v=Po_fdZYcfXo |
| Overview — IPFS Thing | YouTube | https://www.youtube.com/watch?v=g1vzoZjG9Zo |
| Architecture details | YouTube | https://www.youtube.com/watch?v=HVyrVUI2-RA |
| Architecture — IPFS Lab Day | YouTube | https://www.youtube.com/watch?v=h54pShffxvI |
| Introduction and 2020 update | YouTube | https://www.youtube.com/watch?v=oXMqYDLKWPc |
| Introduction | YouTube | https://www.youtube.com/watch?v=dCLboQDlzds |
| Short intro used in example-apps | YouTube | https://www.youtube.com/watch?v=REc8QfKxTik |

## Written references

| Resource | URL or path |
| --- | --- |
| Tech book (Custom Apps chapter) | https://book.peergos.org/features/apps.html |
| This repo’s copy of the book | [protocol/peergos-book-apps.md](../protocol/peergos-book-apps.md) |
| File viewers (built-in vs recommended) | [book/src/features/viewers.md](../../book/src/features/viewers.md) |
| Private websites (related, not sandbox apps) | [book/src/features/private-web.md](../../book/src/features/private-web.md) |
| Cryptree paper (Wuala) | `papers/wuala-cryptree.pdf` |
| Security audit 2024 | https://peergos.org/posts/security-audit-2024 |
| Security audit 2019 | https://peergos.org/posts/security-audit |
| Audit PDFs | `Peergos/audits/` |
| Matrix chat | https://matrix.to/#/#peergos-chat:matrix.org |

## How Verae uses these talks

1. Sandbox isolation → apps never open NATS; they write an **outbox**
   (`verae-app-sdk`).
2. Recommended-apps gallery → `verae-ops/modules/peergos-apps/`.
3. `ADMIN_INSTANCE` is an extra permission used by `org-admin/`, not in
   the 2022 talks.
