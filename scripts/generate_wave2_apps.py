#!/usr/bin/env python3
"""Generate Wave-2 Peergos app repos under ~/research/."""
from __future__ import annotations

import json
import os
from pathlib import Path

RESEARCH = Path(os.environ.get("RESEARCH", Path.home() / "research"))

SDK_MJS = r'''// Peergos data + outbox helpers. Tests inject fetchImpl.
export const DATA_BASE = "/peergos-api/v0/data";

export function createClient(fetchImpl, base = DATA_BASE) {
  const f = fetchImpl || globalThis.fetch.bind(globalThis);

  async function req(path, opts = {}) {
    const res = await f(base + path, opts);
    return res;
  }

  return {
    async writeJSON(path, obj) {
      const res = await req(path, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(obj),
      });
      if (!res.ok) throw new Error("PUT " + path + " " + res.status);
      return res;
    },
    async readJSON(path) {
      const res = await req(path);
      if (!res.ok) throw new Error("GET " + path + " " + res.status);
      return res.json();
    },
    async list(path) {
      const p = path.endsWith("/") ? path : path + "/";
      const res = await req(p);
      if (!res.ok) throw new Error("LIST " + p + " " + res.status);
      const body = await res.json();
      return {
        files: Array.isArray(body.files) ? body.files : [],
        subFolders: Array.isArray(body.subFolders) ? body.subFolders : [],
      };
    },
  };
}

export function cubePaths(cubeId) {
  const root = "/cubes/" + encodeURIComponent(cubeId);
  return { root, manifest: root + "/manifest.json" };
}

export function makeEnvelope(subject, payload, replyFile) {
  if (!subject) throw new Error("subject required");
  if (!payload || typeof payload !== "object") throw new Error("payload object required");
  return { subject, payload, reply_file: replyFile || undefined };
}

export async function enqueue(client, name, envelope) {
  const file = "/outbox/" + name + ".json";
  await client.writeJSON(file, envelope);
  return file;
}

export const SHARE_MODES = [
  { id: "A", title: "Proofs only", detail: "Blockchain + receipts. No metadata or files." },
  { id: "B", title: "Proofs + metadata", detail: "Adds selected object metadata." },
  { id: "C", title: "Proofs + metadata + files", detail: "Adds selected attachments." },
];

export function validateShare(mode, selectedHashes) {
  if (["A", "B", "C"].indexOf(mode) < 0) throw new Error("mode must be A, B, or C");
  if (!selectedHashes || !selectedHashes.length) throw new Error("select at least one object");
  return { mode, selected: selectedHashes.slice(), receipts_preserved: true };
}

export function createMemoryFetch() {
  const store = new Map();
  const fetchImpl = async (url, opts = {}) => {
    const path = url.replace(DATA_BASE, "") || "/";
    const method = (opts.method || "GET").toUpperCase();
    if (method === "PUT") {
      store.set(path, opts.body);
      return { ok: true, status: 200, json: async () => ({}) };
    }
    if (method === "GET") {
      if (store.has(path)) {
        const body = store.get(path);
        return { ok: true, status: 200, json: async () => JSON.parse(body) };
      }
      if (path.endsWith("/")) {
        const prefix = path === "/" ? "/" : path;
        const files = [];
        const sub = new Set();
        for (const key of store.keys()) {
          if (!key.startsWith(prefix)) continue;
          const rest = key.slice(prefix.length);
          if (!rest) continue;
          const parts = rest.split("/").filter(Boolean);
          if (parts.length === 1) files.push(parts[0]);
          else if (parts.length > 1) sub.add(parts[0]);
        }
        return {
          ok: true,
          status: 200,
          json: async () => ({ files, subFolders: [...sub] }),
        };
      }
      return { ok: false, status: 404, json: async () => ({}) };
    }
    return { ok: false, status: 400, json: async () => ({}) };
  };
  fetchImpl.store = store;
  return fetchImpl;
}
'''

SDK_BROWSER = r'''window.VeraeSDK = (function () {
  const DATA_BASE = "/peergos-api/v0/data";
  function createClient(fetchImpl, base) {
    const f = fetchImpl || fetch.bind(globalThis);
    base = base || DATA_BASE;
    async function req(path, opts) {
      return f(base + path, opts || {});
    }
    return {
      async writeJSON(path, obj) {
        const res = await req(path, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(obj),
        });
        if (!res.ok) throw new Error("PUT " + path + " " + res.status);
      },
      async readJSON(path) {
        const res = await req(path);
        if (!res.ok) throw new Error("GET " + path + " " + res.status);
        return res.json();
      },
      async list(path) {
        const p = path.endsWith("/") ? path : path + "/";
        const res = await req(p);
        if (!res.ok) throw new Error("LIST " + p + " " + res.status);
        const body = await res.json();
        return { files: body.files || [], subFolders: body.subFolders || [] };
      },
    };
  }
  function cubePaths(cubeId) {
    const root = "/cubes/" + encodeURIComponent(cubeId);
    return { root, manifest: root + "/manifest.json" };
  }
  function makeEnvelope(subject, payload, replyFile) {
    return { subject, payload, reply_file: replyFile };
  }
  function enqueue(client, name, envelope) {
    return client.writeJSON("/outbox/" + name + ".json", envelope);
  }
  const SHARE_MODES = [
    { id: "A", title: "Proofs only", detail: "Blockchain + receipts. No metadata or files." },
    { id: "B", title: "Proofs + metadata", detail: "Adds selected object metadata." },
    { id: "C", title: "Proofs + metadata + files", detail: "Adds selected attachments." },
  ];
  function validateShare(mode, selectedHashes) {
    if (["A", "B", "C"].indexOf(mode) < 0) throw new Error("mode must be A, B, or C");
    if (!selectedHashes || !selectedHashes.length) throw new Error("select at least one object");
    return { mode, selected: selectedHashes.slice(), receipts_preserved: true };
  }
  return { createClient, cubePaths, makeEnvelope, enqueue, SHARE_MODES, validateShare };
})();
'''

