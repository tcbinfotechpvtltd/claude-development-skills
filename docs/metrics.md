# eng-os metrics log
One row per audit, from `eng-os usage --since <previous audit>`. Turn-1 context = tokens in context before the first reply (system prompt + tools + CLAUDE.md + skill listing + memory).

| Date | Claude Code | Window | Sessions | Turn-1 ctx (median) | Cache-read % | Subagent share of input | Repeat Reads | Tool errors | Compactions | Guard blocks | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-03 | 2.1.299–2.1.309 | 2026-10-06..11-03 | 50 | 83,350 | 98.5 | 40.5% | 62/256 (24%) | 293 | 8 | 2 | Baseline before eng-os (the 2 guard blocks are install tests) |
