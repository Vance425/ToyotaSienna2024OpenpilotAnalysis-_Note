#!/usr/bin/env node
// Probe Toyota SecOC key candidates against sync MACs and protected 0x2E4 frames.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";

const SYNC_ADDR = 0x0f;
const DEFAULT_TARGET_ADDR = 0x2e4;

function parseArgs(argv) {
  const args = {
    logs: [],
    candidateCsvs: [],
    candidateKeyFiles: [],
    outputDir: "",
    targetAddr: DEFAULT_TARGET_ADDR,
    maxCandidates: 500,
    maxSync: 64,
    maxProtected: 64,
    bus: 0,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--candidate-csv") args.candidateCsvs.push(argv[++i]);
    else if (arg === "--candidate-key-file") args.candidateKeyFiles.push(argv[++i]);
    else if (arg === "--output-dir") args.outputDir = argv[++i];
    else if (arg === "--target-addr") args.targetAddr = Number.parseInt(argv[++i].toLowerCase().replace(/^0x/, ""), 16);
    else if (arg === "--max-candidates") args.maxCandidates = Number.parseInt(argv[++i], 10);
    else if (arg === "--max-sync") args.maxSync = Number.parseInt(argv[++i], 10);
    else if (arg === "--max-protected") args.maxProtected = Number.parseInt(argv[++i], 10);
    else if (arg === "--bus") args.bus = Number.parseInt(argv[++i], 10);
    else args.logs.push(arg);
  }
  if (!args.outputDir) throw new Error("missing --output-dir");
  if (!args.logs.length) throw new Error("provide at least one ndjson log file");
  if (!args.candidateCsvs.length && !args.candidateKeyFiles.length) {
    throw new Error("provide at least one --candidate-csv or --candidate-key-file");
  }
  return args;
}

function parseCsvLine(line) {
  const cells = [];
  let cur = "";
  let quoted = false;
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];
    if (quoted && ch === '"' && line[i + 1] === '"') {
      cur += '"';
      i += 1;
    } else if (ch === '"') {
      quoted = !quoted;
    } else if (ch === "," && !quoted) {
      cells.push(cur);
      cur = "";
    } else {
      cur += ch;
    }
  }
  cells.push(cur);
  return cells;
}

function loadCandidates(csvPaths, limit) {
  const seen = new Set();
  const candidates = [];
  for (const csvPath of csvPaths) {
    const text = fs.readFileSync(csvPath, "utf8");
    const lines = text.split(/\r?\n/).filter(Boolean);
    if (!lines.length) continue;
    const header = parseCsvLine(lines[0]);
    const keyIndex = header.indexOf("candidate_hex");
    const scoreIndex = header.indexOf("score");
    if (keyIndex < 0) continue;
    for (let i = 1; i < lines.length; i += 1) {
      const row = parseCsvLine(lines[i]);
      const keyHex = (row[keyIndex] || "").replace(/[^0-9a-fA-F]/g, "").toLowerCase();
      if (keyHex.length !== 32 || seen.has(keyHex)) continue;
      seen.add(keyHex);
      const score = scoreIndex >= 0 ? Number.parseFloat(row[scoreIndex] || "0") : 0;
      const source = `${csvPath}:row${i + 1}`;
      candidates.push({ keyHex, key: Buffer.from(keyHex, "hex"), score, source });
    }
  }
  candidates.sort((a, b) => (Number.isFinite(b.score) ? b.score : 0) - (Number.isFinite(a.score) ? a.score : 0));
  return candidates.slice(0, limit);
}

function loadCandidateKeyFiles(keyFilePaths) {
  const candidates = [];
  for (const keyFilePath of keyFilePaths) {
    const keyHex = fs.readFileSync(keyFilePath, "utf8").replace(/[^0-9a-fA-F]/g, "").toLowerCase();
    if (keyHex.length !== 32) throw new Error(`candidate key file must contain exactly 32 hex chars: ${keyFilePath}`);
    candidates.push({
      keyHex,
      key: Buffer.from(keyHex, "hex"),
      score: 0,
      source: `${keyFilePath}:keyfile`,
    });
  }
  return candidates;
}

function xor16(a, b) {
  const out = Buffer.alloc(16);
  for (let i = 0; i < 16; i += 1) out[i] = a[i] ^ b[i];
  return out;
}

function leftShiftOne(input) {
  const out = Buffer.alloc(16);
  let carry = 0;
  for (let i = 15; i >= 0; i -= 1) {
    out[i] = ((input[i] << 1) & 0xff) | carry;
    carry = (input[i] & 0x80) ? 1 : 0;
  }
  return out;
}

function aesBlock(key, block) {
  const cipher = crypto.createCipheriv("aes-128-ecb", key, null);
  cipher.setAutoPadding(false);
  return Buffer.concat([cipher.update(block), cipher.final()]);
}