CSS = """
:root { --bg:#0a0a0f; --fg:#e0e0e0; --accent:#00d4aa; --muted:#9090a0; --card:#1a1a25; --bd:#2a2a3a; }
body.dark-mode, body { font-family: system-ui, sans-serif; background:var(--bg); color:var(--fg); margin:0; padding:1.5rem; }
h1 { color:var(--accent); font-size:1.25rem; }
button, select { background:var(--card); color:var(--fg); border:1px solid var(--bd); padding:.5rem .8rem; margin:.25rem .25rem 0 0; }
#log { white-space:pre-wrap; font:12px ui-monospace,monospace; color:var(--muted); margin-top:1rem; }
.card { border:1px solid var(--bd); padding:.75rem; margin:.4rem 0; border-radius:8px; }
.row { display:flex; flex-wrap:wrap; gap:.5rem; }
"""


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content if content.endswith("\n") else content + "\n")


def common_files(root: Path, name: str, display: str, specialist: str, subject_notes: str) -> None:
    write(root / "AGENTS.md", f"""# AGENTS — {name}

- Follow `~/research/Verae-DataCube-Solution-Pieces/PLAN.md` and `PLAN-APPS-WAVE2.md`.
- Do not import skipped research trees.
- Cube store is append-only SQLite + directory tree.
- Peergos apps never open NATS; connectors do.
- Specialist: {specialist}.
- Update HISTORY.md on every meaningful change.
""")
    write(root / "HISTORY.md", f"""# History

## 2026-08-16

- Wave 2 scaffold: Peergos app, function specs, unit tests, compliance cert.
""")
    write(root / "DEPENDENCIES.md", """# Dependencies

Runtime in the sandbox: none (vanilla HTML/JS).

Host connector (not this repo): `verae-nats-bus`, `verae-desktop-host`.

Dev: Node.js (tests).
""")
    write(root / "Makefile", """# Wave 2 Peergos app
.PHONY: test certify
test:
\tnode tests/lib.test.mjs
\t@test -f assets/sdk.js
\t@test -f assets/index.html
\t@test -f peergos-app.json
certify: test
\tbash tests/certify-peergos.sh
""")
    write(root / "tests/test_scaffold.sh", "#!/usr/bin/env bash\nset -euo pipefail\ntest -f README.md\necho ok\n")
    write(root / "prompts/buildout.md", "Implement SPECS.md. Apps never open NATS.\n")
    write(root / "prompts/change.md", "Update HISTORY.md and docs in the same change as code.\n")
    write(root / "src/peergos-sdk.mjs", SDK_MJS)
    write(root / "assets/sdk.js", SDK_BROWSER)
    write(
        root / "tests/certify-peergos.sh",
        r"""#!/usr/bin/env bash
set -euo pipefail
python3 - << 'PY'
import json, pathlib, re, sys
root = pathlib.Path(".")
man = json.loads((root/"peergos-app.json").read_text())
assert man.get("schemaVersion") == 1, "schemaVersion"
assert len(man.get("displayName","")) <= 25, "displayName"
assert len(man.get("description","")) <= 100, "description"
assert man.get("launchable") is True
assert (root/"assets/index.html").is_file()
text = ""
for p in (root/"assets").rglob("*"):
    if p.is_file() and p.suffix in {".html",".js",".css"}:
        text += p.read_text(errors="ignore")
if re.search(r"nats\.connect|new\s+WebSocket\s*\(|wss://|NATS\.connect", text):
    sys.exit("forbidden NATS/WebSocket in assets")
# fetch targets: allow /peergos-api or relative
for m in re.finditer(r"fetch\(([^)]+)\)", text):
    arg = m.group(1)
    if "http://" in arg or "https://" in arg:
        sys.exit("absolute fetch: "+arg)
print("peergos compliance: PASS")
PY
""",
    )


APPS = []


def define(app):
    APPS.append(app)


