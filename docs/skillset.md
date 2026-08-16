# Skillset: building more Peergos apps

What you need to know, in order, to add a custom app without breaking
the sandbox or the DataCube rules.

## 1. Isolation model (lectures)

Watch, in this order:

1. [Applications on Peergos](https://www.youtube.com/watch?v=3i1TtknNw2E)
2. [Applications deep dive](https://www.youtube.com/watch?v=oberD75GU8I)
3. [User-owned identity and data](https://www.youtube.com/watch?v=mSElk2jcFqY)

Then architecture as needed: [IPFS Camp 2024](https://www.youtube.com/watch?v=yDU4GHsEo34),
[Devstaff](https://www.youtube.com/watch?v=Po_fdZYcfXo),
[IPFS Thing](https://www.youtube.com/watch?v=g1vzoZjG9Zo),
[slides](https://speakerdeck.com/ianopolous/peergos-architecture).
Full list: [lectures-and-talks.md](lectures-and-talks.md).

Takeaway: the app is a hostile iframe. The server must not see plaintext
app I/O. You get a capability the user granted, nothing else.

## 2. Contract

- Folder + `peergos-app.json` + `assets/index.html`
  ([building-apps.md](building-apps.md))
- Permissions and REST
  ([sandbox-api.md](sandbox-api.md),
  [book apps chapter](../protocol/peergos-book-apps.md))
- Install copies to `/.apps/<name>/`; Update compares `version`
- Gallery is `/peergos/recommended-apps/` (index.html > 20 bytes)

## 3. Patterns already in this org

Read [existing-apps-architecture.md](existing-apps-architecture.md) until
you can name the pattern for hello-cube, texteditor, album, org-admin,
and luckysheet without looking.

Verae-specific: **no NATS in the iframe**. Outbox JSON only
(`verae-app-sdk`).

## 4. Third-party wraps

[third-party-projects.md](third-party-projects.md) lists every official
wrapper and its upstream. Prefer wrapping an existing MIT/Apache UI over
rewriting one.

## 5. Plan the next app

[additional-apps-plan.md](additional-apps-plan.md) — decision tree,
Verae backlog, publish checklist, connector contract.

## 6. Hands-on minimum

Build a throwaway launchable that writes one JSON file with
`STORE_APP_DATA`, install it, then add an outbox job. If that works,
you can copy hello-cube into a real domain app.

## 7. Agent command

`/build-peergos-app` — Grok skill that enforces this skillset when
asked to create or change a Peergos app.
