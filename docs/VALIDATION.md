# Validation record for 1.1.0

This is the official-link public version. It differs from the earlier local full-reference package: manufacturer definitions and specification tables were removed, and the skill now requires the relevant official page or installed SDK before using exact contracts. Earlier package/client results are not reused as proof of the new behavior.

A fresh local clone passed 19 tests on Python 3.12.3 and 3.14.7. Rebuilding the 37-file skill ZIP produced the same SHA-256. Both Codex CLI and Claude Code resolved the RGB-D example link and correctly reported that TouchState fields and numeric joint limits were unavailable from the bundle in a network-disabled request. These were explicit invocations after installation by the host test harness.

Current results are recorded in [offline checks](validation/offline-checks.json) and [client probes](validation/client-probes.json). Tests cover all 23 features and both example languages, 36 example groups and camera sublinks, 93 type-link records without field definitions, sensor routing, invalid input, relocation, manifest verification, installation preservation and backup/rollback. The release check validates ZIP contents, checksum consistency, relative links and the public file list.

Client evaluation must distinguish offline link selection from technical-contract verification. For a network-disabled request, a correct answer identifies that manufacturer fields/limits are unavailable locally and avoids inventing them. A source or installation check is not proof of client discovery. A client invocation is not proof of a ROS build or robot behavior.

The [license review](license-review.md) records the public-scope decision. Cursor GUI/model invocation, Windows/macOS execution, GitHub-hosted CI, ROS/AimDK build, sensor reception and motion remain untested unless new results are explicitly appended. Network availability of official pages can change.
