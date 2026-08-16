# Verae Peergos app handbook

Standalone documentation and Grok skill for **building, publishing, and
planning Peergos HTML5 apps** on the Verae DataCube stack.

This repo is the source of truth for that skillset. Sister code lives in
[Verae-Peergos](https://github.com/DataCube-Modules/Verae-Peergos),
[verae-app-sdk](https://github.com/DataCube-Modules/verae-app-sdk),
and [verae-ops](https://github.com/DataCube-Modules/verae-ops).

## Read in this order

| # | Doc | What it covers |
| --- | --- | --- |
| 1 | [docs/skillset.md](docs/skillset.md) | Ordered skillset for humans and agents |
| 2 | [docs/lectures-and-talks.md](docs/lectures-and-talks.md) | Official lectures and slides |
| 3 | [docs/building-apps.md](docs/building-apps.md) | Folder layout, `peergos-app.json`, sandbox, install, publish |
| 4 | [docs/sandbox-api.md](docs/sandbox-api.md) | Permissions and `/peergos-api/v0` / `v1` (and admin) |
| 5 | [docs/existing-apps-architecture.md](docs/existing-apps-architecture.md) | Code map of every current app (patterns A–I) |
| 6 | [docs/additional-apps-plan.md](docs/additional-apps-plan.md) | Decision tree, Verae backlog, acceptance checklist |
| 7 | [docs/third-party-projects.md](docs/third-party-projects.md) | Official example-apps, upstreams, Verae apps |
| 8 | [protocol/peergos-book-apps.md](protocol/peergos-book-apps.md) | Vendored Peergos book “Custom Apps” chapter (same as https://book.peergos.org/features/apps.html) |

Index copy: [docs/README.md](docs/README.md).

**Lectures first:** [Applications on Peergos](https://www.youtube.com/watch?v=3i1TtknNw2E),
[Applications deep dive](https://www.youtube.com/watch?v=oberD75GU8I),
[User-owned identity and data](https://www.youtube.com/watch?v=mSElk2jcFqY).
Architecture: IPFS Camp 2024, Devstaff, IPFS Thing, [slides](https://speakerdeck.com/ianopolous/peergos-architecture).

Calendar, PDF, social, and Drive are **built into** Peergos. They are not
`peergos-app.json` packages.

## Skills

| Path | Use |
| --- | --- |
| [.grok/skills/build-peergos-app/SKILL.md](.grok/skills/build-peergos-app/SKILL.md) | Grok project skill (`/build-peergos-app`) |
| [skills/build-peergos-app/SKILL.md](skills/build-peergos-app/SKILL.md) | Same file, for people browsing `skills/` |

Install into your Grok home so it loads in every workspace:

```bash
mkdir -p ~/.grok/skills/build-peergos-app
cp skills/build-peergos-app/SKILL.md ~/.grok/skills/build-peergos-app/SKILL.md
```

Then run `/build-peergos-app` or ask to create a Peergos / DataCube app.

## Gallery reference

- [docs/catalog.json](docs/catalog.json) — Verae + official app list
- [docs/gallery-index.html](docs/gallery-index.html) — live gallery source

## License

Documentation in this repo is for the Verae / DataCube-Modules org.
The protocol chapter is copied from the Peergos book (see that file’s
upstream: https://github.com/Peergos/book).