# --- cube browser ---
define(
    dict(
        repo="verae-app-cube-browser",
        display="Cube Browser",
        desc="List cubes, objects, and dual hashes without NATS",
        specialist="JS + integrity engineer",
        perms=["STORE_APP_DATA", "READ_CHOSEN_FOLDER"],
        folderAction=True,
        fileExtensions=["cube"],
        lib=r'''import { cubePaths } from "./peergos-sdk.mjs";

/**
 * listCubes
 * Input: client with list(path)
 * Output: string[] of cube ids (subFolders of /cubes/)
 * Behavior: GET /cubes/; ignore files at that level.
 */
export async function listCubes(client) {
  const listing = await client.list("/cubes");
  return listing.subFolders.slice().sort();
}

/**
 * listCubeObjects
 * Input: client, cubeId (non-empty string)
 * Output: { files: string[], subFolders: string[] }
 * Behavior: lists /cubes/<id>/ ; throws if cubeId empty.
 */
export async function listCubeObjects(client, cubeId) {
  if (!cubeId) throw new Error("cubeId required");
  const { root } = cubePaths(cubeId);
  return client.list(root);
}

/**
 * extractHashes
 * Input: object (manifest or object JSON)
 * Output: { sha256?: string, blake3?: string }
 * Behavior: reads hash, sha256, blake3, or nested hashes; missing keys omitted.
 */
export function extractHashes(obj) {
  if (!obj || typeof obj !== "object") return {};
  const out = {};
  const sha = obj.sha256 || obj.hash || (obj.hashes && obj.hashes.sha256);
  const b3 = obj.blake3 || (obj.hashes && obj.hashes.blake3);
  if (typeof sha === "string") out.sha256 = sha;
  if (typeof b3 === "string") out.blake3 = b3;
  return out;
}
''',
        test=r'''import assert from "node:assert/strict";
import { createClient, createMemoryFetch, cubePaths } from "../src/peergos-sdk.mjs";
import { listCubes, listCubeObjects, extractHashes } from "../src/lib.mjs";

const fetchImpl = createMemoryFetch();
const client = createClient(fetchImpl);
const a = cubePaths("CUBE-A");
const b = cubePaths("CUBE-B");
await client.writeJSON(a.manifest, { cube_id: "CUBE-A", hashes: { sha256: "sha256:aa", blake3: "blake3:bb" } });
await client.writeJSON(a.root + "/note.json", { text: "hi", sha256: "sha256:n1" });
await client.writeJSON(b.manifest, { cube_id: "CUBE-B" });

const ids = await listCubes(client);
assert.deepEqual(ids, ["CUBE-A", "CUBE-B"]);
const objs = await listCubeObjects(client, "CUBE-A");
assert.ok(objs.files.includes("manifest.json"));
assert.ok(objs.files.includes("note.json"));
const h = extractHashes(await client.readJSON(a.manifest));
assert.equal(h.sha256, "sha256:aa");
assert.equal(h.blake3, "blake3:bb");
assert.deepEqual(extractHashes(null), {});
await assert.rejects(() => listCubeObjects(client, ""), /cubeId/);
console.log("cube-browser tests ok");
''',
        ui="""<h1>Cube Browser</h1>
<p>Read-only list of cubes and dual hashes. No NATS.</p>
<button id="scan">Scan /cubes</button>
<div id="out"></div>
<div id="log"></div>
<script src="sdk.js"></script>
<script>
  const log = (m) => { document.getElementById("log").textContent += m + "\\n"; };
  const theme = new URL(location.href).searchParams.get("theme");
  if (theme) document.body.classList.add(theme);
  document.getElementById("scan").onclick = async () => {
    const S = window.VeraeSDK;
    const client = S.createClient();
    try {
      const ids = (await client.list("/cubes")).subFolders;
      let html = "";
      for (const id of ids) {
        const listing = await client.list("/cubes/" + encodeURIComponent(id));
        let hashes = "";
        if (listing.files.includes("manifest.json")) {
          const man = await client.readJSON("/cubes/" + encodeURIComponent(id) + "/manifest.json");
          const h = {
            sha256: man.sha256 || (man.hashes && man.hashes.sha256) || man.hash || "",
            blake3: man.blake3 || (man.hashes && man.hashes.blake3) || ""
          };
          hashes = JSON.stringify(h);
        }
        html += "<div class=\\"card\\"><strong>" + id + "</strong><br/>files: " +
          listing.files.join(", ") + "<br/>" + hashes + "</div>";
      }
      document.getElementById("out").innerHTML = html || "<p>No cubes</p>";
      log("scanned " + ids.length + " cubes");
    } catch (e) { log(e.message); }
  };
</script>
""",
        specs="""# Function specs — cube-browser

Specialist: JS + integrity engineer.

## listCubes(client)

| | |
|---|---|
| Input | `client` with `list(path)` |
| Output | `Promise<string[]>` sorted cube ids |
| Behavior | Lists `/cubes/` `subFolders`. Empty listing → `[]`. |

## listCubeObjects(client, cubeId)

| | |
|---|---|
| Input | `client`, `cubeId` non-empty string |
| Output | `Promise<{files, subFolders}>` |
| Behavior | Lists `/cubes/<cubeId>/`. Throws `cubeId required` if empty. |

## extractHashes(obj)

| | |
|---|---|
| Input | any |
| Output | `{sha256?, blake3?}` |
| Behavior | Reads `sha256`/`hash`/`hashes.sha256` and `blake3`/`hashes.blake3`. Null → `{}`. |
""",
    )
)

