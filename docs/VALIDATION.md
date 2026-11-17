# Validation record for 1.2.2

[Claude Code comparison](CLAUDE_VALIDATION.md): the original sixteen prompts passed required selection and structured/numeric checks with Claude Code 2.1.326. Prose review found one HRI wording issue; only the baseline-subtraction/gravity-compensation paragraph was clarified. The original HRI prompt and a focused tilt counterexample passed again in both Claude and Codex. Discovery flags and narrow-shell permission fallbacks are recorded separately from skill quality.

The package's 26 offline regression tests and 11 frontmatter checks passed locally. Model probes are explicit, opt-in runs and are not executed by CI. Historical model records below retain their original version and limits.

## Historical 1.2.1 record

2026-11-17. [Behavior validation](BEHAVIOR_VALIDATION.md) reports fresh Codex CLI requests, observed skill reads and independent artifact checks. Baseline: 13/13 cases. Revised: 16/16 unique cases, with two additional control rechecks after notation cleanup. All 11 skills were exercised; two negative cases selected no X2 skill. This is a small-sample observation, not a general reliability estimate or a no-skill comparison.

The ordinary 26-case offline suite passed on macOS, including all specialist installation/backup/integrity tests. All 11 skill frontmatter checks also passed. The model probes are opt-in and are not silently executed by CI. The 1.2.1 public behavior cases and numeric oracles contain synthetic data only. Automatic selection was observed in fresh Codex CLI sessions; desktop picker UI and Claude/Cursor model invocation remain untested.

## Historical 1.2.0 record

2026-11-17, macOS, local source validation. Hardware and the shared dashboard were not accessed.

- 11 skills passed the skill-creator frontmatter validator.
- 26 unittest cases passed. The suite covers all 23 feature routes in both languages, all 36 example groups, 93 definition-free type records, 11 standalone archives, installation in relocated paths for Codex/Claude/Cursor, shared Cursor reuse, conflicts/backups, rollback, package identity/tampering, archive corruption and deterministic rebuilds.
- Release verification passed: 117 skill files and 116 relative Markdown links at this check. Public-file count may increase when this record is added to the manifest.
- Public export was tested without the author's original project evidence. The selected text/ZIP credential-pattern scan reported no findings. This is not a proof that every possible sensitive datum is detectable by patterns; the new skill prose and selected inventory were also reviewed.
- The field lessons cite 34 unique project-authored evidence files by workspace-relative path and SHA-256. These files were rehashed at review; the reports' historical robot results were not rerun.
- The knowledge review reconciled RGB-D registration versus measured boundary mismatch, initial versus later central-camera reception, LiDAR relative time units, and the current own-navigation choice. This was source/contract review, not independent model forward-testing.

Automatic discovery in running Codex/Claude/Cursor, Windows, current official website availability, ROS builds, live sensor/control/audio tests and new simulation/training were not run for this release. GitHub CI/release publication are verified separately from these local results.

## Historical 1.1.0 record


This is the official-link public version. It differs from the earlier local full-reference package: manufacturer definitions and specification tables were removed, and the skill now requires the relevant official page or installed SDK before using exact contracts. Earlier package/client results are not reused as proof of the new behavior.

A fresh local clone passed 19 tests on Python 3.12.3 and 3.14.7. Rebuilding the 37-file skill ZIP produced the same SHA-256. Both Codex CLI and Claude Code resolved the RGB-D example link and correctly reported that TouchState fields and numeric joint limits were unavailable from the bundle in a network-disabled request. These were explicit invocations after installation by the host test harness.

Current results are recorded in [offline checks](validation/offline-checks.json) and [client probes](validation/client-probes.json). Tests cover all 23 features and both example languages, 36 example groups and camera sublinks, 93 type-link records without field definitions, sensor routing, invalid input, relocation, manifest verification, installation preservation and backup/rollback. The release check validates ZIP contents, checksum consistency, relative links and the public file list.

Client evaluation must distinguish offline link selection from technical-contract verification. For a network-disabled request, a correct answer identifies that manufacturer fields/limits are unavailable locally and avoids inventing them. A source or installation check is not proof of client discovery. A client invocation is not proof of a ROS build or robot behavior.

The [license review](license-review.md) records the public-scope decision. Cursor GUI/model invocation, Windows/macOS execution, GitHub-hosted CI, ROS/AimDK build, sensor reception and motion remain untested unless new results are explicitly appended. Network availability of official pages can change.
