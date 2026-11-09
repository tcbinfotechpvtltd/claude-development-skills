# Implementation plans: write the plan, run it task by task, finish the branch

For multi-step work: several files, a run that lasts long or spans sessions, or tasks handed to subagents. A small change needs only the chat plan in SKILL.md section 5.

## 1. Write the plan
Put it in the spec (`docs/specs/<feature>.md`, section "Tasks"), so the project keeps one document set. Header: goal, requirement ids (`REQ-nnn`), base branch, the test command, and assumptions marked as such.

Each task gets:
- **Id and title**, and the requirement it serves.
- **Files**: exact paths to create or change.
- **Test first**: the test name, what it asserts, the command, and the failure expected before the change. A config-only or docs-only task may say "Test first: n/a" with the reason.
- **Change**: concrete enough for someone with no project context: signatures, the key logic, the data shapes. Include the code itself when the logic is not obvious.
- **Verify**: commands and the output that proves the task is done.
- **Commit message**.

Rules for the task list:
- One behaviour per task, small enough for one sitting (minutes, not hours), and each leaves the system working and green.
- Order tasks so each builds on a passing state; mark the ones that are independent and could run in parallel.
- Mark tasks that hit an approval gate (shared-data migration, auth, money movement, deploy, anything outward-facing): the run stops there and asks.
- No placeholders: "handle errors appropriately", "add validation", "TBD" and "similar to task 3" are not tasks.
- Check the plan against the spec before starting: every requirement has a task, and every task traces to a requirement. Get the user's go-ahead on a significant plan.

## 2. Run it
- Start on a branch, never on `main` or a shared branch, from a clean tree. Run the suite first and record the baseline; if it is already red, stop and report before changing anything.
- **What the user's go-ahead covers**: local commits on the plan's branch, one per task. Pushing, opening the PR, deploying and every other outward-facing step still need the user's explicit yes when the run reaches them.
- Per task: write the test, watch it fail for the expected reason, make the change, run the task's checks and the relevant suite, read the task's diff, commit (author and trailer rules: global CLAUDE.md, section 7). Tick the task in the plan.
- **Delegating a task to a subagent**: brief it with the task text, the file paths, the project's conventions and the verification command, not the conversation. Spell out its limits: no commits, pushes, deploys or changes to shared data, and stop and report at a task marked as a gate. Set the model by the rules in the global CLAUDE.md, section 8. Subagents working in parallel in one repo each need their own worktree (section 3). When one reports back, read its diff and re-run its checks yourself before you commit and tick the task.
- **Reviews**: risky tasks (money, auth, KYC, migrations, concurrency) get an independent reviewer subagent each; routine tasks share one review of the whole branch at the end.
- **Fix loop**: send a failed check or review back with the specific finding. A task that fails twice means the plan or the model of the problem is wrong: stop guessing and apply the two-failed-attempts rule in the global CLAUDE.md, section 3.
- **When a task shows the plan is wrong**, amend the plan (and the spec or ADR) before the next task, and note what changed and why. Never continue on a plan you know is stale.
- **Decisions made on the user's behalf** (an ambiguity resolved, a default chosen): keep a list as you go and put all of it in the final report, so the user can overrule any of them.
- **Long or multi-session runs**: the ticked plan plus a `docs/progress/` entry must be enough for a new session or a teammate to resume without asking.

## 3. Finish the branch
1. Full suite, lint and build; whole-branch self-review (skill `eng-review`), and an independent review when the change is risky; documents updated (skill `eng-docs`).
2. Then ask the user which they want: **push and open a PR** (recommended), **keep the branch** local as it is, or **discard** it. Push only after their answer. Merges into `main` or a shared branch happen only through the PR, never locally.
3. Discard only on the user's explicit request, and only local work: the branch, its commits (`git log --oneline <base>..<branch>`) and any worktree. Check each worktree for uncommitted changes (`git -C <worktree> status --short`), list everything that will go, and delete only after the user confirms that list. A pushed branch or an open PR is a separate decision with its own confirmation. Deleted local commits survive in the reflog for a limited time only.
4. Parallel work in one repo (two sessions or agents at once): give each its own worktree (`git worktree add ../<repo>-<branch> -b <branch> <base>`), outside the repo or in a git-ignored folder, and remove it once its PR is merged.

Adapted, in our own words and with eng-os gates added, from the writing-plans, executing-plans, subagent-driven-development and finishing-a-development-branch skills of obra/superpowers v7.0.2 (MIT licence, copyright 2025 Jesse Vincent).