define(
    dict(
        repo="verae-app-share-wizard",
        display="Share Wizard",
        desc="Share modes A/B/C; write a share plan into the cube",
        specialist="Frontend + integrity engineer",
        perms=["STORE_APP_DATA", "EDIT_CHOSEN_FILE", "READ_CHOSEN_FOLDER"],
        folderAction=True,
        fileExtensions=["cube"],
        lib=r'''import { cubePaths, validateShare } from "./peergos-sdk.mjs";
export { validateShare };

/**
 * buildSharePlan
 * Input: mode 'A'|'B'|'C', selectedHashes string[]
 * Output: {mode, selected, receipts_preserved:true}
 * Behavior: delegates to validateShare; copies selected array.
 */
export function buildSharePlan(mode, selectedHashes) {
  return validateShare(mode, selectedHashes);
}

/**
 * writeSharePlan
 * Input: client, cubeId, plan from buildSharePlan
 * Output: path string `/cubes/<id>/share-plan.json`
 * Behavior: PUT plan JSON. Throws if cubeId empty.
 */
export async function writeSharePlan(client, cubeId, plan) {
  if (!cubeId) throw new Error("cubeId required");
  if (!plan || !plan.mode) throw new Error("plan required");
  const path = cubePaths(cubeId).root + "/share-plan.json";
  await client.writeJSON(path, plan);
  return path;
}

/**
 * planIncludes
 * Input: plan, hash string
 * Output: boolean
 */
export function planIncludes(plan, hash) {
  return !!(plan && Array.isArray(plan.selected) && plan.selected.indexOf(hash) >= 0);
}
''',
        test=r'''import assert from "node:assert/strict";
import { createClient, createMemoryFetch } from "../src/peergos-sdk.mjs";
import { buildSharePlan, writeSharePlan, planIncludes } from "../src/lib.mjs";

assert.throws(() => buildSharePlan("Z", ["h"]), /mode/);
const plan = buildSharePlan("C", ["sha256:a", "sha256:b"]);
assert.equal(plan.receipts_preserved, true);
assert.ok(planIncludes(plan, "sha256:a"));
assert.equal(planIncludes(plan, "sha256:zzz"), false);

const client = createClient(createMemoryFetch());
const path = await writeSharePlan(client, "CUBE-1", plan);
assert.equal(path, "/cubes/CUBE-1/share-plan.json");
const saved = await client.readJSON(path);
assert.equal(saved.mode, "C");
await assert.rejects(() => writeSharePlan(client, "", plan), /cubeId/);
console.log("share-wizard tests ok");
''',
        ui="""<h1>Share Wizard</h1>
<p>Modes A proofs / B + metadata / C + files. Writes share-plan.json. No NATS.</p>
<label>Cube id <input id="cid" value="CUBE-1"/></label>
<label>Mode <select id="mode"><option>A</option><option>B</option><option selected>C</option></select></label>
<label>Hashes (comma) <input id="hashes" value="sha256:obj1,sha256:obj2" size="40"/></label>
<button id="go">Write plan</button>
<div id="log"></div>
<script src="sdk.js"></script>
<script>
  const log = (m) => { document.getElementById("log").textContent += m + "\\n"; };
  document.getElementById("go").onclick = async () => {
    const S = window.VeraeSDK;
    const client = S.createClient();
    const id = document.getElementById("cid").value.trim();
    const mode = document.getElementById("mode").value;
    const hashes = document.getElementById("hashes").value.split(",").map((s) => s.trim()).filter(Boolean);
    try {
      const plan = S.validateShare(mode, hashes);
      const path = S.cubePaths(id).root + "/share-plan.json";
      await client.writeJSON(path, plan);
      log("wrote " + path + " " + JSON.stringify(plan));
    } catch (e) { log(e.message); }
  };
</script>
""",
        specs="""# Function specs — share-wizard

Specialist: Frontend + integrity.

## buildSharePlan(mode, selectedHashes)

Delegates to `validateShare`. See verae-app-sdk.

## writeSharePlan(client, cubeId, plan)

PUT `/cubes/<id>/share-plan.json`. Throws `cubeId required` / `plan required`.

## planIncludes(plan, hash)

True iff `plan.selected` contains hash.
""",
    )
)

define(
    dict(
        repo="verae-app-timestamp-inbox",
        display="TS Inbox",
        desc="Show Local/Shared/Global timestamp receipts from inbox",
        specialist="Timestamp engineer + JS",
        perms=["STORE_APP_DATA"],
        folderAction=False,
        fileExtensions=[],
        lib=r'''/**
 * listInbox
 * Input: client.list
 * Output: string[] filenames under /inbox/
 */
export async function listInbox(client) {
  const listing = await client.list("/inbox");
  return listing.files.filter((f) => f.endsWith(".json")).sort();
}

/**
 * parseReceipt
 * Input: JSON object
 * Output: {scope, hash, cube_id, ok}
 * Behavior: scope default "local"; ok false if missing hash.
 */
export function parseReceipt(obj) {
  if (!obj || typeof obj !== "object") return { scope: "local", hash: "", cube_id: "", ok: false };
  const scope = obj.scope || (obj.receipt && obj.receipt.scope) || "local";
  const hash = obj.hash || (obj.receipt && obj.receipt.hash) || "";
  const cube_id = obj.cube_id || (obj.receipt && obj.receipt.cube_id) || "";
  return { scope, hash, cube_id, ok: !!hash };
}

/**
 * scopeRank
 * Input: "local"|"shared"|"global"|other
 * Output: 1, 2, 3, or 0
 */
export function scopeRank(scope) {
  if (scope === "local") return 1;
  if (scope === "shared") return 2;
  if (scope === "global") return 3;
  return 0;
}
''',
        test=r'''import assert from "node:assert/strict";
import { createClient, createMemoryFetch } from "../src/peergos-sdk.mjs";
import { listInbox, parseReceipt, scopeRank } from "../src/lib.mjs";

const fetchImpl = createMemoryFetch();
const client = createClient(fetchImpl);
await client.writeJSON("/inbox/a.reply.json", { hash: "sha256:1", scope: "global", cube_id: "C" });
await client.writeJSON("/inbox/note.txt", { x: 1 });
const files = await listInbox(client);
assert.deepEqual(files, ["a.reply.json"]);
const r = parseReceipt(await client.readJSON("/inbox/a.reply.json"));
assert.equal(r.ok, true);
assert.equal(r.scope, "global");
assert.equal(scopeRank("local"), 1);
assert.equal(scopeRank("shared"), 2);
assert.equal(scopeRank("global"), 3);
assert.equal(scopeRank("nope"), 0);
assert.equal(parseReceipt(null).ok, false);
console.log("timestamp-inbox tests ok");
''',
        ui="""<h1>Timestamp inbox</h1>
<p>Reads connector replies in /inbox. Local=1 Shared=2 Global=3.</p>
<button id="load">Load inbox</button>
<div id="out"></div>
<div id="log"></div>
<script src="sdk.js"></script>
<script>
  const log = (m) => { document.getElementById("log").textContent += m + "\\n"; };
  function rank(s) { return s==="global"?3:s==="shared"?2:s==="local"?1:0; }
  document.getElementById("load").onclick = async () => {
    const client = window.VeraeSDK.createClient();
    try {
      const listing = await client.list("/inbox");
      const files = listing.files.filter((f) => f.endsWith(".json"));
      let html = "";
      for (const f of files) {
        const obj = await client.readJSON("/inbox/" + f);
        const scope = obj.scope || (obj.receipt && obj.receipt.scope) || "local";
        const hash = obj.hash || (obj.receipt && obj.receipt.hash) || "";
        html += "<div class=\\"card\\">" + f + " scope=" + scope + " rank=" + rank(scope) + " hash=" + hash + "</div>";
      }
      document.getElementById("out").innerHTML = html || "<p>Empty inbox</p>";
      log("loaded " + files.length);
    } catch (e) { log(e.message); }
  };
</script>
""",
        specs="""# Function specs — timestamp-inbox

Specialist: Timestamp + JS.

## listInbox(client) → Promise<string[]>
JSON filenames in `/inbox/`.

## parseReceipt(obj) → {scope, hash, cube_id, ok}
Defaults scope to local; ok iff hash present.

## scopeRank(scope) → 0|1|2|3
local=1 shared=2 global=3 else 0.
""",
    )
)

