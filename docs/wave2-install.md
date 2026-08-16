# Wave 2 installation guide

## Prerequisites

- Peergos account on https://peergos.georgelambert.org (or local daemon)
- Java 21 + `Peergos.jar` if using OrgTool
- Desktop-host connectors for outbox subjects (timestamp, append, export, verify)

## Install one app

From a clone of e.g. `verae-app-cube-browser`:

```bash
# Web: upload peergos-app.json + assets/, then Install App
# CLI:
java -cp Peergos.jar OrgTool install-app \
  https://peergos.georgelambert.org "$USER" "$PASS" cube-browser .
```

Or wait for gallery publish: Apps → Custom → Install.

## Install all seven

```bash
for r in cube-browser share-wizard timestamp-inbox iso-export itad-board sig-verify connector-status; do
  echo "== $r =="
  # OrgTool install-app ... $r ~/research/verae-app-$r
done
```

## Connector subjects to enable on the host

| Subject | App |
| --- | --- |
| `verae.ts.request` / receipts | timestamp-inbox (reads inbox) |
| `verae.cube.append` | itad-board |
| `verae.cube.export` | iso-export (new) |
| `verae.sig.verify` | sig-verify (new) |

`verae.cube.export` and `verae.sig.verify` were added to
`verae-nats-bus/schemas/subjects.json`. Host connectors must implement
them before those two apps do useful work beyond queueing files.

## Verify

```bash
cd ~/research/verae-app-cube-browser && make certify
```

Repeat per repo. Expected: `peergos compliance: PASS`.
