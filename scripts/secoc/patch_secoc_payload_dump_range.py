#!/usr/bin/env python3
"""Patch the old encrypted SecOC payload to dump a nearby memory range.

This avoids rebuilding the V850 shellcode when only the hard-coded dump start
and end constants change. It decrypts payload.bin, replaces the two 32-bit
little-endian addresses, recomputes the CRC/CMAC trailer, and encrypts a new
payload file.
"""

from __future__ import annotations

import argparse
import binascii
import json
from pathlib import Path
import struct

from Crypto.Cipher import AES
from Crypto.Hash import CMAC


SECRET_DEFAULT = "00" * 16
ZERO_16 = "00" * 16
CRC_DATA_END = 0xFEC
CRC_BLOCK_END = 0xFF0
CMAC_END = 0x1000


def parse_int(text: str) -> int:
  return int(str(text), 0)


def derive_key(secret: bytes, did_key: bytes) -> bytes:
  return AES.new(secret, AES.MODE_ECB).encrypt(did_key)


def aes_cmac(data: bytes, key: bytes) -> bytes:
  cobj = CMAC.new(key, ciphermod=AES)
  cobj.update(data)
  return cobj.digest()


def replace_exact(buf: bytearray, old: bytes, new: bytes, label: str) -> list[int]:
  hits = []
  pos = 0
  while True:
    idx = buf.find(old, pos)
    if idx < 0:
      break
    hits.append(idx)
    pos = idx + 1
  if len(hits) != 1:
    raise RuntimeError(f"expected exactly one {label} constant, found {len(hits)} at {hits}")
  buf[hits[0]:hits[0] + len(old)] = new
  return hits


def patch_payload(args: argparse.Namespace) -> dict:
  secret = bytes.fromhex(args.secret)
  did_key = bytes.fromhex(args.key)
  iv = bytes.fromhex(args.iv)
  if len(secret) != 16 or len(did_key) != 16 or len(iv) != 16:
    raise ValueError("secret/key/iv must be 16 bytes each")

  encrypted = args.input.read_bytes()
  if len(encrypted) != CMAC_END or len(encrypted) % 16 != 0:
    raise ValueError(f"expected 4096-byte AES-CBC payload, got {len(encrypted)}")

  derived = derive_key(secret, did_key)
  plain = bytearray(AES.new(derived, AES.MODE_CBC, iv=iv).decrypt(encrypted))

  old_start = struct.pack("<I", args.old_start)
  old_end = struct.pack("<I", args.old_end)
  new_start = struct.pack("<I", args.new_start)
  new_end = struct.pack("<I", args.new_end)

  start_hits = replace_exact(plain, old_start, new_start, "dump start")
  end_hits = replace_exact(plain, old_end, new_end, "dump end")

  crc = binascii.crc32(plain[:CRC_DATA_END])
  plain[CRC_DATA_END:CRC_BLOCK_END] = struct.pack("<I", crc ^ 0xFFFFFFFF)
  if binascii.crc32(plain[:CRC_BLOCK_END]) != 0xFFFFFFFF:
    raise RuntimeError("CRC repair failed")

  cmac = aes_cmac(iv + bytes(plain[:CRC_BLOCK_END]), key=derived)
  plain[CRC_BLOCK_END:CMAC_END] = cmac

  patched = AES.new(derived, AES.MODE_CBC, iv=iv).encrypt(bytes(plain))
  args.output.parent.mkdir(parents=True, exist_ok=True)
  args.output.write_bytes(patched)

  summary = {
    "input": str(args.input),
    "output": str(args.output),
    "old_start": f"0x{args.old_start:08x}",
    "old_end": f"0x{args.old_end:08x}",
    "new_start": f"0x{args.new_start:08x}",
    "new_end": f"0x{args.new_end:08x}",
    "new_bytes": args.new_end - args.new_start,
    "new_frames": (args.new_end - args.new_start) // 4,
    "start_constant_offsets": [f"0x{x:x}" for x in start_hits],
    "end_constant_offsets": [f"0x{x:x}" for x in end_hits],
    "plain_crc32_first_0xff0": f"0x{binascii.crc32(plain[:CRC_BLOCK_END]) & 0xFFFFFFFF:08x}",
    "cmac": cmac.hex(),
    "sha256": __import__("hashlib").sha256(patched).hexdigest(),
  }
  if args.summary:
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
  return summary


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description="Patch encrypted SecOC dump payload range")
  parser.add_argument("--input", "-i", type=Path, required=True)
  parser.add_argument("--output", "-o", type=Path, required=True)
  parser.add_argument("--summary", type=Path)
  parser.add_argument("--old-start", type=parse_int, default=0xFEBE6E34)
  parser.add_argument("--old-end", type=parse_int, default=0xFEBE6FF4)
  parser.add_argument("--new-start", type=parse_int, default=0xFEBE6000)
  parser.add_argument("--new-end", type=parse_int, default=0xFEBE8000)
  parser.add_argument("--secret", default=SECRET_DEFAULT)
  parser.add_argument("--key", default=ZERO_16)
  parser.add_argument("--iv", default=ZERO_16)
  return parser


def main() -> int:
  args = build_parser().parse_args()
  if args.new_end <= args.new_start:
    raise SystemExit("new end must be greater than new start")
  if (args.new_end - args.new_start) % 4:
    raise SystemExit("new range length must be divisible by 4")
  summary = patch_payload(args)
  print(json.dumps(summary, indent=2, sort_keys=True))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