define(
    dict(
        repo="verae-app-iso-export",
        display="ISO Export",
        desc="Enqueue verae.cube.export for host xorriso ISO packager",
        specialist="Storage + wine frontend",
        perms=["STORE_APP_DATA"],
        folderAction=True,
        fileExtensions=["cube"],
        lib=r'''import { makeEnvelope, enqueue, validateShare } from "./peergos-sdk.mjs";

export const EXPORT_SUBJECT = "verae.cube.export";

/**
 * enqueueExport
 * Input: client, {cube_id, format="iso", share_mode="A"}
 * Output: outbox path
 * Behavior: validates share_mode; writes envelope; reply_file `<id>.export.json`.
 */
export async function enqueueExport(client, opts) {
  if (!opts || !opts.cube_id) throw new Error("cube_id required");
  const format = opts.format || "iso";
  if (format !== "iso") throw new Error("format must be iso");
  const share_mode = opts.share_mode || "A";
  validateShare(share_mode, opts.selected || ["sha256:tip"]);
  const env = makeEnvelope(EXPORT_SUBJECT, {
    cube_id: opts.cube_id,
    format,
    share_mode,
  }, opts.cube_id + ".export.json");
  return enqueue(client, opts.cube_id + "-export", env);
}

/**
 * parseExportAck
 * Input: inbox JSON
 * Output: {ok, path?, error?}
 */
export function parseExportAck(obj) {
  if (!obj || typeof obj !== "object") return { ok: false, error: "empty ack" };
  if (obj.error) return { ok: false, error: String(obj.error) };
  if (obj.path) return { ok: true, path: String(obj.path) };
  return { ok: false, error: "missing path" };
}
''',
        test=r'''import assert from "node:assert/strict";
import { createClient, createMemoryFetch } from "../src/peergos-sdk.mjs";
import { enqueueExport, parseExportAck, EXPORT_SUBJECT } from "../src/lib.mjs";

const fetchImpl = createMemoryFetch();
const client = createClient(fetchImpl);
const path = await enqueueExport(client, { cube_id: "WINE-1", share_mode: "A" });
assert.equal(path, "/outbox/WINE-1-export.json");
const env = JSON.parse(fetchImpl.store.get(path));
assert.equal(env.subject, EXPORT_SUBJECT);
assert.equal(env.payload.format, "iso");
assert.equal(parseExportAck({ path: "/exports/WINE-1.iso" }).ok, true);
assert.equal(parseExportAck({ error: "xorriso failed" }).ok, false);
await assert.rejects(() => enqueueExport(client, {}), /cube_id/);
console.log("iso-export tests ok");
''',
        ui="""<h1>ISO Export</h1>
<p>Queues verae.cube.export. Host connector runs xorriso. Share A/B/C selects payload.</p>
<label>Cube <input id="cid" value="WINE-1"/></label>
<label>Mode <select id="mode"><option>A</option><option>B</option><option>C</option></select></label>
<button id="go">Enqueue export</button>
<div id="log"></div>
<script src="sdk.js"></script>
<script>
  const log = (m) => { document.getElementById("log").textContent += m + "\\n"; };
  document.getElementById("go").onclick = async () => {
    const S = window.VeraeSDK;
    const client = S.createClient();
    const id = document.getElementById("cid").value.trim();
    const mode = document.getElementById("mode").value;
    try {
      S.validateShare(mode, ["sha256:tip"]);
      const env = S.makeEnvelope("verae.cube.export", { cube_id: id, format: "iso", share_mode: mode }, id + ".export.json");
      await S.enqueue(client, id + "-export", env);
      log("queued " + id + " mode " + mode);
    } catch (e) { log(e.message); }
  };
</script>
""",
        specs="""# Function specs — iso-export

Specialist: Storage + wine frontend.

## enqueueExport(client, opts)
opts.cube_id required. format must be `iso`. share_mode via validateShare.
Writes `/outbox/<cube_id>-export.json` subject `verae.cube.export`.

## parseExportAck(obj)
ok+path or ok false + error.
""",
    )
)

