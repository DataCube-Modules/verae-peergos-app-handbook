# Building Peergos apps

This folder is the handbook body. The repo root
[README](../README.md) is the landing page.

Complete set for **designing, implementing, installing, and publishing**
Peergos HTML5 apps, plus the architecture of every app we already ship
and a plan for the next ones.

Read in this order if you are new:

1. [skillset.md](skillset.md) — what to learn
2. [lectures-and-talks.md](lectures-and-talks.md) — Applications on Peergos, deep dive, identity
3. [building-apps.md](building-apps.md) — tutorial
4. [existing-apps-architecture.md](existing-apps-architecture.md) — how current apps work
5. [additional-apps-plan.md](additional-apps-plan.md) — what to build next

| Document | What it covers |
| --- | --- |
| [skillset.md](skillset.md) | Ordered skillset for humans and agents |
| [building-apps.md](building-apps.md) | Folder layout, `peergos-app.json`, sandbox, install, publish |
| [sandbox-api.md](sandbox-api.md) | Permissions and `/peergos-api/v0` / `v1` (and admin) |
| [existing-apps-architecture.md](existing-apps-architecture.md) | Code map of Verae + official apps (patterns A–I) |
| [additional-apps-plan.md](additional-apps-plan.md) | Decision tree, Verae backlog, acceptance checklist |
| [lectures-and-talks.md](lectures-and-talks.md) | Official lectures and slides |
| [third-party-projects.md](third-party-projects.md) | Official example-apps, upstreams, Verae apps |

Canonical protocol chapter (same text as https://book.peergos.org/features/apps.html):

- [protocol/peergos-book-apps.md](../protocol/peergos-book-apps.md)

Agent skill: `.grok/skills/build-peergos-app/SKILL.md` (`/build-peergos-app`).

Live gallery: https://peergos.georgelambert.org → **Apps** → **Custom**.

Publish: `verae-ops/modules/peergos-apps/` and `deploy/tools/OrgTool.java`.

Calendar, PDF, social, and Drive are **built into** the Peergos UI. They
are not `peergos-app.json` packages.
