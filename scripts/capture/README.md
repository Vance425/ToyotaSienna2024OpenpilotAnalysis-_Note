# Raw CAN Logger

This directory contains the C3X-side raw CAN logger used by the legacy tool API.

## Legacy API Path

The phone UI `START LOG` button calls the legacy API job:

```text
POST /tools/jobs/start_logger/run
```

On the C3X, that job is defined in:

```text
/data/tools/mySienna_api/config/jobs.json
```

The job runs:

```text
/data/tools/start_logger.sh
```

`start_logger.sh` launches this script:

```text
/data/tools/toyota_full_bus_logger_seed_hunter_v3.3.py
```

In this repo the same script is stored as:

```text
scripts/capture/toyota_full_bus_logger_seed_hunter_v3_3.py
```

## Typical Command

```bash
/usr/local/venv/bin/python3 scripts/capture/toyota_full_bus_logger_seed_hunter_v3_3.py \
  --out /data/raw_can_logs \
  --pid-file /data/raw_can_logs/logger.pid \
  --stdout-log /data/raw_can_logs/logger_stdout.log
```

## Outputs

- `toyota_all_*.ndjson`: continuous full-bus stream
- `toyota_seg_IGN_ON_*.ndjson`: ignition-on segmented stream
- `toyota_seg_IGN_OFF_*.ndjson`: ignition-off segmented stream
- `events.jsonl`
- `file_index.jsonl`
- `state_timeline.jsonl`
- `lifecycle_events.jsonl`
- `session_manifest.json`
- `health_summary.json`
- `seed_key_pairs.csv`

## Notes

The logger uses Panda directly and is intended to run on a C3X / openpilot environment. It does not include raw CAN logs, keys, VIN, dongle id, or vehicle-specific secrets.