define(
    dict(
        repo="verae-app-itad-board",
        display="ITAD Board",
        desc="Kanban pickup through wipe and sale; append via outbox",
        specialist="ITAD SME + JS",
        perms=["STORE_APP_DATA"],
        folderAction=False,
        fileExtensions=["cube"],
        lib=r'''import { makeEnvelope, enqueue } from "./peergos-sdk.mjs";

export const STAGES = ["pickup", "wipe", "disposition", "sale"];

/**
 * nextStage
 * Input: current stage string
 * Output: next stage or null if sale / unknown
 */
export function nextStage(current) {
  const i = STAGES.indexOf(current);
  if (i < 0 || i === STAGES.length - 1) return null;
  return STAGES[i + 1];
}

/**
 * columnize
 * Input: events [{id, stage, ...}]
 * Output: {pickup:[], wipe:[], disposition:[], sale:[]}
 * Behavior: unknown stage ignored.
 */
export function columnize(events) {
  const cols = { pickup: [], wipe: [], disposition: [], sale: [] };
  for (const ev of events || []) {
    if (ev && cols[ev.stage]) cols[ev.stage].push(ev);
  }
  return cols;
}

/**
 * enqueueStage
 * Input: client, {cube_id, asset_id, stage, event_type?}
 * Output: outbox path
 * Behavior: subject verae.cube.append; block.event_type defaults to stage.
 */
export async function enqueueStage(client, opts) {
  if (!opts || !opts.cube_id) throw new Error("cube_id required");
  if (!opts.asset_id) throw new Error("asset_id required");
  if (STAGES.indexOf(opts.stage) < 0) throw new Error("invalid stage");
  const block = {
    event_type: opts.event_type || opts.stage,
    asset_id: opts.asset_id,
    stage: opts.stage,
  };
  return enqueue(client, opts.asset_id + "-" + opts.stage, makeEnvelope("verae.cube.append", { block }));
}
''',
        test=r'''import assert from "node:assert/strict";
import { createClient, createMemoryFetch } from "../src/peergos-sdk.mjs";
import { STAGES, nextStage, columnize, enqueueStage } from "../src/lib.mjs";

assert.equal(STAGES.length, 4);
assert.equal(nextStage("pickup"), "wipe");
assert.equal(nextStage("sale"), null);
assert.equal(nextStage("nope"), null);
const cols = columnize([{id:1, stage:"pickup"}, {id:2, stage:"wipe"}, {id:3, stage:"ghost"}]);
assert.equal(cols.pickup.length, 1);
assert.equal(cols.wipe.length, 1);
assert.equal(cols.sale.length, 0);
const client = createClient(createMemoryFetch());
const p = await enqueueStage(client, { cube_id: "ITAD-1", asset_id: "CZC1", stage: "wipe" });
assert.equal(p, "/outbox/CZC1-wipe.json");
await assert.rejects(() => enqueueStage(client, { cube_id: "x", asset_id: "y", stage: "nope" }), /stage/);
console.log("itad-board tests ok");
''',
        ui="""<h1>ITAD Board</h1>
<p>pickup → wipe → disposition → sale. Appends via verae.cube.append.</p>
<label>Cube <input id="cid" value="ITAD-1"/></label>
<label>Asset <input id="aid" value="CZC1"/></label>
<label>Stage <select id="st"><option>pickup</option><option>wipe</option><option>disposition</option><option>sale</option></select></label>
<button id="go">Queue stage</button>
<div id="log"></div>
<script src="sdk.js"></script>
<script>
  const log = (m) => { document.getElementById("log").textContent += m + "\\n"; };
  document.getElementById("go").onclick = async () => {
    const S = window.VeraeSDK;
    const client = S.createClient();
    const cube = document.getElementById("cid").value.trim();
    const asset = document.getElementById("aid").value.trim();
    const stage = document.getElementById("st").value;
    try {
      const env = S.makeEnvelope("verae.cube.append", { block: { event_type: stage, asset_id: asset, stage } });
      await S.enqueue(client, asset + "-" + stage, env);
      log("queued " + asset + " " + stage + " on " + cube);
    } catch (e) { log(e.message); }
  };
</script>
""",
        specs="""# Function specs — itad-board

Specialist: ITAD SME + JS.

## STAGES
`pickup`, `wipe`, `disposition`, `sale`.

## nextStage(current) → string|null

## columnize(events) → columns object

## enqueueStage(client, opts)
`verae.cube.append` with `{block:{event_type, asset_id, stage}}`.
""",
    )
)

