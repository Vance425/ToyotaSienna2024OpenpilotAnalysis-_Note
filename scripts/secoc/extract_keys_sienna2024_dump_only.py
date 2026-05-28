#!/usr/bin/env python3
"""
2024 Toyota Sienna SecOC dump-only tool.

This is intentionally not a key extractor. It preserves the old direct branch
UDS/unlock/payload/dump path, then writes raw dumps and transcripts for offline
layout discovery. It never writes openpilot params.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import inspect
import shutil
import struct
import subprocess
import sys
import time

try:
  from panda.python.uds import NegativeResponseError
except ImportError:
  try:
    from panda.uds import NegativeResponseError
  except ImportError:
    try:
      from opendbc.car.uds import NegativeResponseError
    except ImportError:
      class NegativeResponseError(Exception):
        pass


PROFILES = {
  "sienna_2024_eps": {
    "payload_name": "payload.bin",
    "tx_addr": 0x7A1,
    "rx_addr": 0x7A9,
    "bus": 0,
    "app_version_hex": "0138393635423435313430303000000000",
    "boot_version_hex": "022121212121212121212121212121212121212121212121212121212121212121",
    "download_address": 0xFEBF0000,
    "download_size": 0x1000,
    "erase_address": 0x000E0000,
    "erase_size": 0x8000,
    "dump_ranges": [
      [0xFEBE6E34, 0xFEBE6FF4],
    ],
    "session_settle_seconds": 0.2,
    "programming_settle_seconds": 0.8,
  },
  "sienna_2024_eps_nearby_8k": {
    "payload_name": "payload_febe6000_febe8000.bin",
    "tx_addr": 0x7A1,
    "rx_addr": 0x7A9,
    "bus": 0,
    "app_version_hex": "0138393635423435313430303000000000",
    "boot_version_hex": "022121212121212121212121212121212121212121212121212121212121212121",
    "download_address": 0xFEBF0000,
    "download_size": 0x1000,
    "erase_address": 0x000E0000,
    "erase_size": 0x8000,
    "dump_ranges": [
      [0xFEBE6000, 0xFEBE8000],
    ],
    "session_settle_seconds": 0.2,
    "programming_settle_seconds": 0.8,
  },
  "sienna_2024_eps_dataflash": {
    "payload_name": "payload_dataflash_ff200000_ff208000.bin",
    "tx_addr": 0x7A1,
    "rx_addr": 0x7A9,
    "bus": 0,
    "app_version_hex": "0138393635423435313430303000000000",
    "boot_version_hex": "022121212121212121212121212121212121212121212121212121212121212121",
    "download_address": 0xFEBF0000,
    "download_size": 0x1000,
    "erase_address": 0x000E0000,
    "erase_size": 0x8000,
    "dump_ranges": [
      [0xFF200000, 0xFF208000],
    ],
    "session_settle_seconds": 0.2,
    "programming_settle_seconds": 0.8,
  },
}

SEED_KEY_SECRET = bytes.fromhex("00" * 16)
DID_201_KEY = b"\x00" * 16
DID_202_IV = b"\x00" * 16
APP_DID_FALLBACK = 0xF181
RESPONSE_PENDING = b"\x03\x7f\x31\x78\x00\x00\x00\x00"


class PartialDumpError(TimeoutError):
  def __init__(self, message, output_path, start, end, current, frames, expected_frames, bytes_count, captured_offsets=None):
    super().__init__(message)
    self.output_path = Path(output_path)
    self.start = start
    self.end = end
    self.current = current
    self.frames = frames
    self.expected_frames = expected_frames
    self.bytes_count = bytes_count
    self.captured_offsets = sorted(captured_offsets or [])


def compact_captured_ranges(start, captured_offsets):
  ranges = []
  if not captured_offsets:
    return ranges
  sorted_offsets = sorted(captured_offsets)
  range_start = sorted_offsets[0]
  prev = sorted_offsets[0]
  for offset in sorted_offsets[1:]:
    if offset == prev + 4:
      prev = offset
      continue
    ranges.append([f"0x{start + range_start:08x}", f"0x{start + prev + 4:08x}"])
    range_start = offset
    prev = offset
  ranges.append([f"0x{start + range_start:08x}", f"0x{start + prev + 4:08x}"])
  return ranges


def const_value(container, attr_name, dict_name=None, default=None):
  if hasattr(container, attr_name):
    return getattr(container, attr_name)
  if isinstance(container, dict):
    if attr_name in container:
      return container[attr_name]
    if dict_name and dict_name in container:
      return container[dict_name]
  if default is not None:
    return default
  raise KeyError(attr_name)


def parse_int(text):
  return int(str(text), 0)


def parse_range(text):
  if ":" not in text:
    raise argparse.ArgumentTypeError("dump range must be START:END, e.g. 0xfebe6e34:0xfebe6ff4")
  start_text, end_text = text.split(":", 1)
  start = parse_int(start_text)
  end = parse_int(end_text)
  if end <= start:
    raise argparse.ArgumentTypeError("dump range END must be greater than START")
  if (end - start) % 4:
    raise argparse.ArgumentTypeError("dump range length must be a multiple of 4")
  return [start, end]


def settle(seconds, logger, phase):
  if seconds and seconds > 0:
    logger.event(phase, seconds=seconds)
    time.sleep(seconds)


def uds_retry(label, logger, attempts, delay, func):
  last_exc = None
  for attempt in range(1, attempts + 1):
    try:
      if attempts > 1:
        logger.event(f"{label}_attempt", attempt=attempt, attempts=attempts)
      return func()
    except Exception as exc:
      last_exc = exc
      if attempt >= attempts:
        break
      logger.event(f"{label}_retry", ok=False, attempt=attempt, attempts=attempts, error=repr(exc))
      time.sleep(delay)
  raise last_exc


def now_tag():
  return time.strftime("%Y%m%d_%H%M%S")


def sha256_file(path):
  h = hashlib.sha256()
  with open(path, "rb") as f:
    while True:
      chunk = f.read(1024 * 1024)
      if not chunk:
        break
      h.update(chunk)
  return h.hexdigest()


class RunLogger:
  def __init__(self, output_dir, run_stamp=None):
    self.output_dir = Path(output_dir)
    self.output_dir.mkdir(parents=True, exist_ok=True)
    transcript_name = f"transcript_{run_stamp}.jsonl" if run_stamp else "transcript.jsonl"
    self.transcript_path = self.output_dir / transcript_name

  def event(self, phase, ok=True, **fields):
    record = {
      "ts": time.time(),
      "phase": phase,
      "ok": ok,
      **fields,
    }
    with open(self.transcript_path, "a", encoding="utf-8") as f:
      f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    status = "OK" if ok else "FAIL"
    print(f"[{status}] {phase}")
    for key, value in fields.items():
      if key in ("error", "detail", "path", "hex", "value"):
        print(f"  {key}: {value}")


def pidof(name):
  try:
    out = subprocess.check_output(["pidof", name], stderr=subprocess.DEVNULL)
    return out.decode("utf-8", errors="replace").strip()
  except Exception:
    return ""


def check_openpilot_stopped(skip_check, logger):
  if skip_check:
    logger.event("openpilot_check_skipped")
    return
  boardd = pidof("boardd")
  manager = pidof("manager.py")
  if boardd or manager:
    logger.event(
      "openpilot_running",
      ok=False,
      detail=f"boardd={boardd or '-'} manager.py={manager or '-'}",
    )
    raise SystemExit("openpilot/boardd appears to be running. Stop openpilot first or pass --skip-openpilot-check.")
  logger.event("openpilot_not_running")


def resolve_payload_path(args, profile):
  candidates = []
  if args.payload:
    candidates.append(Path(args.payload))
  script_dir = Path(__file__).resolve().parent
  payload_name = profile.get("payload_name", "payload.bin")
  candidates.extend([
    Path.cwd() / payload_name,
    script_dir / payload_name,
  ])
  if payload_name == "payload.bin":
    candidates.extend([
      Path.cwd() / "payload.bin",
      script_dir / "payload.bin",
      script_dir / "secoc" / "payload.bin",
      script_dir / "GoodSecoc" / "secoc" / "payload.bin",
      script_dir / "20241205" / "secoc" / "payload.bin",
    ])
  for path in candidates:
    if path.is_file():
      return path
  raise FileNotFoundError(f"{payload_name} not found. Pass --payload /path/to/payload.bin")


def build_security_key(seed):
  from Crypto.Cipher import AES

  seed_payload = b"\x00" * 16
  intermediate = AES.new(SEED_KEY_SECRET, AES.MODE_ECB).decrypt(seed_payload)
  return AES.new(intermediate, AES.MODE_ECB).encrypt(seed)


def import_panda_stack():
  from panda import Panda

  last_error = None
  for module_name in ("panda.python.uds", "panda.uds", "opendbc.car.uds"):
    try:
      module = __import__(
        module_name,
        fromlist=[
          "UdsClient",
          "ACCESS_TYPE",
          "SESSION_TYPE",
          "DATA_IDENTIFIER_TYPE",
          "SERVICE_TYPE",
          "ROUTINE_CONTROL_TYPE",
          "NegativeResponseError",
        ],
      )
      globals()["NegativeResponseError"] = module.NegativeResponseError
      return {
        "Panda": Panda,
        "UdsClient": module.UdsClient,
        "IsoTpMessage": getattr(module, "IsoTpMessage", None),
        "ACCESS_TYPE": module.ACCESS_TYPE,
        "SESSION_TYPE": module.SESSION_TYPE,
        "DATA_IDENTIFIER_TYPE": module.DATA_IDENTIFIER_TYPE,
        "SERVICE_TYPE": module.SERVICE_TYPE,
        "ROUTINE_CONTROL_TYPE": module.ROUTINE_CONTROL_TYPE,
        "uds_module": module_name,
      }
    except ImportError as e:
      last_error = e
      continue

  raise last_error or ImportError("no compatible UDS module found")


def verify_runtime_imports(logger=None):
  from Crypto.Cipher import AES

  panda_stack = import_panda_stack()
  Panda = panda_stack["Panda"]
  UdsClient = panda_stack["UdsClient"]

  required_panda_attrs = [
    "can_recv",
    "can_send",
    "set_safety_mode",
  ]
  missing_panda_attrs = [name for name in required_panda_attrs if not hasattr(Panda, name)]
  has_isotp_send = hasattr(Panda, "isotp_send")
  has_isotp_message = panda_stack.get("IsoTpMessage") is not None

  required_uds_methods = [
    "_uds_request",
    "diagnostic_session_control",
    "read_data_by_identifier",
    "security_access",
    "write_data_by_identifier",
    "transfer_data",
    "request_transfer_exit",
    "routine_control",
  ]
  missing_uds_methods = [name for name in required_uds_methods if not hasattr(UdsClient, name)]

  const_checks = {
    "ACCESS_TYPE.REQUEST_SEED": const_value(panda_stack["ACCESS_TYPE"], "REQUEST_SEED", "requestSeed"),
    "ACCESS_TYPE.SEND_KEY": const_value(panda_stack["ACCESS_TYPE"], "SEND_KEY", "sendKey"),
    "SESSION_TYPE.DEFAULT": const_value(panda_stack["SESSION_TYPE"], "DEFAULT", "default"),
    "SESSION_TYPE.EXTENDED_DIAGNOSTIC": const_value(panda_stack["SESSION_TYPE"], "EXTENDED_DIAGNOSTIC", "extended"),
    "SESSION_TYPE.PROGRAMMING": const_value(panda_stack["SESSION_TYPE"], "PROGRAMMING", "programming"),
    "DATA_IDENTIFIER_TYPE.APPLICATION_SOFTWARE_IDENTIFICATION": const_value(
      panda_stack["DATA_IDENTIFIER_TYPE"],
      "APPLICATION_SOFTWARE_IDENTIFICATION",
      default=APP_DID_FALLBACK,
    ),
    "SERVICE_TYPE.REQUEST_DOWNLOAD": const_value(panda_stack["SERVICE_TYPE"], "REQUEST_DOWNLOAD", "requestDownload"),
    "ROUTINE_CONTROL_TYPE.START": const_value(panda_stack["ROUTINE_CONTROL_TYPE"], "START", "startRoutine"),
  }

  security_access_signature = str(inspect.signature(UdsClient.security_access))
  init_signature = str(inspect.signature(UdsClient.__init__))

  # Exercise AES import and mode without using ECU data.
  AES.new(SEED_KEY_SECRET, AES.MODE_ECB).decrypt(b"\x00" * 16)

  result = {
    "crypto_aes": True,
    "uds_module": panda_stack.get("uds_module"),
    "panda_class": f"{Panda.__module__}.{Panda.__name__}",
    "uds_client_class": f"{UdsClient.__module__}.{UdsClient.__name__}",
    "missing_panda_attrs": missing_panda_attrs,
    "missing_uds_methods": missing_uds_methods,
    "has_direct_isotp_send": has_isotp_send,
    "has_uds_isotp_message": has_isotp_message,
    "const_checks": {key: int(value) for key, value in const_checks.items()},
    "uds_client_init_signature": init_signature,
    "security_access_signature": security_access_signature,
  }
  result["ok"] = not missing_panda_attrs and not missing_uds_methods and (has_isotp_send or has_isotp_message)

  if logger:
    logger.event(
      "dry_run_runtime_imports",
      ok=result["ok"],
      value=result["uds_module"],
      detail=json.dumps({
        "missing_panda_attrs": missing_panda_attrs,
        "missing_uds_methods": missing_uds_methods,
        "has_direct_isotp_send": has_isotp_send,
        "has_uds_isotp_message": has_isotp_message,
        "security_access_signature": security_access_signature,
      }, sort_keys=True),
    )
  if not result["ok"]:
    raise RuntimeError(f"runtime import check failed: {result}")
  return result


def safety_elm327_value(Panda):
  return getattr(Panda, "SAFETY_ELM327", 3)


def make_uds_client(UdsClient, panda, profile, args):
  kwargs = {
    "timeout": args.timeout,
    "response_pending_timeout": args.response_pending_timeout,
  }
  if args.debug:
    kwargs["debug"] = True
  try:
    return UdsClient(
      panda,
      profile["tx_addr"],
      profile["rx_addr"],
      profile["bus"],
      **kwargs,
    )
  except TypeError:
    kwargs.pop("debug", None)
    return UdsClient(
      panda,
      profile["tx_addr"],
      profile["rx_addr"],
      profile["bus"],
      **kwargs,
    )


def request_download_payload(uds_client, profile, payload, service_type, logger):
  if len(payload) != profile["download_size"]:
    raise ValueError(f"payload size {len(payload)} != expected {profile['download_size']}")

  logger.event("write_did_0203")
  uds_client.write_data_by_identifier(0x203, b"\x00" * 5)

  logger.event("write_did_0201")
  uds_client.write_data_by_identifier(0x201, DID_201_KEY)

  logger.event("write_did_0202")
  uds_client.write_data_by_identifier(0x202, DID_202_IV)

  data = b"\x01"
  data += b"\x46"
  data += b"\x01"
  data += b"\x00"
  data += struct.pack("!I", profile["download_address"])
  data += struct.pack("!I", profile["download_size"])

  logger.event(
    "request_download",
    address=f"0x{profile['download_address']:08x}",
    size=profile["download_size"],
  )
  resp = uds_client._uds_request(const_value(service_type, "REQUEST_DOWNLOAD", "requestDownload"), data=data)
  logger.event("request_download_response", hex=resp.hex() if isinstance(resp, bytes) else str(resp))

  chunk_size = 0x400
  for offset in range(0, len(payload), chunk_size):
    block_no = offset // chunk_size + 1
    logger.event("transfer_data", block=block_no, offset=offset, size=chunk_size)
    uds_client.transfer_data(block_no, payload[offset:offset + chunk_size])

  logger.event("request_transfer_exit")
  uds_client.request_transfer_exit()


def routine_verify_payload(uds_client, profile, routine_control_type, logger):
  data = b"\x45\x00"
  data += struct.pack("!I", profile["download_address"])
  data += struct.pack("!I", profile["download_size"])
  logger.event("routine_10f0_start")
  uds_client.routine_control(const_value(routine_control_type, "START", "startRoutine"), 0x10F0, data)


def trigger_payload(panda, uds_client, profile, mode, routine_control_type, isotp_message_cls, logger):
  data = b"\x45\x00"
  data += struct.pack("!I", profile["erase_address"])
  data += struct.pack("!I", profile["erase_size"])

  if mode == "none":
    logger.event("trigger_skipped")
    return

  if mode == "routine":
    logger.event("trigger_payload_routine_ff00")
    uds_client.routine_control(const_value(routine_control_type, "START", "startRoutine"), 0xFF00, data)
    return

  if mode == "isotp":
    logger.event("trigger_payload_isotp_ff00")
    erase = b"\x31\x01\xff\x00" + data
    if hasattr(panda, "isotp_send"):
      panda.isotp_send(profile["tx_addr"], erase, bus=profile["bus"])
      return
    if isotp_message_cls is None or not hasattr(uds_client, "_can_client"):
      raise RuntimeError("no compatible ISO-TP sender available")
    isotp = isotp_message_cls(uds_client._can_client, timeout=0.1)
    isotp.send(erase)
    deadline = time.monotonic() + 2.0
    while not getattr(isotp, "tx_done", True):
      if time.monotonic() > deadline:
        raise TimeoutError("timeout sending trigger ISO-TP request")
      try:
        isotp.recv(0.1)
      except Exception:
        if getattr(isotp, "tx_done", False):
          break
        raise
    return

  raise ValueError(f"unknown trigger mode: {mode}")


def dump_range(panda, profile, start, end, output_path, logger, idle_timeout):
  logger.event("dump_range_start", start=f"0x{start:08x}", end=f"0x{end:08x}", path=str(output_path))
  expected_frames = (end - start) // 4
  chunks = {}
  last_rx = time.monotonic()

  with open(output_path, "wb") as f:
    while len(chunks) < expected_frames:
      saw_frame = False
      for addr, data, bus in panda.can_recv():
        if bus != profile["bus"] or addr != profile["rx_addr"]:
          continue
        if data == RESPONSE_PENDING:
          continue
        saw_frame = True
        last_rx = time.monotonic()

        if len(data) < 8:
          logger.event("short_dump_frame", ok=False, hex=data.hex())
          continue

        ptr = struct.unpack("<I", data[:4])[0]
        frame_addr = (start & 0xFF000000) | ((ptr >> 8) & 0xFFFFFF)
        if frame_addr < start or frame_addr >= end or ((frame_addr - start) % 4) != 0:
          logger.event(
            "unexpected_dump_pointer",
            ok=False,
            expected=f"0x{start:08x}-0x{end:08x}",
            ptr=f"0x{ptr:08x}",
            decoded=f"0x{frame_addr:08x}",
            hex=data.hex(),
          )
          continue

        offset = frame_addr - start
        if offset in chunks:
          continue

        chunk = data[4:8]
        chunks[offset] = chunk
        f.seek(offset)
        f.write(chunk)
        f.flush()
        if len(chunks) % 32 == 0 or len(chunks) >= expected_frames:
          logger.event("dump_progress", frames=len(chunks), expected_frames=expected_frames, bytes=len(chunks) * 4)
        break

      if not saw_frame and (time.monotonic() - last_rx) > idle_timeout:
        missing = [start + offset for offset in range(0, end - start, 4) if offset not in chunks]
        current = missing[0] if missing else end
        raise PartialDumpError(
          f"no dump frame for {idle_timeout:.1f}s at 0x{current:08x}",
          output_path,
          start,
          end,
          current,
          len(chunks),
          expected_frames,
          len(chunks) * 4,
          captured_offsets=chunks.keys(),
        )

  full_dump = bytearray(end - start)
  for offset, chunk in chunks.items():
    full_dump[offset:offset + 4] = chunk
  logger.event("dump_range_done", bytes=len(full_dump), frames=len(chunks), path=str(output_path))
  return bytes(full_dump)


def mark_partial_dump(error, dump_path, dump_name, logger):
  partial_name = dump_name[:-4] + ".partial.bin" if dump_name.endswith(".bin") else dump_name + ".partial"
  partial_path = dump_path.with_name(partial_name)
  if dump_path.exists():
    if partial_path.exists():
      partial_path.unlink()
    try:
      dump_path.replace(partial_path)
    except OSError:
      shutil.copyfile(dump_path, partial_path)
      try:
        dump_path.unlink()
      except OSError:
        logger.event("partial_dump_original_left_in_place", ok=False, path=str(dump_path))
  elif partial_path.exists():
    pass
  else:
    partial_path = dump_path

  sha256 = None
  if partial_path.exists():
    sha256 = sha256_file(partial_path)

  info = {
    "file": partial_path.name,
    "status": "partial",
    "partial": True,
    "start": f"0x{error.start:08x}",
    "end": f"0x{error.end:08x}",
    "current": f"0x{error.current:08x}",
    "bytes": error.bytes_count,
    "frames": error.frames,
    "expected_frames": error.expected_frames,
    "captured_ranges": compact_captured_ranges(error.start, error.captured_offsets),
    "captured_range_count": len(compact_captured_ranges(error.start, error.captured_offsets)),
    "error": str(error),
  }
  if sha256 is not None:
    info["sha256"] = sha256

  logger.event(
    "partial_dump_saved",
    ok=False,
    path=str(partial_path),
    value=f"{error.bytes_count}/{error.end - error.start} bytes",
    error=str(error),
  )
  return info


def write_dump_summary(output_dir, dump_infos, run_stamp=None):
  lines = [
    "# SecOC Dump Summary",
    "",
    "This is a raw dump capture. It does not prove that any extracted bytes are SecOC keys.",
    "",
    "## Dumps",
    "",
  ]
  for info in dump_infos:
    lines.append(f"- `{info['file']}`")
    lines.append(f"  - range: `{info['start']} -> {info['end']}`")
    lines.append(f"  - bytes: `{info['bytes']}`")
    lines.append(f"  - sha256: `{info['sha256']}`")
  summary_name = f"dump_summary_{run_stamp}.md" if run_stamp else "dump_summary.md"
  Path(output_dir, summary_name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args):
  run_stamp = args.run_stamp or now_tag()
  dated_stamp = run_stamp if args.dated_files else None
  profile = dict(PROFILES[args.profile])
  if args.tx_addr is not None:
    profile["tx_addr"] = parse_int(args.tx_addr)
    profile["rx_addr"] = profile["tx_addr"] + 8 if args.rx_addr is None else parse_int(args.rx_addr)
  if args.rx_addr is not None:
    profile["rx_addr"] = parse_int(args.rx_addr)
  if args.bus is not None:
    profile["bus"] = int(args.bus)
  if args.dump_range:
    profile["dump_ranges"] = args.dump_range

  output_dir = Path(args.output_dir or Path("out") / f"secoc_dump_{run_stamp}").resolve()
  logger = RunLogger(output_dir, dated_stamp)

  metadata = {
    "tool": Path(__file__).name,
    "created_at": time.strftime("%Y-%m-%d %H:%M:%S %z"),
    "run_stamp": run_stamp,
    "profile": args.profile,
    "tx_addr": f"0x{profile['tx_addr']:x}",
    "rx_addr": f"0x{profile['rx_addr']:x}",
    "bus": profile["bus"],
    "dump_ranges": [[f"0x{s:08x}", f"0x{e:08x}"] for s, e in profile["dump_ranges"]],
    "timeout": args.timeout,
    "response_pending_timeout": args.response_pending_timeout,
    "dump_idle_timeout": args.dump_idle_timeout,
    "uds_attempts": args.uds_attempts,
    "uds_retry_delay": args.uds_retry_delay,
    "skip_bootloader_check": args.skip_bootloader_check,
    "session_settle_seconds": profile.get("session_settle_seconds", 0),
    "programming_settle_seconds": profile.get("programming_settle_seconds", 0),
    "safety_ack_parked": bool(args.unsafe_ack_parked),
    "writes_openpilot_param": False,
    "parses_key": False,
  }

  try:
    payload_path = resolve_payload_path(args, profile)
    payload_sha256 = sha256_file(payload_path)
    payload = payload_path.read_bytes()
    metadata["payload_path"] = str(payload_path)
    metadata["payload_size"] = len(payload)
    metadata["payload_sha256"] = payload_sha256
    logger.event("payload_resolved", path=str(payload_path), size=len(payload), sha256=payload_sha256)

    if args.dry_run_profile:
      if args.dry_run_imports:
        import_check = verify_runtime_imports(logger)
        metadata["runtime_import_check"] = import_check
        metadata["uds_module"] = import_check.get("uds_module")
      logger.event("dry_run_profile_done")
      return output_dir

    if not args.unsafe_ack_parked:
      metadata["error"] = "unsafe_ack_parked_required"
      logger.event(
        "safety_refused",
        ok=False,
        reason="This EPS UDS dump can affect power steering assist. Run only while parked and pass --unsafe-ack-parked.",
      )
      raise RuntimeError("unsafe_ack_parked_required")

    check_openpilot_stopped(args.skip_openpilot_check, logger)

    panda_stack = import_panda_stack()
    Panda = panda_stack["Panda"]
    UdsClient = panda_stack["UdsClient"]
    IsoTpMessage = panda_stack["IsoTpMessage"]
    ACCESS_TYPE = panda_stack["ACCESS_TYPE"]
    SESSION_TYPE = panda_stack["SESSION_TYPE"]
    DATA_IDENTIFIER_TYPE = panda_stack["DATA_IDENTIFIER_TYPE"]
    SERVICE_TYPE = panda_stack["SERVICE_TYPE"]
    ROUTINE_CONTROL_TYPE = panda_stack["ROUTINE_CONTROL_TYPE"]
    metadata["uds_module"] = panda_stack.get("uds_module")
    logger.event("uds_module_loaded", value=panda_stack.get("uds_module"))

    panda = Panda()
    logger.event("panda_connected")
    panda.set_safety_mode(safety_elm327_value(Panda))
    logger.event("panda_safety_elm327", value=safety_elm327_value(Panda))

    uds_client = make_uds_client(UdsClient, panda, profile, args)

    app_did = const_value(
      DATA_IDENTIFIER_TYPE,
      "APPLICATION_SOFTWARE_IDENTIFICATION",
      default=APP_DID_FALLBACK,
    )

    logger.event("read_application_version")
    app_version = uds_retry(
      "read_application_version",
      logger,
      args.uds_attempts,
      args.uds_retry_delay,
      lambda: uds_client.read_data_by_identifier(app_did),
    )
    metadata["application_version_hex"] = app_version.hex()
    logger.event("application_version", hex=app_version.hex())
    if app_version.hex() != profile["app_version_hex"]:
      raise RuntimeError(f"unexpected app version {app_version.hex()}")

    logger.event("session_default")
    uds_retry(
      "session_default",
      logger,
      args.uds_attempts,
      args.uds_retry_delay,
      lambda: uds_client.diagnostic_session_control(const_value(SESSION_TYPE, "DEFAULT", "default")),
    )
    settle(profile.get("session_settle_seconds", 0), logger, "settle_after_session_default")
    logger.event("session_extended")
    uds_retry(
      "session_extended",
      logger,
      args.uds_attempts,
      args.uds_retry_delay,
      lambda: uds_client.diagnostic_session_control(const_value(SESSION_TYPE, "EXTENDED_DIAGNOSTIC", "extended")),
    )
    settle(profile.get("session_settle_seconds", 0), logger, "settle_after_session_extended")
    logger.event("session_programming")
    uds_retry(
      "session_programming",
      logger,
      args.uds_attempts,
      args.uds_retry_delay,
      lambda: uds_client.diagnostic_session_control(const_value(SESSION_TYPE, "PROGRAMMING", "programming")),
    )
    settle(profile.get("programming_settle_seconds", 0), logger, "settle_after_session_programming")

    if args.skip_bootloader_check:
      logger.event("bootloader_check_skipped")
      metadata["bootloader_check_skipped"] = True
    else:
      logger.event("session_default_for_bootloader_read")
      uds_retry(
        "session_default_for_bootloader_read",
        logger,
        args.uds_attempts,
        args.uds_retry_delay,
        lambda: uds_client.diagnostic_session_control(const_value(SESSION_TYPE, "DEFAULT", "default")),
      )
      settle(profile.get("session_settle_seconds", 0), logger, "settle_after_bootloader_default")
      logger.event("session_extended_for_bootloader_read")
      uds_retry(
        "session_extended_for_bootloader_read",
        logger,
        args.uds_attempts,
        args.uds_retry_delay,
        lambda: uds_client.diagnostic_session_control(const_value(SESSION_TYPE, "EXTENDED_DIAGNOSTIC", "extended")),
      )
      settle(profile.get("session_settle_seconds", 0), logger, "settle_after_bootloader_extended")
      logger.event("read_bootloader_version")
      boot_version = uds_retry(
        "read_bootloader_version",
        logger,
        args.uds_attempts,
        args.uds_retry_delay,
        lambda: uds_client.read_data_by_identifier(app_did),
      )
      metadata["bootloader_version_hex"] = boot_version.hex()
      logger.event("bootloader_version", hex=boot_version.hex())
      if boot_version.hex() != profile["boot_version_hex"]:
        raise RuntimeError(f"unexpected bootloader version {boot_version.hex()}")

    logger.event("session_programming_again")
    uds_retry(
      "session_programming_again",
      logger,
      args.uds_attempts,
      args.uds_retry_delay,
      lambda: uds_client.diagnostic_session_control(const_value(SESSION_TYPE, "PROGRAMMING", "programming")),
    )
    settle(profile.get("programming_settle_seconds", 0), logger, "settle_after_session_programming_again")

    seed_payload = b"\x00" * 16
    logger.event("security_access_request_seed")
    seed = uds_retry(
      "security_access_request_seed",
      logger,
      args.uds_attempts,
      args.uds_retry_delay,
      lambda: uds_client.security_access(
        const_value(ACCESS_TYPE, "REQUEST_SEED", "requestSeed"),
        data_record=seed_payload,
      ),
    )
    key = build_security_key(seed)
    metadata["security_seed_hex"] = seed.hex()
    metadata["security_key_sent_hex"] = key.hex()
    logger.event("security_seed", hex=seed.hex())

    logger.event("security_access_send_key")
    uds_retry(
      "security_access_send_key",
      logger,
      args.uds_attempts,
      args.uds_retry_delay,
      lambda: uds_client.security_access(const_value(ACCESS_TYPE, "SEND_KEY", "sendKey"), key),
    )
    logger.event("security_access_ok")

    if not args.skip_upload:
      request_download_payload(uds_client, profile, payload, SERVICE_TYPE, logger)
      routine_verify_payload(uds_client, profile, ROUTINE_CONTROL_TYPE, logger)
    else:
      logger.event("upload_skipped")

    trigger_payload(panda, uds_client, profile, args.trigger_mode, ROUTINE_CONTROL_TYPE, IsoTpMessage, logger)

    dump_infos = []
    for start, end in profile["dump_ranges"]:
      dump_name = f"dump_{dated_stamp}_{start:08x}_{end:08x}.bin" if dated_stamp else f"dump_{start:08x}_{end:08x}.bin"
      dump_path = output_dir / dump_name
      try:
        dump_bytes = dump_range(panda, profile, start, end, dump_path, logger, args.dump_idle_timeout)
      except PartialDumpError as e:
        partial_info = mark_partial_dump(e, dump_path, dump_name, logger)
        dump_infos.append(partial_info)
        metadata["dumps"] = dump_infos
        metadata["partial_dump"] = True
        metadata["partial_dump_file"] = partial_info["file"]
        metadata["partial_dump_bytes"] = partial_info["bytes"]
        metadata["partial_dump_frames"] = partial_info["frames"]
        metadata["partial_dump_expected_frames"] = partial_info["expected_frames"]
        metadata["partial_dump_current"] = partial_info["current"]
        raise
      dump_infos.append({
        "file": dump_name,
        "status": "complete",
        "partial": False,
        "start": f"0x{start:08x}",
        "end": f"0x{end:08x}",
        "bytes": len(dump_bytes),
        "frames": len(dump_bytes) // 4,
        "expected_frames": (end - start) // 4,
        "sha256": hashlib.sha256(dump_bytes).hexdigest(),
      })

    metadata["dumps"] = dump_infos
    write_dump_summary(output_dir, dump_infos, dated_stamp)
    logger.event("run_done", path=str(output_dir))
    return output_dir

  except NegativeResponseError as e:
    logger.event("negative_response", ok=False, error=str(e))
    metadata["error"] = str(e)
    raise
  except Exception as e:
    logger.event("exception", ok=False, error=repr(e))
    metadata["error"] = repr(e)
    raise
  finally:
    metadata_name = f"metadata_{dated_stamp}.json" if dated_stamp else "metadata.json"
    metadata_path = output_dir / metadata_name
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_arg_parser():
  parser = argparse.ArgumentParser(description="2024 Sienna SecOC dump-only capture tool")
  parser.add_argument("--profile", choices=sorted(PROFILES), default="sienna_2024_eps")
  parser.add_argument("--payload", help="payload.bin path")
  parser.add_argument("--output-dir", help="output directory; default out/secoc_dump_YYYYMMDD_HHMMSS")
  parser.add_argument("--run-stamp", help="timestamp label for this run, e.g. YYYYMMDD_HHMMSS")
  parser.add_argument("--dated-files", action="store_true", help="include run stamp in metadata/transcript/summary/dump filenames")
  parser.add_argument("--dump-range", action="append", type=parse_range, help="START:END, e.g. 0xfebe6e34:0xfebe6ff4")
  parser.add_argument("--tx-addr", help="override UDS tx address")
  parser.add_argument("--rx-addr", help="override UDS rx address")
  parser.add_argument("--bus", type=int, help="override bus")
  parser.add_argument("--timeout", type=float, default=2.0)
  parser.add_argument("--response-pending-timeout", type=float, default=20.0)
  parser.add_argument("--dump-idle-timeout", type=float, default=5.0)
  parser.add_argument("--uds-attempts", type=int, default=3, help="UDS retries for version/session/security steps")
  parser.add_argument("--uds-retry-delay", type=float, default=1.0, help="seconds to wait between UDS retries")
  parser.add_argument("--trigger-mode", choices=["isotp", "routine", "none"], default="isotp")
  parser.add_argument("--skip-upload", action="store_true", help="skip DID/download/routine upload path")
  parser.add_argument("--skip-bootloader-check", action="store_true", default=True, help="skip bootloader DID check and proceed to SecurityAccess")
  parser.add_argument("--require-bootloader-check", dest="skip_bootloader_check", action="store_false", help="require bootloader DID check before SecurityAccess")
  parser.add_argument("--skip-openpilot-check", action="store_true", help="allow running while boardd/manager.py is present")
  parser.add_argument("--unsafe-ack-parked", action="store_true", help="required for non-dry-run; confirms vehicle is parked and this EPS dump must not be run while driving")
  parser.add_argument("--dry-run-profile", action="store_true", help="resolve payload/profile and write metadata only")
  parser.add_argument("--dry-run-imports", action="store_true", help="with --dry-run-profile, also verify Panda and UDS imports without opening Panda")
  parser.add_argument("--debug", action="store_true", help="enable UDS debug logging")
  return parser


def main():
  args = build_arg_parser().parse_args()
  out = run(args)
  print(f"\n[INFO] output: {out}")
  print("[INFO] dump-only complete; no key parsing and no SecOCKey param write were performed.")


if __name__ == "__main__":
  main()
