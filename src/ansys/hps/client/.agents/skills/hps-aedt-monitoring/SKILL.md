---
name: hps-aedt-monitoring
description: STUB — Live monitoring of Ansys AEDT (Electronics Desktop) jobs running on HPS. Populate with AEDT-specific output file names, progress format, and regex patterns from the first real monitoring session. Load hps-solver-monitoring for shared timeout/reset/token patterns.
---

# HPS AEDT Monitoring

> **Stub** — this file has not yet been populated from a real monitoring session.
> When you successfully monitor an AEDT job, update this file with:
> - Which output file(s) to tail (AEDT solver progress log)
> - The progress/convergence line format and a working regex
> - Any AEDT-specific timing behaviour (EM solves can take minutes per frequency point)
> - A complete tested monitoring snippet

Always load `hps-solver-monitoring` alongside this skill. All shared patterns (MonitorClient `timeout_seconds`, conditional job reset, backlog, token TTL) live there.

## Known AEDT output files

| File | Content |
|------|---------|
| `*.log` | Main solver log — frequency sweep progress, adaptive pass convergence |
| `*.aedt.lock` | Lock file (not useful for monitoring) |

## Likely progress format

AEDT adaptive pass convergence lines typically look like:

```
[info] Adaptive Pass 1, Converged = True, Max Delta S = 0.01234
[info] Frequency 2.4 GHz: Converged after 3 passes
```

AEDT frequency sweep lines:
```
[info] Solving frequency point 1 of 20: 1.0 GHz
```

Populate the actual regex once confirmed against a real HPS AEDT run.

## AEDT-specific timing note

AEDT solves (especially 3D EM) can have very long gaps between log lines — tens of minutes per frequency point. Set `timeout_seconds` in `MonitorClient` to at least 3600 (1 hour) for full-wave EM jobs.

## TODO

- [ ] Run an AEDT job and capture raw `stream_task_logs` messages
- [ ] Identify the correct `file_path` filter value for AEDT progress output
- [ ] Write and validate a regex for convergence/frequency-point lines
- [ ] Document adaptive pass vs. frequency sweep structure
- [ ] Update this file with complete working example
