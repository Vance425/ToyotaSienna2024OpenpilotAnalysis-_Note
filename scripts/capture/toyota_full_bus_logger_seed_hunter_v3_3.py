#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toyota Full Bus Logger + Seed Hunter v3 (Dual writers)
- Writer A: continuous (no ignition segmentation), only size rotation
- Writer B: segmented by ignition state (IGN_ON/IGN_OFF/UNKNOWN), also size rotation
- Event log + seed CSV extraction

Outputs:
  <out>/toyota_all_YYYYmmdd_HHMMSS_###.ndjson              (continuous)
  <out>/toyota_seg_IGN_ON_YYYYmmdd_HHMMSS_###.ndjson       (segmented)
  <out>/toyota_seg_IGN_OFF_YYYYmmdd_HHMMSS_###.ndjson
  <out>/events.jsonl
  <out>/seed_key_pairs.csv
"""

import argparse
import atexit
import csv
import json
import os
import signal
import socket
import sys
import time
import uuid
from dataclasses import dataclass
from typing import Optional, List, Tuple

try:
    from panda import Panda
except Exception:
    print("ERROR: cannot import panda. Run on C3X/openpilot env.")
    raise


SCRIPT_VERSION = "toyota_full_bus_logger_seed_hunter_v3.3+sidecars+state-candidates+operation-hints"

ADDR_90 = 0x90
ADDR_116 = 0x116
ADDR_131 = 0x131
ADDR_191 = 0x191
ADDR_260 = 0x260
ADDR_2E4 = 0x2E4
ADDR_D5 = 0x0D5
ADDR_610 = 0x610
TOP_TIER_ZONE = "fff4"
EXIT_ZONE = "fff0"
CORRIDOR_ZONES = {"fff4", "fff0", "ffee", "ffeb", "ffe8", "ffe7"}
OPERATION_CLUSTER_GAP_MS = 1500
OPERATION_WINDOW_MS = 10 * 60 * 1000
OPERATION_PROFILE_DYNAMIC = "dynamic_compact_0509"
OPERATION_PROFILE_STEADY = "steady_bridge_0517"


def operation_kind(kind: Optional[str]) -> Optional[str]:
    if kind == "seed":
        return "seed"
    if kind == "ramp_top":
        return "ramp"
    if kind == "plateau_top":
        return "plateau"
    if kind == "exit_pair":
        return "exit"
    return None


def now_ms() -> int:
    return int(time.time() * 1000)


def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def write_json_file(path: str, obj: dict) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False, sort_keys=True)
        fh.write("\n")


def remove_file_quiet(path: Optional[str]) -> None:
    if not path:
        return
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def daemonize_if_needed(args) -> None:
    if args.foreground:
        return
    if os.name != "posix" or not hasattr(os, "fork"):
        return

    stdout_log = args.stdout_log or os.path.join(args.out, "logger_stdout.log")
    pid_file = args.pid_file or os.path.join(args.out, "logger.pid")
    ensure_dir(os.path.dirname(stdout_log))
    ensure_dir(os.path.dirname(pid_file))

    pid = os.fork()
    if pid > 0:
        print(f"[INFO] logger detached pid={pid} pid_file={pid_file} stdout_log={stdout_log}")
        os._exit(0)

    os.setsid()
    signal.signal(signal.SIGHUP, signal.SIG_IGN)

    pid = os.fork()
    if pid > 0:
        os._exit(0)

    os.chdir("/")
    os.umask(0o022)

    sys.stdout.flush()
    sys.stderr.flush()
    with open("/dev/null", "r", encoding="utf-8", errors="ignore") as stdin_fh:
        os.dup2(stdin_fh.fileno(), 0)
    with open(stdout_log, "a", encoding="utf-8") as out_fh:
        os.dup2(out_fh.fileno(), 1)
        os.dup2(out_fh.fileno(), 2)

    with open(pid_file, "w", encoding="utf-8") as pid_fh:
        pid_fh.write(str(os.getpid()) + "\n")
    atexit.register(remove_file_quiet, pid_file)


def make_session_id() -> str:
    ts = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    return f"{ts}_{socket.gethostname()}_{os.getpid()}_{uuid.uuid4().hex[:8]}"


def hex_bytes(b: bytes) -> str:
    return b.hex()


def parse_int_auto(x: str) -> int:
    x = x.strip().lower()
    if x.startswith("0x"):
        return int(x, 16)
    return int(x, 10)


def s16le(buf: bytes, idx: int) -> int:
    v = buf[idx] | (buf[idx + 1] << 8)
    return v - 65536 if v & 0x8000 else v


def s16be(buf: bytes, idx: int) -> int:
    v = (buf[idx] << 8) | buf[idx + 1]
    return v - 65536 if v & 0x8000 else v


def u16be(buf: bytes, idx: int) -> int:
    return (buf[idx] << 8) | buf[idx + 1]


def s8(v: int) -> int:
    return v - 256 if v >= 128 else v


def control_from_260(buf: bytes) -> Optional[int]:
    if len(buf) < 6:
        return None
    fine = s16le(buf, 2)
    control = fine + (s8(buf[5]) << 8)
    if buf[1] == 0xFF:
        control = -control
    return control


@dataclass
class RotationConfig:
    rotate_bytes: int
    keep_files: int


class RotatingNDJSONWriter:
    def __init__(self, out_dir: str, prefix: str, rotation: RotationConfig):
        self.out_dir = out_dir
        self.prefix = prefix
        self.rotation = rotation
        self._fh = None
        self._bytes_written = 0
        self._index = 0
        self.current_path = None
        self.current_file_index = None
        self.current_open_ts_ms = None
        ensure_dir(self.out_dir)

    def open_new(self):
        if self._fh:
            try:
                self._fh.flush()
                os.fsync(self._fh.fileno())
            except Exception:
                pass
            self._fh.close()

        ts = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        file_index = self._index
        path = os.path.join(self.out_dir, f"{self.prefix}_{ts}_{file_index:03d}.ndjson")
        self._fh = open(path, "a", buffering=1)
        self._bytes_written = 0
        self.current_path = path
        self.current_file_index = file_index
        self.current_open_ts_ms = now_ms()
        self._index += 1
        self._cleanup_old_files()

    def _cleanup_old_files(self):
        if self.rotation.keep_files <= 0:
            return
        files = [f for f in os.listdir(self.out_dir) if f.startswith(self.prefix) and f.endswith(".ndjson")]
        files.sort()
        while len(files) > self.rotation.keep_files:
            rm = files.pop(0)
            try:
                os.remove(os.path.join(self.out_dir, rm))
            except Exception:
                break

    def write_obj(self, obj: dict):
        if not self._fh:
            self.open_new()
        line = json.dumps(obj, separators=(",", ":"), ensure_ascii=False) + "\n"
        b = line.encode("utf-8")
        self._fh.write(line)
        self._bytes_written += len(b)
        if self.rotation.rotate_bytes > 0 and self._bytes_written >= self.rotation.rotate_bytes:
            self.open_new()

    def close(self):
        if self._fh:
            try:
                self._fh.flush()
                os.fsync(self._fh.fileno())
            except Exception:
                pass
            self._fh.close()
            self._fh = None
            self.current_path = None
            self.current_file_index = None
            self.current_open_ts_ms = None


class SeedCSVWriter:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        ensure_dir(os.path.dirname(csv_path))
        self._fh = open(self.csv_path, "a", newline="")
        self._w = csv.writer(self._fh)
        if os.path.getsize(self.csv_path) == 0:
            self._w.writerow([
                "ts_ms", "bus", "rx_addr", "raw_hex",
                "iso_tp", "service", "subfn_or_level", "seed_hex"
            ])
            self._fh.flush()

    def append(self, row: List):
        self._w.writerow(row)
        self._fh.flush()

    def close(self):
        try:
            self._fh.flush()
        except Exception:
            pass
        self._fh.close()


class EventWriter:
    def __init__(self, path: str):
        self.path = path
        ensure_dir(os.path.dirname(path))
        self._fh = open(self.path, "a", buffering=1)

    def write(self, obj: dict):
        self._fh.write(json.dumps(obj, separators=(",", ":"), ensure_ascii=False) + "\n")

    def close(self):
        try:
            self._fh.flush()
        except Exception:
            pass
        self._fh.close()


@dataclass
class FileStats:
    stream: str
    prefix: str
    path: str
    file_index: Optional[int]
    open_ts_ms: int
    first_frame_ts_ms: Optional[int] = None
    last_frame_ts_ms: Optional[int] = None
    first_frame_seq: Optional[int] = None
    last_frame_seq: Optional[int] = None
    frame_count: int = 0
    bus_counts: Optional[dict] = None

    def ingest(self, row: dict) -> None:
        if self.bus_counts is None:
            self.bus_counts = {}
        ts_ms = int(row["ts_ms"])
        frame_seq = int(row["frame_seq"])
        bus = str(int(row["bus"]))
        if self.first_frame_ts_ms is None:
            self.first_frame_ts_ms = ts_ms
            self.first_frame_seq = frame_seq
        self.last_frame_ts_ms = ts_ms
        self.last_frame_seq = frame_seq
        self.frame_count += 1
        self.bus_counts[bus] = self.bus_counts.get(bus, 0) + 1


class FileIndexWriter:
    def __init__(self, path: str):
        self.writer = EventWriter(path)

    def opened(self, stats: FileStats, reason: str, segment_id: Optional[str] = None, segment_state: Optional[str] = None) -> None:
        self.writer.write({
            "type": "file_opened",
            "ts_ms": stats.open_ts_ms,
            "stream": stats.stream,
            "prefix": stats.prefix,
            "path": stats.path,
            "file_index": stats.file_index,
            "reason": reason,
            "segment_id": segment_id,
            "segment_state": segment_state,
        })

    def closed(self, stats: Optional[FileStats], reason: str, close_ts_ms: Optional[int] = None) -> None:
        if stats is None:
            return
        path = stats.path
        size_bytes = None
        try:
            size_bytes = os.path.getsize(path)
        except Exception:
            pass
        self.writer.write({
            "type": "file_closed",
            "ts_ms": close_ts_ms or now_ms(),
            "stream": stats.stream,
            "prefix": stats.prefix,
            "path": path,
            "file_index": stats.file_index,
            "reason": reason,
            "open_ts_ms": stats.open_ts_ms,
            "first_frame_ts_ms": stats.first_frame_ts_ms,
            "last_frame_ts_ms": stats.last_frame_ts_ms,
            "first_frame_seq": stats.first_frame_seq,
            "last_frame_seq": stats.last_frame_seq,
            "frame_count": stats.frame_count,
            "bus_counts": stats.bus_counts or {},
            "size_bytes": size_bytes,
        })

    def close(self) -> None:
        self.writer.close()


class AnalysisStateTracker:
    def __init__(self):
        self.latest_131: Optional[Tuple[int, str]] = None
        self.latest_260: Optional[Tuple[int, str, Optional[int], str]] = None
        self.latest_191: Optional[Tuple[int, int, int, str]] = None
        self.latest_90: Optional[tuple] = None
        self.latest_610: Optional[tuple] = None
        self.latest_d5: Optional[Tuple[int, int, str]] = None
        self.latest_116: Optional[dict] = None
        self.last_2e4_ts_ms = 0
        self._last_timeline_ts_ms = 0
        self.lifecycle_recent_events: List[dict] = []
        self.lifecycle_clusters: List[dict] = []

    def _prune_operation_history(self, ts_ms: int) -> None:
        cutoff = ts_ms - OPERATION_WINDOW_MS
        self.lifecycle_recent_events = [
            ev for ev in self.lifecycle_recent_events
            if int(ev.get("ts_ms", 0)) >= cutoff
        ][-128:]
        self.lifecycle_clusters = [
            cluster for cluster in self.lifecycle_clusters
            if int(cluster.get("end_ts_ms", 0)) >= cutoff
        ][-64:]

    def _compact_cluster(self, cluster: dict) -> dict:
        return {
            "kind": cluster.get("kind"),
            "raw_kind": cluster.get("raw_kind"),
            "start_ts_ms": cluster.get("start_ts_ms"),
            "end_ts_ms": cluster.get("end_ts_ms"),
            "count": cluster.get("count"),
            "first_phase_hex": cluster.get("first_phase_hex"),
            "last_phase_hex": cluster.get("last_phase_hex"),
            "max_phase_sum": cluster.get("max_phase_sum"),
            "family_pair": cluster.get("family_pair"),
            "segment_id": cluster.get("segment_id"),
            "segment_index": cluster.get("segment_index"),
            "segment_path": cluster.get("segment_path"),
        }

    def _chain_from_seed_index(self, seed_idx: int) -> List[dict]:
        targets = ["seed", "ramp", "plateau", "exit"]
        target_idx = 0
        chain = []
        for cluster in self.lifecycle_clusters[seed_idx:]:
            if cluster.get("kind") == targets[target_idx]:
                chain.append(cluster)
                target_idx += 1
                if target_idx >= len(targets):
                    break
        return chain

    def _chain_gaps_s(self, chain: List[dict]) -> List[float]:
        gaps_s = []
        for prev, cur in zip(chain, chain[1:]):
            gaps_s.append(round((int(cur["start_ts_ms"]) - int(prev["end_ts_ms"])) / 1000.0, 3))
        return gaps_s

    def _best_recent_chain(self) -> List[dict]:
        best_chain: List[dict] = []
        best_score = None
        for idx, cluster in enumerate(self.lifecycle_clusters):
            if cluster.get("kind") != "seed":
                continue
            chain = self._chain_from_seed_index(idx)
            if not chain:
                continue
            gaps_s = self._chain_gaps_s(chain)
            max_gap_s = max(gaps_s) if gaps_s else 0.0
            total_gap_s = sum(gaps_s) if gaps_s else 0.0
            has_full_chain = [c.get("kind") for c in chain] == ["seed", "ramp", "plateau", "exit"]
            ramp_max = chain[1].get("max_phase_sum") if len(chain) >= 2 else None
            plateau_max = chain[2].get("max_phase_sum") if len(chain) >= 3 else None
            exit_phase = chain[3].get("first_phase_hex") if len(chain) >= 4 else None
            dynamic_like = (
                has_full_chain and ramp_max is not None and plateau_max is not None and
                ramp_max >= 100 and 140 <= plateau_max <= 153 and exit_phase == "0000" and max_gap_s <= 90
            )
            steady_like = (
                has_full_chain and ramp_max is not None and plateau_max is not None and
                ramp_max <= 25 and 150 <= plateau_max <= 165 and exit_phase == "0000" and 75 < max_gap_s <= 300
            )
            # Prefer full reference-like chains, then fuller/later chains. This avoids
            # losing a real cross-file chain when a short seed/ramp appears before exit.
            score = (
                4 if dynamic_like else 3 if steady_like else 2 if has_full_chain else 1,
                len(chain),
                -max_gap_s,
                -total_gap_s,
                int(chain[-1].get("end_ts_ms", 0)),
            )
            if best_score is None or score > best_score:
                best_score = score
                best_chain = chain
        return best_chain

    def _operation_profile_hints(self, ts_ms: int) -> dict:
        self._prune_operation_history(ts_ms)
        chain = self._best_recent_chain()
        cluster_path = [cluster.get("kind") for cluster in self.lifecycle_clusters[-8:]]
        chain_path = [cluster.get("kind") for cluster in chain]
        chain_phase_path = [cluster.get("first_phase_hex") for cluster in chain]
        chain_phase_last_path = [cluster.get("last_phase_hex") for cluster in chain]
        chain_phase_max_sums = [cluster.get("max_phase_sum") for cluster in chain]

        gaps_s = self._chain_gaps_s(chain)
        max_gap_s = max(gaps_s) if gaps_s else None

        has_full_chain = chain_path == ["seed", "ramp", "plateau", "exit"]
        ramp_max = chain[1].get("max_phase_sum") if len(chain) >= 2 else None
        plateau_max = chain[2].get("max_phase_sum") if len(chain) >= 3 else None
        exit_phase = chain[3].get("first_phase_hex") if len(chain) >= 4 else None
        dynamic_like = bool(
            has_full_chain and ramp_max is not None and plateau_max is not None and
            ramp_max >= 100 and 140 <= plateau_max <= 153 and exit_phase == "0000"
        )
        steady_like = bool(
            has_full_chain and ramp_max is not None and plateau_max is not None and
            ramp_max <= 25 and 150 <= plateau_max <= 165 and exit_phase == "0000"
        )
        dynamic_partial = bool(len(chain) >= 2 and ramp_max is not None and ramp_max >= 100)
        steady_partial = bool(len(chain) >= 2 and ramp_max is not None and ramp_max <= 25)

        classification = "no_seed_chain"
        best_profile = None
        if has_full_chain:
            if dynamic_like and max_gap_s is not None and max_gap_s <= 90:
                classification = "dynamic_compact_candidate"
                best_profile = OPERATION_PROFILE_DYNAMIC
            elif steady_like and max_gap_s is not None and 75 < max_gap_s <= 300:
                classification = "steady_bridge_candidate"
                best_profile = OPERATION_PROFILE_STEADY
            elif max_gap_s is not None and max_gap_s > 300:
                classification = "too_loose_full_chain"
            elif max_gap_s is not None and max_gap_s <= 90:
                classification = "compact_full_chain_unknown_profile"
            else:
                classification = "bridge_full_chain_unknown_profile"
        elif chain_path:
            classification = "partial_" + "_".join(chain_path)

        latest_seed_idx = None
        for idx in range(len(self.lifecycle_clusters) - 1, -1, -1):
            if self.lifecycle_clusters[idx].get("kind") == "seed":
                latest_seed_idx = idx
                break
        reverse_trap = False
        preamble_kinds = []
        if latest_seed_idx is not None:
            seed = self.lifecycle_clusters[latest_seed_idx]
            for cluster in self.lifecycle_clusters[max(0, latest_seed_idx - 4):latest_seed_idx]:
                gap_ms = int(seed["start_ts_ms"]) - int(cluster["end_ts_ms"])
                if 0 <= gap_ms <= 30000 and cluster.get("kind") in ("ramp", "plateau", "exit"):
                    reverse_trap = True
                    preamble_kinds.append(cluster.get("kind"))

        return {
            "classification_hint": classification,
            "best_profile_hint": best_profile,
            "dynamic_compact_0509_candidate": bool(classification == "dynamic_compact_candidate"),
            "steady_bridge_0517_candidate": bool(classification == "steady_bridge_candidate"),
            "dynamic_compact_partial_possible": dynamic_partial and not has_full_chain,
            "steady_bridge_partial_possible": steady_partial and not has_full_chain,
            "reverse_preamble_trap_hint": reverse_trap,
            "reverse_preamble_kinds": preamble_kinds,
            "rolling_cluster_path": cluster_path,
            "active_chain_path": chain_path,
            "active_chain_phase_path_first": chain_phase_path,
            "active_chain_phase_path_last": chain_phase_last_path,
            "active_chain_phase_max_sums": chain_phase_max_sums,
            "active_chain_gaps_s": gaps_s,
            "active_chain_max_gap_s": max_gap_s,
            "recent_clusters": [self._compact_cluster(c) for c in self.lifecycle_clusters[-6:]],
        }

    def _record_lifecycle_event(self, event: dict) -> dict:
        ts_ms = int(event["ts_ms"])
        raw_kind = event.get("kind")
        kind = operation_kind(raw_kind)
        self.lifecycle_recent_events.append({
            "ts_ms": ts_ms,
            "raw_kind": raw_kind,
            "kind": kind,
            "phase_hex": event.get("phase_hex"),
            "phase_sum": event.get("phase_sum"),
            "family131": event.get("family131"),
            "family260": event.get("family260"),
            "segment_id": event.get("segment_id"),
            "segment_index": event.get("segment_index"),
            "segment_path": event.get("segment_path"),
        })
        if kind:
            last = self.lifecycle_clusters[-1] if self.lifecycle_clusters else None
            if (
                last and last.get("kind") == kind and
                ts_ms - int(last.get("end_ts_ms", ts_ms)) <= OPERATION_CLUSTER_GAP_MS
            ):
                last["end_ts_ms"] = ts_ms
                last["count"] = int(last.get("count", 0)) + 1
                last["raw_kind"] = raw_kind
                last["last_phase_hex"] = event.get("phase_hex")
                last["max_phase_sum"] = max(
                    int(last.get("max_phase_sum") or 0),
                    int(event.get("phase_sum") or 0),
                )
                last["family_pair"] = "%s|%s" % (event.get("family131"), event.get("family260"))
                last["segment_id"] = event.get("segment_id")
                last["segment_index"] = event.get("segment_index")
                last["segment_path"] = event.get("segment_path")
            else:
                self.lifecycle_clusters.append({
                    "kind": kind,
                    "raw_kind": raw_kind,
                    "start_ts_ms": ts_ms,
                    "end_ts_ms": ts_ms,
                    "count": 1,
                    "first_phase_hex": event.get("phase_hex"),
                    "last_phase_hex": event.get("phase_hex"),
                    "max_phase_sum": int(event.get("phase_sum") or 0),
                    "family_pair": "%s|%s" % (event.get("family131"), event.get("family260")),
                    "segment_id": event.get("segment_id"),
                    "segment_index": event.get("segment_index"),
                    "segment_path": event.get("segment_path"),
                })
        return self._operation_profile_hints(ts_ms)

    def _latest_vehicle_state_candidates(self, ts_ms: int) -> dict:
        latest_90 = None
        if self.latest_90:
            latest_90 = {
                "ts_ms": self.latest_90[0],
                "b01_s16be": self.latest_90[1],
                "b01_u16be": self.latest_90[4],
                "b45_s16be": self.latest_90[2],
                "raw_data": self.latest_90[3],
                "age_ms": ts_ms - self.latest_90[0],
            }
        latest_610 = None
        if self.latest_610:
            latest_610 = {
                "ts_ms": self.latest_610[0],
                "b01_s16be": self.latest_610[1],
                "b12_s16be": self.latest_610[2],
                "b23_s16be": self.latest_610[3],
                "b23_u16be": self.latest_610[10],
                "b34_s16be": self.latest_610[4],
                "b45_s16be": self.latest_610[5],
                "b56_s16be": self.latest_610[6],
                "b56_u16be_centered_32768": self.latest_610[7],
                "b56_u16be": self.latest_610[11],
                "b67_s16be": self.latest_610[8],
                "raw_data": self.latest_610[9],
                "age_ms": ts_ms - self.latest_610[0],
            }
        latest_d5 = None
        if self.latest_d5:
            latest_d5 = {
                "ts_ms": self.latest_d5[0],
                "speed_ref_u16be_b1_2": self.latest_d5[1],
                "raw_data": self.latest_d5[2],
                "age_ms": ts_ms - self.latest_d5[0],
            }

        motion_state_hint = "unknown"
        if self.latest_d5 and self.latest_d5[1] not in (0, 0xFFFF):
            motion_state_hint = "speed_ref_candidate_d5"
        elif self.latest_90 and abs(self.latest_90[1]) >= 350:
            motion_state_hint = "motion_candidate_0x90"
        elif self.latest_90:
            motion_state_hint = "low_or_unknown_motion_candidate_0x90"

        return {
            "motion_state_hint": motion_state_hint,
            "latest_90": latest_90,
            "latest_610": latest_610,
            "latest_d5": latest_d5,
        }

    def ingest(self, row: dict, state: str, segment_id: str, segment_index: int) -> Optional[dict]:
        if int(row.get("bus", -1)) != 0:
            return None
        addr = int(row["addr"])
        ts_ms = int(row["ts_ms"])
        data_hex = str(row["data"])
        try:
            data = bytes.fromhex(data_hex)
        except Exception:
            return None

        if addr == ADDR_131 and len(data) >= 4:
            self.latest_131 = (ts_ms, data[2:4].hex())
            return None

        if addr == ADDR_260 and len(data) >= 5:
            control = control_from_260(data)
            self.latest_260 = (ts_ms, data[3:5].hex(), control, data_hex)
            return None

        if addr == ADDR_191 and len(data) >= 8:
            self.latest_191 = (ts_ms, s16le(data, 4), s16be(data, 6), data_hex)
            return None

        if addr == ADDR_90 and len(data) >= 2:
            b45 = s16be(data, 4) if len(data) >= 6 else None
            self.latest_90 = (ts_ms, s16be(data, 0), b45, data_hex, u16be(data, 0))
            return None

        if addr == ADDR_610 and len(data) >= 8:
            b23_u16 = u16be(data, 2)
            b56_u16 = u16be(data, 5)
            self.latest_610 = (
                ts_ms,
                s16be(data, 0),
                s16be(data, 1),
                s16be(data, 2),
                s16be(data, 3),
                s16be(data, 4),
                s16be(data, 5),
                b56_u16 - 32768,
                s16be(data, 6),
                data_hex,
                b23_u16,
                b56_u16,
            )
            return None

        if addr == ADDR_D5 and len(data) >= 3:
            self.latest_d5 = (ts_ms, u16be(data, 1), data_hex)
            return None

        if addr == ADDR_2E4:
            self.last_2e4_ts_ms = ts_ms
            return None

        if addr != ADDR_116 or len(data) < 2:
            return None

        family131 = None
        family260 = None
        control260 = None
        data260 = None
        if self.latest_131 and ts_ms - self.latest_131[0] <= 250:
            family131 = self.latest_131[1]
        if self.latest_260 and ts_ms - self.latest_260[0] <= 250:
            family260 = self.latest_260[1]
            control260 = self.latest_260[2]
            data260 = self.latest_260[3]
        phase_hex = data[0:2].hex()
        phase_sum = int(data[0]) + int(data[1])

        kind = None
        if family131 == TOP_TIER_ZONE and family260 == TOP_TIER_ZONE and phase_hex == "0000":
            kind = "seed"
        elif family131 == TOP_TIER_ZONE and family260 == TOP_TIER_ZONE and 1 <= phase_sum < 130:
            kind = "ramp_top"
        elif family131 == TOP_TIER_ZONE and family260 == TOP_TIER_ZONE and phase_sum >= 130:
            kind = "plateau_top"
        elif family131 == TOP_TIER_ZONE and family260 == EXIT_ZONE:
            kind = "exit_pair"
        elif family131 in CORRIDOR_ZONES and family260 in CORRIDOR_ZONES:
            kind = "corridor"

        self.latest_116 = {
            "ts_ms": ts_ms,
            "phase_hex": phase_hex,
            "phase_sum": phase_sum,
            "family131": family131,
            "family260": family260,
            "kind": kind,
            "raw_data": data_hex,
        }

        if not kind:
            return None

        companion = None
        if self.latest_191 and ts_ms - self.latest_191[0] <= 100:
            companion = {
                "ts_ms": self.latest_191[0],
                "b45_s16le": self.latest_191[1],
                "b67_s16be": self.latest_191[2],
                "raw_data": self.latest_191[3],
            }

        event = {
            "type": "protected_lifecycle_event",
            "ts_ms": ts_ms,
            "session_id": row.get("session_id"),
            "frame_seq": row.get("frame_seq"),
            "recv_batch_seq": row.get("recv_batch_seq"),
            "state": state,
            "segment_id": segment_id,
            "segment_index": segment_index,
            "segment_path": row.get("segment_path"),
            "kind": kind,
            "phase_hex": phase_hex,
            "phase_sum": phase_sum,
            "family131": family131,
            "family260": family260,
            "raw_116": data_hex,
            "control260": control260,
            "raw_260": data260,
            "companion191": companion,
            "vehicle_state_candidates": self._latest_vehicle_state_candidates(ts_ms),
        }
        event["operation_hints"] = self._record_lifecycle_event(event)
        return event

    def timeline_due(self, ts_ms: int, interval_ms: int) -> bool:
        if interval_ms <= 0:
            return False
        if self._last_timeline_ts_ms == 0 or ts_ms - self._last_timeline_ts_ms >= interval_ms:
            self._last_timeline_ts_ms = ts_ms
            return True
        return False

    def snapshot(self, ts_ms: int, session_id: str, state: str, segment_id: str, segment_index: int,
                 segment_path: Optional[str], msg_count: int, frame_seq: int, recv_batch_seq: int,
                 bus_counts: dict, current_rate: Optional[float]) -> dict:
        latest_131 = None
        if self.latest_131:
            latest_131 = {"ts_ms": self.latest_131[0], "family": self.latest_131[1], "age_ms": ts_ms - self.latest_131[0]}
        latest_260 = None
        if self.latest_260:
            latest_260 = {
                "ts_ms": self.latest_260[0],
                "family": self.latest_260[1],
                "control": self.latest_260[2],
                "raw_data": self.latest_260[3],
                "age_ms": ts_ms - self.latest_260[0],
            }
        latest_191 = None
        if self.latest_191:
            latest_191 = {
                "ts_ms": self.latest_191[0],
                "b45_s16le": self.latest_191[1],
                "b67_s16be": self.latest_191[2],
                "raw_data": self.latest_191[3],
                "age_ms": ts_ms - self.latest_191[0],
            }
        latest_116 = None
        if self.latest_116:
            latest_116 = dict(self.latest_116)
            latest_116["age_ms"] = ts_ms - int(self.latest_116["ts_ms"])
        vehicle_state_candidates = self._latest_vehicle_state_candidates(ts_ms)
        operation_state_hints = self._operation_profile_hints(ts_ms)
        return {
            "type": "state_timeline",
            "ts_ms": ts_ms,
            "session_id": session_id,
            "state": state,
            "segment_id": segment_id,
            "segment_index": segment_index,
            "segment_path": segment_path,
            "msg_count": msg_count,
            "frame_seq": frame_seq,
            "recv_batch_seq": recv_batch_seq,
            "current_rate_hz": current_rate,
            "bus_counts_total": bus_counts,
            "latest_116": latest_116,
            "latest_131": latest_131,
            "latest_260": latest_260,
            "latest_191": latest_191,
            "vehicle_state_candidates": vehicle_state_candidates,
            "operation_state_hints": operation_state_hints,
            "last_2e4_age_ms": None if not self.last_2e4_ts_ms else ts_ms - self.last_2e4_ts_ms,
        }


class ManualMarkerReader:
    def __init__(self, path: str):
        self.path = path
        ensure_dir(os.path.dirname(path))
        if not os.path.exists(path):
            with open(path, "a", encoding="utf-8"):
                pass
        self._offset = os.path.getsize(path)

    def poll(self) -> List[dict]:
        out = []
        with open(self.path, "r", encoding="utf-8") as fh:
            fh.seek(self._offset)
            while True:
                line = fh.readline()
                if not line:
                    break
                self._offset = fh.tell()
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        out.append(obj)
                        continue
                except Exception:
                    pass
                out.append({"label": line})
        return out


# -------- UDS / ISO-TP (minimal, single-frame only) --------
def isotp_send(p: Panda, bus: int, tx_addr: int, payload: bytes) -> None:
    if len(payload) <= 7:
        pci = bytes([0x00 | len(payload)])
        data = (pci + payload).ljust(8, b"\x00")
        p.can_send(tx_addr, data, bus)
        return


def isotp_try_extract_seed_from_frame(data: bytes) -> Optional[Tuple[int, int, bytes]]:
    if len(data) != 8:
        return None
    pci = data[0]
    if ((pci >> 4) & 0x0F) != 0x0:
        return None
    ln = pci & 0x0F
    if ln < 3 or ln > 7:
        return None
    uds = data[1:1+ln]
    if len(uds) < 3:
        return None
    service, subfn, level = uds[0], uds[1], uds[2]
    if service == 0x67 and subfn == 0x27:
        return (service, level, uds[3:])
    return None


# -------- Ignition detector (rate-based) --------
class IgnitionDetector:
    def __init__(self, on_threshold: float, off_threshold: float, on_window: float, off_window: float):
        self.on_threshold = on_threshold
        self.off_threshold = off_threshold
        self.on_window = on_window
        self.off_window = off_window
        self.state = "UNKNOWN"
        self._bucket_start = time.time()
        self._bucket_count = 0
        self._history: List[Tuple[float, float]] = []

    def ingest_msgs(self, n: int) -> Optional[dict]:
        now = time.time()
        self._bucket_count += n

        if now - self._bucket_start >= 1.0:
            dt = now - self._bucket_start
            rate = self._bucket_count / max(dt, 1e-6)
            self._history.append((now, rate))
            self._history = [(t, r) for (t, r) in self._history if now - t <= 60.0]
            self._bucket_start = now
            self._bucket_count = 0

            avg_on = self._avg_over_window(now, self.on_window)
            avg_off = self._avg_over_window(now, self.off_window)

            prev = self.state

            if self.state == "UNKNOWN":
                if avg_on is not None and avg_on >= self.on_threshold:
                    self.state = "IGN_ON"
                elif avg_off is not None and avg_off <= self.off_threshold:
                    self.state = "IGN_OFF"
            else:
                if self.state != "IGN_ON" and avg_on is not None and avg_on >= self.on_threshold:
                    self.state = "IGN_ON"
                if self.state != "IGN_OFF" and avg_off is not None and avg_off <= self.off_threshold:
                    self.state = "IGN_OFF"

            if self.state != prev:
                return {
                    "type": "ignition_transition",
                    "ts_ms": now_ms(),
                    "from": prev,
                    "to": self.state,
                    "avg_on_rate": avg_on,
                    "avg_off_rate": avg_off,
                    "on_threshold": self.on_threshold,
                    "off_threshold": self.off_threshold,
                }
        return None

    def _avg_over_window(self, now: float, window: float) -> Optional[float]:
        if window <= 0:
            return None
        xs = [r for (t, r) in self._history if now - t <= window]
        if not xs:
            return None
        return sum(xs) / len(xs)


# -------- Main --------
stop_flag = False
def handle_sig(_sig, _frm):
    global stop_flag
    stop_flag = True


def main():
    ap = argparse.ArgumentParser()

    ap.add_argument("--out", default="/data/raw_can_logs", help="Output directory")
    ap.add_argument("--rotate-mb", type=int, default=200, help="Rotate per N MB (0=disable)")
    ap.add_argument("--keep-files", type=int, default=60, help="Keep last N files per prefix")
    ap.add_argument("--print-rate", type=float, default=2.0, help="Stats print interval (sec)")
    ap.add_argument("--foreground", action="store_true", help="Stay attached to current terminal instead of daemonizing")
    ap.add_argument("--pid-file", default=None, help="PID file path (default: <out>/logger.pid)")
    ap.add_argument("--stdout-log", default=None, help="Detached stdout/stderr log path (default: <out>/logger_stdout.log)")

    # continuous + segmented prefixes
    ap.add_argument("--prefix-all", default="toyota_all", help="Prefix for continuous logs")
    ap.add_argument("--prefix-seg", default="toyota_seg", help="Prefix for segmented logs")

    # ignition detection params
    ap.add_argument("--ign-on-threshold", type=float, default=250.0)
    ap.add_argument("--ign-off-threshold", type=float, default=20.0)
    ap.add_argument("--ign-on-window", type=float, default=3.0)
    ap.add_argument("--ign-off-window", type=float, default=6.0)

    ap.add_argument("--events", default=None)
    ap.add_argument("--csv", default=None)
    ap.add_argument("--manifest", default=None, help="Session manifest path (default: <out>/session_manifest.json)")
    ap.add_argument("--health-summary", default=None, help="Health summary path (default: <out>/health_summary.json)")
    ap.add_argument("--session-id", default=None, help="Optional externally supplied session id")
    ap.add_argument("--marker-queue", default=None, help="Path to manual marker queue jsonl/text file (default: <out>/manual_marker_queue.jsonl)")
    ap.add_argument("--file-index", default=None, help="File open/close index jsonl path (default: <out>/file_index.jsonl)")
    ap.add_argument("--state-timeline", default=None, help="Per-interval analysis state jsonl path (default: <out>/state_timeline.jsonl)")
    ap.add_argument("--lifecycle-events", default=None, help="Protected lifecycle event jsonl path (default: <out>/lifecycle_events.jsonl)")
    ap.add_argument("--state-interval", type=float, default=1.0, help="State timeline interval in seconds (0=disable)")
    ap.add_argument("--disable-sidecars", action="store_true", help="Disable file_index/state_timeline/lifecycle_events writers")

    # UDS probe (optional)
    ap.add_argument("--enable-uds", action="store_true")
    ap.add_argument("--uds-bus", type=int, default=1)
    ap.add_argument("--uds-tx", default="0x7E0")
    ap.add_argument("--uds-rx", default="0x7E8")
    ap.add_argument("--seed-levels", default="1")
    ap.add_argument("--uds-interval", type=float, default=2.0)

    ap.add_argument("--safety-off", action="store_true", help="Do NOT set Toyota safety mode (not recommended)")
    args = ap.parse_args()

    rotate_bytes = int(args.rotate_mb) * 1024 * 1024 if args.rotate_mb > 0 else 0
    rotation = RotationConfig(rotate_bytes=rotate_bytes, keep_files=int(args.keep_files))

    ensure_dir(args.out)
    daemonize_if_needed(args)
    if not args.events:
        args.events = os.path.join(args.out, "events.jsonl")
    if not args.csv:
        args.csv = os.path.join(args.out, "seed_key_pairs.csv")
    if not args.manifest:
        args.manifest = os.path.join(args.out, "session_manifest.json")
    if not args.health_summary:
        args.health_summary = os.path.join(args.out, "health_summary.json")
    if not args.marker_queue:
        args.marker_queue = os.path.join(args.out, "manual_marker_queue.jsonl")
    if not args.file_index:
        args.file_index = os.path.join(args.out, "file_index.jsonl")
    if not args.state_timeline:
        args.state_timeline = os.path.join(args.out, "state_timeline.jsonl")
    if not args.lifecycle_events:
        args.lifecycle_events = os.path.join(args.out, "lifecycle_events.jsonl")
    session_id = args.session_id or make_session_id()
    event_writer = EventWriter(args.events)
    seed_csv = SeedCSVWriter(args.csv)
    marker_reader = ManualMarkerReader(args.marker_queue)
    file_index_writer = None if args.disable_sidecars else FileIndexWriter(args.file_index)
    timeline_writer = None if args.disable_sidecars else EventWriter(args.state_timeline)
    lifecycle_writer = None if args.disable_sidecars else EventWriter(args.lifecycle_events)
    state_tracker = AnalysisStateTracker()

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    p = Panda()
    if not args.safety_off:
        try:
            p.set_safety_mode(Panda.SAFETY_TOYOTA)
        except Exception:
            try:
                p.set_safety_mode(0)
            except Exception:
                pass

    uds_tx = parse_int_auto(args.uds_tx)
    uds_rx = parse_int_auto(args.uds_rx)
    seed_levels = [int(x.strip()) for x in args.seed_levels.split(",") if x.strip()]

    ign = IgnitionDetector(
        on_threshold=float(args.ign_on_threshold),
        off_threshold=float(args.ign_off_threshold),
        on_window=float(args.ign_on_window),
        off_window=float(args.ign_off_window),
    )

    # Writer A: continuous
    writer_all = RotatingNDJSONWriter(args.out, args.prefix_all, rotation)
    writer_all.open_new()
    all_file_stats = FileStats(
        stream="continuous",
        prefix=args.prefix_all,
        path=writer_all.current_path,
        file_index=writer_all.current_file_index,
        open_ts_ms=writer_all.current_open_ts_ms or now_ms(),
    )
    if file_index_writer:
        file_index_writer.opened(all_file_stats, reason="start")

    # Writer B: segmented (prefix depends on state)
    current_state = "UNKNOWN"
    writer_seg = RotatingNDJSONWriter(args.out, f"{args.prefix_seg}_{current_state}", rotation)
    writer_seg.open_new()
    current_segment_index = 0
    current_segment_id = f"{session_id}:{current_state}:{current_segment_index:04d}"
    seg_file_stats = FileStats(
        stream="segmented",
        prefix=f"{args.prefix_seg}_{current_state}",
        path=writer_seg.current_path,
        file_index=writer_seg.current_file_index,
        open_ts_ms=writer_seg.current_open_ts_ms or now_ms(),
    )
    if file_index_writer:
        file_index_writer.opened(seg_file_stats, reason="start", segment_id=current_segment_id, segment_state=current_state)

    event_seq = 0

    def emit_event(obj: dict):
        nonlocal event_seq
        event_seq += 1
        enriched = {
            "session_id": session_id,
            "event_seq": event_seq,
            **obj,
        }
        event_writer.write(enriched)

    def new_file_stats(stream: str, writer: RotatingNDJSONWriter, reason: str,
                       segment_id: Optional[str] = None, segment_state: Optional[str] = None) -> FileStats:
        stats = FileStats(
            stream=stream,
            prefix=writer.prefix,
            path=writer.current_path,
            file_index=writer.current_file_index,
            open_ts_ms=writer.current_open_ts_ms or now_ms(),
        )
        if file_index_writer:
            file_index_writer.opened(stats, reason=reason, segment_id=segment_id, segment_state=segment_state)
        return stats

    def close_file_stats(stats: Optional[FileStats], reason: str, ts_ms: Optional[int] = None) -> None:
        if file_index_writer:
            file_index_writer.closed(stats, reason=reason, close_ts_ms=ts_ms)

    start_ts_ms = now_ms()
    manifest = {
        "session_id": session_id,
        "script": os.path.abspath(__file__),
        "script_version": SCRIPT_VERSION,
        "start_ts_ms": start_ts_ms,
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
        "out": args.out,
        "events": args.events,
        "csv": args.csv,
        "marker_queue": args.marker_queue,
        "file_index": args.file_index,
        "state_timeline": args.state_timeline,
        "lifecycle_events": args.lifecycle_events,
        "prefix_all": args.prefix_all,
        "prefix_seg": args.prefix_seg,
        "rotation": {
            "rotate_bytes": rotation.rotate_bytes,
            "keep_files": rotation.keep_files,
        },
        "uds": {
            "enabled": bool(args.enable_uds),
            "bus": int(args.uds_bus),
            "tx": hex(uds_tx),
            "rx": hex(uds_rx),
            "seed_levels": seed_levels,
            "interval_sec": float(args.uds_interval),
        },
        "ignition_detector": {
            "on_threshold": ign.on_threshold,
            "off_threshold": ign.off_threshold,
            "on_window": ign.on_window,
            "off_window": ign.off_window,
        },
        "sidecars": {
            "enabled": not bool(args.disable_sidecars),
            "state_interval_sec": float(args.state_interval),
            "file_index": args.file_index,
            "state_timeline": args.state_timeline,
            "lifecycle_events": args.lifecycle_events,
            "operation_hints": {
                "enabled": not bool(args.disable_sidecars),
                "cluster_gap_ms": OPERATION_CLUSTER_GAP_MS,
                "window_ms": OPERATION_WINDOW_MS,
                "profiles": [OPERATION_PROFILE_DYNAMIC, OPERATION_PROFILE_STEADY],
            },
        },
    }
    write_json_file(args.manifest, manifest)

    bus_counts = {}
    can_recv_error_count = 0
    uds_probe_count = 0
    seed_hit_count = 0
    recv_batch_seq = 0
    frame_seq = 0
    segment_files_opened = 1
    manual_marker_count = 0

    # drain old
    try:
        p.can_recv()
    except Exception:
        pass

    msg_count = 0
    last_print = time.time()
    last_uds = 0.0
    last_seen_seed_ts = 0

    emit_event({
        "type": "start",
        "ts_ms": start_ts_ms,
        "out": args.out,
        "prefix_all": args.prefix_all,
        "prefix_seg": args.prefix_seg,
        "uds_enabled": bool(args.enable_uds),
        "uds_bus": int(args.uds_bus),
        "uds_tx": hex(uds_tx),
        "uds_rx": hex(uds_rx),
        "ign_params": {
            "on_threshold": ign.on_threshold,
            "off_threshold": ign.off_threshold,
            "on_window": ign.on_window,
            "off_window": ign.off_window,
        }
    })
    emit_event({
        "type": "segment_opened",
        "ts_ms": start_ts_ms,
        "segment_id": current_segment_id,
        "segment_index": current_segment_index,
        "segment_state": current_state,
        "reason": "start",
        "path": writer_seg.current_path,
    })

    print(f"[INFO] Out: {args.out}")
    print(f"[INFO] Foreground: {bool(args.foreground)}")
    print(f"[INFO] Session ID: {session_id}")
    print(f"[INFO] Continuous prefix: {args.prefix_all}")
    print(f"[INFO] Segmented prefix:  {args.prefix_seg}_<STATE>")
    print(f"[INFO] Events: {args.events}")
    print(f"[INFO] Seed CSV: {args.csv}")
    print(f"[INFO] Marker queue: {args.marker_queue}")
    print(f"[INFO] Manifest: {args.manifest}")
    print(f"[INFO] Health summary: {args.health_summary}")
    print(f"[INFO] Sidecars: {'disabled' if args.disable_sidecars else 'enabled'}")
    if not args.disable_sidecars:
        print(f"[INFO] File index: {args.file_index}")
        print(f"[INFO] State timeline: {args.state_timeline} interval={args.state_interval}s")
        print(f"[INFO] Lifecycle events: {args.lifecycle_events}")
    print(f"[INFO] UDS probe: {'ENABLED' if args.enable_uds else 'disabled'}")
    print("[INFO] Ctrl+C to stop.")

    while not stop_flag:
        try:
            msgs = p.can_recv()
        except Exception as e:
            print(f"[WARN] can_recv error: {e}")
            can_recv_error_count += 1
            time.sleep(0.05)
            continue
        recv_batch_seq += 1
        batch_ts_ms = now_ms()

        # ignition transition
        ev = ign.ingest_msgs(len(msgs))
        if ev is not None:
            emit_event(ev)
            if ev.get("to") in ("IGN_ON", "IGN_OFF"):
                new_state = ev["to"]
                if new_state != current_state:
                    close_file_stats(seg_file_stats, reason="state_transition", ts_ms=batch_ts_ms)
                    current_state = new_state
                    writer_seg.close()
                    writer_seg = RotatingNDJSONWriter(args.out, f"{args.prefix_seg}_{current_state}", rotation)
                    writer_seg.open_new()
                    current_segment_index += 1
                    current_segment_id = f"{session_id}:{current_state}:{current_segment_index:04d}"
                    seg_file_stats = new_file_stats(
                        "segmented",
                        writer_seg,
                        reason="state_transition",
                        segment_id=current_segment_id,
                        segment_state=current_state,
                    )
                    segment_files_opened += 1
                    emit_event({
                        "type": "segment_opened",
                        "ts_ms": batch_ts_ms,
                        "segment_id": current_segment_id,
                        "segment_index": current_segment_index,
                        "segment_state": current_state,
                        "reason": "state_transition",
                        "path": writer_seg.current_path,
                    })
                    print(f"[EVENT] ignition -> {current_state} (segmented new file started)")

        for (addr, dat, bus) in msgs:
            frame_seq += 1
            bus_counts[int(bus)] = bus_counts.get(int(bus), 0) + 1
            base = {
                "ts_ms": batch_ts_ms,
                "session_id": session_id,
                "frame_seq": frame_seq,
                "recv_batch_seq": recv_batch_seq,
                "batch_ts_ms": batch_ts_ms,
                "bus": int(bus),
                "addr": int(addr),
                "data": hex_bytes(dat),
            }
            # continuous stream
            before_all_path = writer_all.current_path
            writer_all.write_obj(base)
            all_file_stats.ingest(base)
            if writer_all.current_path != before_all_path:
                close_file_stats(all_file_stats, reason="rotate", ts_ms=batch_ts_ms)
                all_file_stats = new_file_stats("continuous", writer_all, reason="rotate")

            # segmented stream includes state field
            seg_obj = dict(base)
            seg_obj["state"] = current_state
            seg_obj["segment_id"] = current_segment_id
            seg_obj["segment_index"] = current_segment_index
            seg_obj["segment_state"] = current_state
            seg_obj["segment_path"] = os.path.basename(writer_seg.current_path) if writer_seg.current_path else None
            before_seg_path = writer_seg.current_path
            writer_seg.write_obj(seg_obj)
            seg_file_stats.ingest(seg_obj)
            if lifecycle_writer or timeline_writer:
                lifecycle_event = state_tracker.ingest(seg_obj, current_state, current_segment_id, current_segment_index)
                if lifecycle_writer and lifecycle_event:
                    lifecycle_writer.write(lifecycle_event)
            if writer_seg.current_path != before_seg_path:
                close_file_stats(seg_file_stats, reason="rotate", ts_ms=batch_ts_ms)
                current_segment_index += 1
                current_segment_id = f"{session_id}:{current_state}:{current_segment_index:04d}"
                seg_file_stats = new_file_stats(
                    "segmented",
                    writer_seg,
                    reason="rotate",
                    segment_id=current_segment_id,
                    segment_state=current_state,
                )
                segment_files_opened += 1
                emit_event({
                    "type": "segment_opened",
                    "ts_ms": batch_ts_ms,
                    "segment_id": current_segment_id,
                    "segment_index": current_segment_index,
                    "segment_state": current_state,
                    "reason": "rotate",
                    "path": writer_seg.current_path,
                })

            msg_count += 1

            # seed extraction
            if int(addr) == uds_rx:
                parsed = isotp_try_extract_seed_from_frame(dat)
                if parsed is not None:
                    service, level, seed = parsed
                    seed_csv.append([
                        base["ts_ms"], int(bus), hex(int(addr)), base["data"],
                        "SF", hex(service), int(level), seed.hex()
                    ])
                    last_seen_seed_ts = base["ts_ms"]
                    seed_hit_count += 1

        t = time.time()
        if timeline_writer and state_tracker.timeline_due(batch_ts_ms, int(float(args.state_interval) * 1000)):
            current_rate = ign._history[-1][1] if getattr(ign, "_history", None) else None
            timeline_writer.write(state_tracker.snapshot(
                ts_ms=batch_ts_ms,
                session_id=session_id,
                state=current_state,
                segment_id=current_segment_id,
                segment_index=current_segment_index,
                segment_path=os.path.basename(writer_seg.current_path) if writer_seg.current_path else None,
                msg_count=msg_count,
                frame_seq=frame_seq,
                recv_batch_seq=recv_batch_seq,
                bus_counts=bus_counts,
                current_rate=current_rate,
            ))
        if (t - last_print) >= float(args.print_rate):
            print(f"[STAT] state={current_state} msgs={msg_count} last_seed_ts_ms={last_seen_seed_ts}")
            last_print = t

        # optional UDS probes (only when IGN_ON)
        if args.enable_uds and (t - last_uds) >= float(args.uds_interval):
            if current_state == "IGN_ON":
                for level in seed_levels:
                    payload = bytes([0x27, level & 0xFF])
                    isotp_send(p, int(args.uds_bus), uds_tx, payload)
                    uds_probe_count += 1
                    time.sleep(0.05)
            last_uds = t

        for marker in marker_reader.poll():
            marker_ts_ms = now_ms()
            emit_event({
                "type": "manual_marker",
                "ts_ms": marker_ts_ms,
                "state": current_state,
                "segment_id": current_segment_id,
                "segment_index": current_segment_index,
                "marker_label": marker.get("label") or marker.get("type") or "MANUAL",
                "marker_note": marker.get("note"),
                "marker_meta": marker.get("meta"),
                "raw_marker": marker,
            })
            manual_marker_count += 1

        if not msgs:
            time.sleep(0.005)

    stop_ts_ms = now_ms()
    emit_event({"type": "stop", "ts_ms": stop_ts_ms, "msgs": msg_count})
    close_file_stats(all_file_stats, reason="stop", ts_ms=stop_ts_ms)
    close_file_stats(seg_file_stats, reason="stop", ts_ms=stop_ts_ms)
    health_summary = {
        "session_id": session_id,
        "script_version": SCRIPT_VERSION,
        "start_ts_ms": start_ts_ms,
        "stop_ts_ms": stop_ts_ms,
        "duration_ms": stop_ts_ms - start_ts_ms,
        "out": args.out,
        "events": args.events,
        "csv": args.csv,
        "manifest": args.manifest,
        "file_index": args.file_index,
        "state_timeline": args.state_timeline,
        "lifecycle_events": args.lifecycle_events,
        "sidecars_enabled": not bool(args.disable_sidecars),
        "msg_count": msg_count,
        "recv_batch_count": recv_batch_seq,
        "frame_seq_last": frame_seq,
        "bus_counts": bus_counts,
        "can_recv_error_count": can_recv_error_count,
        "uds_probe_count": uds_probe_count,
        "seed_hit_count": seed_hit_count,
        "segment_files_opened": segment_files_opened,
        "manual_marker_count": manual_marker_count,
        "last_seen_seed_ts_ms": last_seen_seed_ts,
        "final_state": current_state,
    }
    write_json_file(args.health_summary, health_summary)
    print("[INFO] Stopping, flushing files...")
    for w in (writer_all, writer_seg):
        try:
            w.close()
        except Exception:
            pass
    try:
        seed_csv.close()
    except Exception:
        pass
    try:
        event_writer.close()
    except Exception:
        pass
    for sidecar in (file_index_writer, timeline_writer, lifecycle_writer):
        try:
            if sidecar:
                sidecar.close()
        except Exception:
            pass
    print("[INFO] Done.")


if __name__ == "__main__":
    main()
