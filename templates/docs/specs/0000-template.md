# <Feature> spec

**Status**: draft | agreed with <name, role> on YYYY-MM-DD | built | superseded
**Requirements**: REQ-nnn, REQ-nnn ([requirements.md](../requirements.md))

## 1. Problem
Who has it, what it costs them today, and why now. In the user's words where possible.

## 2. Solution in one paragraph
What the user will be able to do when this is done. No implementation detail.

## 3. User stories
- As a <role>, I want <capability>, so that <outcome>.
- (Cover every role, including the ones who must be denied, and the edge cases: empty, duplicate, concurrent, late, reversed.)

## 4. Decisions
The choices that shape the build, each with its reason: data model, state machine, API contract, vendor, sync or async. Describe behaviour and contracts, not file paths, so this stays true while the code moves. Decisions that are costly to reverse also get an ADR in `../adr/`.

## 5. Test seams
Where behaviour will be tested (the public function, API endpoint or screen), agreed before building. Expected values come from an independent source (the spec, a worked example, the client's own sheet), never recomputed by the code under test.

## 6. Out of scope
What this does not do, so nobody builds it by accident.

## 7. Open questions
Only the questions that would change the design, each with a recommended answer. Mark business facts **TO CONFIRM** until the client confirms them.

## 8. Tasks
The implementation plan (skill `eng-design`, `implementation-plans.md`):
- thin vertical slices, each small enough for one fresh session and each leaving the system working;
- for each slice: files, the test first, the change, the checks and the commit;
- dependencies between slices ("blocked by T-2");
- the slices that hit an approval gate.

| Task | Requirement | Blocked by | Gate? | Done (commit) |
|---|---|---|---|---|
| T-1 | REQ-nnn | – | no | |
