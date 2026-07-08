---
name: hps-mapdl-monitoring
description: STUB — Live monitoring of Ansys MAPDL jobs running on HPS. Populate with MAPDL-specific output file names, convergence data format, and regex patterns from the first real monitoring session. Load hps-solver-monitoring for shared timeout/reset/token patterns.
---

# HPS MAPDL Monitoring

> **Stub** — this file has not yet been populated from a real monitoring session.
> When you successfully monitor a MAPDL job, update this file with:
> - Which output file(s) to tail (e.g. `.out`, `.mntr`, solver log)
> - The convergence/residual line format and a working regex
> - Any MAPDL-specific timing or whitespace behaviour
> - A complete tested monitoring snippet

Always load `hps-solver-monitoring` alongside this skill. All shared patterns (MonitorClient `timeout_seconds`, conditional job reset, backlog, token TTL) live there.

## Known MAPDL output files

| File | Content |
|------|---------|
| `file.out` | Main solver output — convergence data, substep summaries |
| `file.mntr` | Monitor file — cumulative convergence table (ANSYS structural) |
| `*.log` | Session log |

## Likely convergence format (structural)

MAPDL structural convergence lines typically look like:

```
 EQUIL ITER   1 COMPLETED.  NEW TRIANG MATRIX.  MAX DOF INC=  2.230E+00  CRITERIUM=  1.000E-04
```

or for a force convergence monitor:
```
 *** LOAD STEP     1   SUBSTEP     1  COMPLETED.    CUM ITER =      1
     TIME=  1.00000    LOAD FACTOR=  1.000
```

Populate the actual regex once confirmed against a real HPS MAPDL run.

## TODO

- [ ] Run a MAPDL job and capture raw `stream_task_logs` messages
- [ ] Identify the correct `file_path` filter value for MAPDL convergence output
- [ ] Write and validate a regex for convergence lines
- [ ] Document substep/iteration structure (MAPDL uses substeps, not simple iteration numbers)
- [ ] Update this file with complete working example