define(
    dict(
        repo="verae-app-sig-verify",
        display="Sig Verify",
        desc="List valid/revoked signatures; enqueue verae.sig.verify",
        specialist="Crypto + JS",
        perms=["STORE_APP_DATA"],
        folderAction=False,
        fileExtensions=[],
        lib=r'''import { makeEnvelope, enqueue } from "./peergos-sdk.mjs";

export const VERIFY_SUBJECT = "verae.sig.verify";

export async function listValid(client) {
  const listing = await client.list("/signatures/valid");
  return listing.files.filter((f) => f.endsWith(".json")).sort();
}

export async function listRevoked(client) {
  const listing = await client.list("/signatures/revoked");
  return listing.files.filter((f) => f.endsWith(".json")).sort();
}

/**
 * isRevoked
 * Input: filename or id, revoked filenames[]
 * Output: boolean — true if exact file or stem matches a revoked name
 */
export function isRevoked(id, revokedFiles) {
  if (!id) return false;
  const set = new Set(revokedFiles || []);
  if (set.has(id) || set.has(id + ".json")) return true;
  const stem = id.replace(/\.json$/, "");
  return set.has(stem) || set.has(stem + ".json");
}

export async function enqueueVerify(client, opts) {
  if (!opts || !opts.object_sha256) throw new Error("object_sha256 required");
  if (!opts.signature_id) throw new Error("signature_id required");
  return enqueue(client, opts.signature_id + "-verify", makeEnvelope(VERIFY_SUBJECT, {
    object_sha256: opts.object_sha256,
    signature_id: opts.signature_id,
  }, opts.signature_id + ".verify.json"));
}
''',
        test=r'''import assert from "node:assert/strict";
import { createClient, createMemoryFetch } from "../src/peergos-sdk.mjs";
import { listValid, listRevoked, isRevoked, enqueueVerify, VERIFY_SUBJECT } from "../src/lib.mjs";

const fetchImpl = createMemoryFetch();
const client = createClient(fetchImpl);
await client.writeJSON("/signatures/valid/sig1.json", { object_sha256: "sha256:doc" });
await client.writeJSON("/signatures/revoked/sig1.json", { revoked: true });
assert.deepEqual(await listValid(client), ["sig1.json"]);
assert.deepEqual(await listRevoked(client), ["sig1.json"]);
assert.equal(isRevoked("sig1", ["sig1.json"]), true);
assert.equal(isRevoked("other", ["sig1.json"]), false);
const p = await enqueueVerify(client, { object_sha256: "sha256:doc", signature_id: "sig1" });
const env = JSON.parse(fetchImpl.store.get(p));
assert.equal(env.subject, VERIFY_SUBJECT);
await assert.rejects(() => enqueueVerify(client, { object_sha256: "x" }), /signature_id/);
console.log("sig-verify tests ok");
''',
        ui="""<h1>Signature verify</h1>
<p>Reads signatures/valid and revoked. Queues verae.sig.verify.</p>
<button id="scan">Scan</button>
<label>SHA-256 <input id="hash" value="sha256:doc"/></label>
<label>Sig id <input id="sid" value="sig1"/></label>
<button id="go">Enqueue verify</button>
<div id="out"></div>
<div id="log"></div>
<script src="sdk.js"></script>
<script>
  const log = (m) => { document.getElementById("log").textContent += m + "\\n"; };
  document.getElementById("scan").onclick = async () => {
    const c = window.VeraeSDK.createClient();
    try {
      const v = (await c.list("/signatures/valid")).files;
      const r = (await c.list("/signatures/revoked")).files;
      document.getElementById("out").innerHTML =
        "<div class=\\"card\\">valid: " + v.join(", ") + "</div>" +
        "<div class=\\"card\\">revoked: " + r.join(", ") + "</div>";
    } catch (e) { log(e.message); }
  };
  document.getElementById("go").onclick = async () => {
    const S = window.VeraeSDK;
    const c = S.createClient();
    const sid = document.getElementById("sid").value.trim();
    const hash = document.getElementById("hash").value.trim();
    try {
      const env = S.makeEnvelope("verae.sig.verify", { object_sha256: hash, signature_id: sid }, sid + ".verify.json");
      await S.enqueue(c, sid + "-verify", env);
      log("queued verify " + sid);
    } catch (e) { log(e.message); }
  };
</script>
""",
        specs="""# Function specs — sig-verify

Specialist: Crypto + JS.

## listValid / listRevoked → JSON filenames

## isRevoked(id, revokedFiles) → boolean

## enqueueVerify(client, {object_sha256, signature_id})
Subject `verae.sig.verify`.
""",
    )
)