function cmac(key, message) {
  const zero = Buffer.alloc(16);
  const l = aesBlock(key, zero);
  let k1 = leftShiftOne(l);
  if (l[0] & 0x80) k1[15] ^= 0x87;
  let k2 = leftShiftOne(k1);
  if (k1[0] & 0x80) k2[15] ^= 0x87;

  const n = Math.max(1, Math.ceil(message.length / 16));
  const complete = message.length > 0 && message.length % 16 === 0;
  const blocks = [];
  for (let i = 0; i < n - 1; i += 1) blocks.push(message.subarray(i * 16, i * 16 + 16));

  let last;
  if (complete) {
    last = xor16(message.subarray((n - 1) * 16, n * 16), k1);
  } else {
    const padded = Buffer.alloc(16);
    const tail = message.subarray((n - 1) * 16);
    tail.copy(padded);
    padded[tail.length] = 0x80;
    last = xor16(padded, k2);
  }

  let x = Buffer.alloc(16);
  for (const block of blocks) x = aesBlock(key, xor16(x, block));
  return aesBlock(key, xor16(x, last));
}

function buildSyncMacHex(key, tripCnt, resetCnt) {
  const msg = Buffer.alloc(8);
  msg.writeUInt16BE(0x0f, 0);
  msg.writeUInt16BE(tripCnt, 2);
  const resetShifted = resetCnt << 12;
  msg[4] = (resetShifted >>> 16) & 0xff;
  msg[5] = (resetShifted >>> 8) & 0xff;
  msg[6] = resetShifted & 0xff;
  return cmac(key, msg.subarray(0, 7)).toString("hex").slice(0, 7);
}

function buildProtectedMacHex(key, addr, prefix, tripCnt, resetCnt, msgCnt) {
  const freshnessInt = (resetCnt << 12) | ((msgCnt & 0xff) << 4) | ((resetCnt & 0x03) << 2);
  const msg = Buffer.alloc(12);
  msg.writeUInt16BE(addr, 0);
  prefix.copy(msg, 2);
  msg.writeUInt16BE(tripCnt, 6);
  msg.writeUInt32BE(freshnessInt >>> 0, 8);
  return cmac(key, msg).toString("hex").slice(0, 7);
}

function decodeSync(dataHex, tsMs, bus) {
  const data = Buffer.from(dataHex, "hex");
  if (data.length !== 8) return null;
  return {
    tsMs,
    bus,
    tripCnt: (data[0] << 8) | data[1],
    resetCnt: (data[2] << 12) | (data[3] << 4) | (data[4] >> 4),
    authHex: (((data[4] & 0x0f) << 24) | (data[5] << 16) | (data[6] << 8) | data[7]).toString(16).padStart(7, "0"),
  };
}

function decodeProtected(dataHex, tsMs, bus, sync) {
  const data = Buffer.from(dataHex, "hex");
  if (data.length !== 8 || !sync) return null;
  const flags = data[4] >> 4;
  return {
    tsMs,
    bus,
    prefix: data.subarray(0, 4),
    prefixHex: data.subarray(0, 4).toString("hex"),
    msgCntLow2: flags >> 2,
    resetLow2: flags & 0x03,
    authHex: (((data[4] & 0x0f) << 24) | (data[5] << 16) | (data[6] << 8) | data[7]).toString(16).padStart(7, "0"),
    tripCnt: sync.tripCnt,
    resetCnt: sync.resetCnt,
    syncAgeMs: tsMs - sync.tsMs,
  };
}

async function collectFrames(logPaths, targetAddr, bus, maxSync, maxProtected) {
  const syncs = [];
  const protectedFrames = [];
  const lastSyncByBus = new Map();
  const syncDedup = new Set();
  for (const logPath of logPaths) {
    const rl = readline.createInterface({
      input: fs.createReadStream(logPath, { encoding: "utf8" }),
      crlfDelay: Infinity,
    });
    for await (const line of rl) {
      let row;
      try {
        row = JSON.parse(line);
      } catch {
        continue;
      }
      const addr = Number(row.addr);
      const rowBus = Number(row.bus);
      const tsMs = Number(row.ts_ms);
      const dataHex = String(row.data || "").toLowerCase();
      if (addr === SYNC_ADDR) {
        const sync = decodeSync(dataHex, tsMs, rowBus);
        if (!sync) continue;
        lastSyncByBus.set(rowBus, sync);
        const key = `${sync.tripCnt}:${sync.resetCnt}:${sync.authHex}`;
        if (rowBus === bus && syncs.length < maxSync && !syncDedup.has(key)) {
          syncDedup.add(key);
          syncs.push(sync);
        }
      } else if (addr === targetAddr && rowBus === bus && protectedFrames.length < maxProtected) {
        const sync = lastSyncByBus.get(rowBus);
        const frame = decodeProtected(dataHex, tsMs, rowBus, sync);
        if (!frame) continue;
        if (frame.syncAgeMs < 0 || frame.syncAgeMs > 1000) continue;
        if ((frame.resetCnt & 0x03) !== frame.resetLow2) continue;
        protectedFrames.push(frame);
      }
    }
  }
  return { syncs, protectedFrames };
}

