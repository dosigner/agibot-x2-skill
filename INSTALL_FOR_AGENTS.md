# Install and introduce the AGIBOT X2 skill

Use this procedure when the user requests installation or an update. It applies to Codex, Claude Code and Cursor. Preserve decisions already made in the conversation. Read the repository README for product scope; do not stop at summarizing it.

## 1. Resolve the destination

Identify the running client, OS, Python 3.10+ executable and target project from the session. Default to the current user project. The temporary download/clone directory is not the target project. Use personal scope only when requested. If there is no identifiable client or project, ask only for that missing information.

| Client | Project destination | Personal destination | Invocation |
|---|---|---|---|
| Codex | `<project>/.agents/skills/agibot-x2-interfaces` | `~/.agents/skills/agibot-x2-interfaces` | `$agibot-x2-interfaces` |
| Claude Code | `<project>/.claude/skills/agibot-x2-interfaces` | `~/.claude/skills/agibot-x2-interfaces` | `/agibot-x2-interfaces` |
| Cursor | `<project>/.cursor/skills/agibot-x2-interfaces` | `~/.cursor/skills/agibot-x2-interfaces` | `/agibot-x2-interfaces` |

Inspect the destination and other client discovery paths at project and personal scope for this name. Cursor also reads `.agents` and `.claude` skills. The installer detects shared copies only at the selected scope; report remaining duplicate or shadowing copies and resolve their provenance before claiming discovery. Preserve existing client settings and permissions.

Complete this step with a known client, scope and absolute project/destination path.

## 2. Obtain one identified version

Use the actual repository URL supplied by the user or the verified origin of the current checkout. The public repository is https://github.com/dosigner/agibot-x2-skill. Resolve the actual release metadata; source installation is available even if no Release has been published. For a local evaluation, use the supplied local source tree and label the result as a local simulation.

For GitHub, retrieve release metadata from the actual repository (GitHub UI/API or an already authenticated `gh` command). Resolve `latest` once to a concrete tag and save that metadata. For a requested tag, use that tag only. Obtain source tools from the same tag: clone the repository at the resolved tag, or use its source archive. Confirm `VERSION` before proceeding.

If a Release exists, download its `agibot-x2-interfaces.zip` and `.zip.sha256` assets using the URLs returned by that release's metadata. Versioned filenames are also supported when the metadata lists them. Verify the checksum before extraction, require exactly one top-level `agibot-x2-interfaces/` folder, reject absolute/traversal paths and symlinks, and extract into a new temporary directory. Compare the manifest version to `VERSION` and the selected `v<VERSION>` tag. A checksum provides byte integrity, not independent publisher authentication.

If no Release exists and no tag was requested, install from the repository checkout: record its commit and manifest version and state that this is a source installation. If a requested tag or asset is absent, report that fact; do not substitute another version silently. When only a skill ZIP is available, it contains no `tools/` directory. Use the source tools from the same release or the manual copy method in the README.

Complete this step with a local source root, verified skill folder, version, and provenance (release tag, commit, or local simulation). Never execute a guessed URL or a bracketed README placeholder.

## 3. Verify and install

Set `SKILL_SOURCE` to the verified extracted skill folder, or `<source-root>/skills/agibot-x2-interfaces` for a source installation. Use the available Python 3.10+ executable. From the source root, adapt these commands to the resolved client and absolute paths:

```bash
python3 "$SKILL_SOURCE/scripts/verify.py" --expected-version "$VERSION"
python3 tools/install_skill.py --client "$CLIENT" --project "$PROJECT" --source "$SKILL_SOURCE" --dry-run
python3 tools/install_skill.py --client "$CLIENT" --project "$PROJECT" --source "$SKILL_SOURCE"
```

These shell variables represent values you resolved; initialize them before running commands. For an explicitly selected personal installation, replace `--project "$PROJECT"` with `--user`.

Identical content returns `already identical` and is reused. Different content returns an error without changing it. If the user requested an update/replacement, inspect that difference and use `--backup-existing` to preserve the old folder outside skill discovery before installation. Otherwise report the conflict and the backup option; do not overwrite a user's edited skill. A different Cursor shared copy is a conflict even with this flag: resolve the existing copy instead of creating an ambiguous duplicate.

Complete this step only when the command succeeds and reports the actual installed or reused absolute path. Retain any backup path for the final response.

Some client sandboxes protect `.agents` or `.claude` even inside the project. If installation is blocked, use the client's normal per-command approval flow when available. Otherwise provide the exact terminal installation command and report installation as incomplete. Preserve sandbox settings; do not bypass a denied permission or silently change the client configuration.

## 4. Check the result

Run the installed verifier, then an offline lookup from a different working directory:

```bash
python3 "$INSTALLED/scripts/verify.py" --expected-version "$VERSION"
python3 "$INSTALLED/scripts/lookup.py" --feature 4.1 --sensor rgbd --language python
```

Require `passed: true` and a feature `4.1` result with `contracts_included: false` and the selected RGB-D example links. Confirm that `SKILL.md`, routing references and lookup tools exist at that installed path. This public version contains official links instead of manufacturer definitions and specification tables. It works offline for installation and link selection; exact X2 contracts require the selected official page or an installed SDK.

Separately test client discovery/invocation if the current client exposes a skill selector or an authorized new session. If a restart/new session is needed, explain how to open the target project and invoke the skill. Reading `SKILL.md` directly or completing an offline lookup does not prove automatic discovery. Keep ROS/SDK build, live sensor reception and robot motion marked untested unless independently performed under the user's task. Installation does not request robot access.

## 5. Finish with first-use guidance

Reply in the user's language with:

1. Client, version, provenance, scope and absolute installation path; backup path if used.
2. Checks actually run and their results. Separate file placement/integrity, offline lookup, client discovery and robot validation.
3. One copyable first request, using the client's invocation prefix: “Explain the AGIBOT X2 Ultra RGB-D data flow using the skill and the linked official documentation; do not access a robot.”
4. Three short examples: learning interfaces; editing an existing `camera_listener.py` while retaining decisions; designing a C++ camera/IMU algorithm with explicit inputs, timing and coordinate frames.
5. Any required new-session step or unresolved duplicate/conflict.

If tools, network, authentication or permissions prevent installation, state the exact unperformed step and give the minimum manual action from the README. Do not claim completion from the existence of a README or from planned commands.