define(
    dict(
        repo="verae-app-connector-status",
        display="Conn Status",
        desc="List outbox pending vs inbox acked connector jobs",
        specialist="Messaging + host engineer",
        perms=["STORE_APP_DATA"],
        folderAction=False,
        fileExtensions=[],
        lib=r'''/**
 * listOutbox / listInbox — JSON names under those folders.
 */
export async function listOutbox(client) {
  const listing = await client.list("/outbox");
  return listing.files.filter((f) => f.endsWith(".json")).sort();
}

export async function listInbox(client) {
  const listing = await client.list("/inbox");
  return listing.files.filter((f) => f.endsWith(".json")).sort();
}

/**
 * jobStem
 * Input: filename
 * Output: stem without .json and trailing -export|-verify|-ts
 */
export function jobStem(name) {
  return String(name || "").replace(/\.json$/, "");
}

/**
 * classifyJobs
 * Input: outbox names[], inbox names[]
 * Output: {pending, acked}
 * Behavior: outbox job is acked if any inbox file starts with the same stem
 * or equals reply_file pattern `<stem>.` prefix.
 */
export function classifyJobs(outboxFiles, inboxFiles) {
  const inbox = inboxFiles || [];
  const pending = [];
  const acked = [];
  for (const f of outboxFiles || []) {
    const stem = jobStem(f);
    const done = inbox.some((i) => i === f || i.startsWith(stem) || jobStem(i).startsWith(stem.split("-")[0]));
    (done ? acked : pending).push(f);
  }
  return { pending, acked };
}
''',
        test=r'''import assert from "node:assert/strict";
import { createClient, createMemoryFetch } from "../src/peergos-sdk.mjs";
import { listOutbox, listInbox, classifyJobs, jobStem } from "../src/lib.mjs";

const fetchImpl = createMemoryFetch();
const client = createClient(fetchImpl);
await client.writeJSON("/outbox/job1.json", { subject: "verae.ts.request" });
await client.writeJSON("/outbox/job2.json", { subject: "verae.ts.request" });
await client.writeJSON("/inbox/job1.reply.json", { hash: "x" });
assert.deepEqual(await listOutbox(client), ["job1.json", "job2.json"]);
assert.deepEqual(await listInbox(client), ["job1.reply.json"]);
assert.equal(jobStem("job1.json"), "job1");
const cls = classifyJobs(["job1.json", "job2.json"], ["job1.reply.json"]);
assert.deepEqual(cls.acked, ["job1.json"]);
assert.deepEqual(cls.pending, ["job2.json"]);
console.log("connector-status tests ok");
''',
        ui="""<h1>Connector status</h1>
<p>Outbox = pending. Inbox match = acked. Ops view. No NATS in the iframe.</p>
<button id="scan">Scan</button>
<div id="out"></div>
<div id="log"></div>
<script src="sdk.js"></script>
<script>
  const log = (m) => { document.getElementById("log").textContent += m + "\\n"; };
  document.getElementById("scan").onclick = async () => {
    const c = window.VeraeSDK.createClient();
    try {
      const o = (await c.list("/outbox")).files.filter((f) => f.endsWith(".json"));
      const i = (await c.list("/inbox")).files.filter((f) => f.endsWith(".json"));
      document.getElementById("out").innerHTML =
        "<div class=\\"card\\">outbox: " + o.join(", ") + "</div>" +
        "<div class=\\"card\\">inbox: " + i.join(", ") + "</div>";
      log("outbox " + o.length + " inbox " + i.length);
    } catch (e) { log(e.message); }
  };
</script>
""",
        specs="""# Function specs — connector-status

Specialist: Messaging + host engineer.

## listOutbox / listInbox → JSON filenames

## jobStem(name) → string

## classifyJobs(outboxFiles, inboxFiles) → {pending, acked}
Acked if an inbox name starts with the outbox stem.
""",
    )
)


def html_page(title, body):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{title}</title>
  <style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""


def readme(app):
    return f"""# {app['repo']}

{app['desc']}

**Specialist:** {app['specialist']}  
**Plan:** `PLAN-APPS-WAVE2.md`  
**Pattern:** Peergos sandbox + file store; NATS only via outbox connector.

## Install (Peergos)

1. Sign in at https://peergos.georgelambert.org
2. Apps → Custom, or upload this folder and **Install App** on `peergos-app.json`.
3. Grant the listed permissions.

```
OrgTool install-app <server> <user> <pass> {app['repo'].replace('verae-app-','')} .
```

## Develop

```
make test
make certify
```

## Docs

- [docs/SPECS.md](docs/SPECS.md) — function names, I/O, behavior
- [docs/INSTALL.md](docs/INSTALL.md)
- [docs/DEVELOPER.md](docs/DEVELOPER.md)
"""


def install_md(app):
    return f"""# Installation — {app['display']}

## Requirements

- Peergos account on a Verae host
- Permissions: {', '.join(app['perms'])}
- For outbox subjects: desktop-host connector running

## Steps

1. Copy `peergos-app.json` and `assets/` into Drive (or use OrgTool / gallery).
2. Context menu on `peergos-app.json` → **Install App**.
3. Open from Apps launcher.
4. Dark theme: Peergos passes `?theme=dark-mode`.

## Uninstall

Apps launcher → remove `{app['display']}`. Data remains under `/.apps/` until deleted.
"""


def developer_md(app):
    return f"""# Developer reference — {app['repo']}

## Layout

```
peergos-app.json
assets/index.html
assets/sdk.js
src/peergos-sdk.mjs
src/lib.mjs
tests/lib.test.mjs
tests/certify-peergos.sh
```

## Integration

Sandbox `fetch` → `/peergos-api/v0/data`.  
Outbox JSON → connector → NATS (`verae-nats-bus/schemas/subjects.json`).  
Inbox JSON → app lists `/inbox/`.

## Tests

`make test` runs Node unit tests against an in-memory `fetch`.  
`make certify` adds Peergos compliance (manifest bounds, no NATS/WebSocket).

{app['specs']}
"""


def emit(app):
    root = RESEARCH / app["repo"]
    if root.exists() and (root / ".git").exists():
        # refresh files in existing repo
        pass
    root.mkdir(parents=True, exist_ok=True)
    common_files(root, app["repo"], app["display"], app["specialist"], "")
    write(root / "src/lib.mjs", app["lib"])
    write(root / "tests/lib.test.mjs", app["test"])
    write(root / "assets/index.html", html_page(app["display"], app["ui"]))
    write(
        root / "peergos-app.json",
        json.dumps(
            {
                "schemaVersion": 1,
                "displayName": app["display"][:25],
                "description": app["desc"][:100],
                "version": "0.1.0",
                "author": "Verae",
                "launchable": True,
                "folderAction": bool(app.get("folderAction")),
                "fileExtensions": app.get("fileExtensions") or [],
                "permissions": app["perms"],
            },
            indent=2,
        )
        + "\n",
    )
    write(root / "README.md", readme(app))
    write(root / "docs/SPECS.md", app["specs"])
    write(root / "docs/INSTALL.md", install_md(app))
    write(root / "docs/DEVELOPER.md", developer_md(app))
    write(
        root / "docs/OVERVIEW.md",
        f"# {app['display']}\n\n{app['desc']}\n\nSpecialist: {app['specialist']}.\n",
    )
    return root


def main():
    for app in APPS:
        p = emit(app)
        print("wrote", p)


if __name__ == "__main__":
    main()