function probeCandidate(candidate, syncs, protectedFrames, targetAddr) {
  let syncMatches = 0;
  for (const sync of syncs) {
    if (buildSyncMacHex(candidate.key, sync.tripCnt, sync.resetCnt) === sync.authHex) syncMatches += 1;
  }
  let protectedMatches = 0;
  const msgCntHits = [];
  for (const frame of protectedFrames) {
    let matched = false;
    let hit = null;
    for (let msgCnt = frame.msgCntLow2; msgCnt < 256; msgCnt += 4) {
      if (buildProtectedMacHex(candidate.key, targetAddr, frame.prefix, frame.tripCnt, frame.resetCnt, msgCnt) === frame.authHex) {
        matched = true;
        hit = msgCnt;
        break;
      }
    }
    if (matched) {
      protectedMatches += 1;
      msgCntHits.push(hit);
    }
  }
  const keyHash = crypto.createHash("sha256").update(candidate.key).digest("hex").slice(0, 16);
  return {
    key_sha256_16: keyHash,
    source: candidate.source,
    source_score: candidate.score,
    sync_matches: syncMatches,
    sync_checked: syncs.length,
    protected_matches: protectedMatches,
    protected_checked: protectedFrames.length,
    protected_msgcnt_hits_head: msgCntHits.slice(0, 12),
  };
}

function writeCsv(filePath, rows) {
  const headers = Object.keys(rows[0] || {
    key_sha256_16: "",
    source: "",
    source_score: "",
    sync_matches: "",
    sync_checked: "",
    protected_matches: "",
    protected_checked: "",
    protected_msgcnt_hits_head: "",
  });
  const quote = (value) => `"${String(value ?? "").replace(/"/g, '""')}"`;
  const lines = [headers.join(",")];
  for (const row of rows) lines.push(headers.map((h) => quote(Array.isArray(row[h]) ? row[h].join(" ") : row[h])).join(","));
  fs.writeFileSync(filePath, `${lines.join("\n")}\n`, "utf8");
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  fs.mkdirSync(args.outputDir, { recursive: true });
  const candidates = [
    ...loadCandidateKeyFiles(args.candidateKeyFiles),
    ...loadCandidates(args.candidateCsvs, args.maxCandidates),
  ].slice(0, args.maxCandidates);
  const { syncs, protectedFrames } = await collectFrames(args.logs, args.targetAddr, args.bus, args.maxSync, args.maxProtected);
  const results = candidates
    .map((candidate) => probeCandidate(candidate, syncs, protectedFrames, args.targetAddr))
    .sort((a, b) => (b.sync_matches - a.sync_matches) || (b.protected_matches - a.protected_matches));

  const payload = {
    settings: args,
    candidates_loaded: candidates.length,
    sync_checked: syncs.length,
    protected_checked: protectedFrames.length,
    top_results: results.slice(0, 50),
  };
  const jsonPath = path.join(args.outputDir, "secoc_key_probe_results.json");
  const csvPath = path.join(args.outputDir, "secoc_key_probe_results.csv");
  const mdPath = path.join(args.outputDir, "secoc_key_probe_report.md");
  fs.writeFileSync(jsonPath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
  writeCsv(csvPath, results.slice(0, 100));

  const best = results[0];
  const lines = [
    "# SecOC Key Probe",
    "",
    `Candidates loaded: \`${candidates.length}\``,
    `Sync frames checked: \`${syncs.length}\``,
    `Protected frames checked: \`${protectedFrames.length}\``,
    "",
    "Candidate keys are redacted in this report; `key_sha256_16` is a short SHA-256 fingerprint of the 16-byte candidate.",
    "",
    "## Best Result",
    "",
    best
      ? `- key hash \`${best.key_sha256_16}\`, sync \`${best.sync_matches}/${best.sync_checked}\`, 0x2E4 \`${best.protected_matches}/${best.protected_checked}\`, source \`${best.source}\``
      : "- No candidates loaded.",
    "",
    "## Interpretation",
    "",
    "- A real key for the tested protected frame should match essentially all sampled protected frames.",
    "- Sync MAC is reported separately because the synchronization frame may use a different key/variant or a layout nuance not covered by this probe.",
    "- 0x2E4 protected matches try all 64 message-counter values compatible with the low 2-bit flag.",
    "",
    "## Outputs",
    "",
    `- \`${jsonPath}\``,
    `- \`${csvPath}\``,
  ];
  fs.writeFileSync(mdPath, `${lines.join("\n")}\n`, "utf8");

  console.log(`[INFO] candidates=${candidates.length} sync=${syncs.length} protected=${protectedFrames.length}`);
  if (best) console.log(`[INFO] best sync=${best.sync_matches}/${best.sync_checked} protected=${best.protected_matches}/${best.protected_checked} hash=${best.key_sha256_16}`);
  console.log(`[INFO] report=${mdPath}`);
}

main().catch((err) => {
  console.error(err.stack || err.message || err);
  process.exit(1);
});
