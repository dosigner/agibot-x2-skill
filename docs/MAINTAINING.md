# Maintain and publish the official-link package

Run from the repository root with Python 3.10+:

```bash
python3 tools/check_release.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The default checks require no ROS, robot, network or model calls. `references/data/routes.json` contains only navigation metadata. Update official links there and in the feature files when needed. Review upstream pages without copying their definitions or specification tables into this distribution. Manufacturer cache extraction/build tools are intentionally absent.

After an intentional skill change, update `VERSION`, the versioned asset entry in `public_files.json` and the README version references, then run `python3 tools/package_skill.py`. Never change bytes under a tag that has already been published. The verifier checks file hashes; `validate_package.py` also rejects manufacturer snapshot paths and unexpected schema payloads.

Export only selected publication files into a new directory:

```bash
python3 tools/export_release.py --output release/review/github-source
```

The exporter writes a source ZIP and checksum beside the exported tree and records its exact file inventory in `PUBLIC_MANIFEST.json`. Review it before publishing. Pattern scanning is limited and does not prove that every possible secret has been found. Raw logs, source HTML and historical full-reference releases stay in the authoring workspace.

The repository is intended to be public. The repository is https://github.com/dosigner/agibot-x2-skill. Rerun the checks and export the final selected source tree before creating a version tag and Release with the skill ZIP, checksum and source ZIP/checksum. Verify the live assets and repeat installation from the real repository URL when possible.

The AI installation procedure is in [INSTALL_FOR_AGENTS.md](../INSTALL_FOR_AGENTS.md). Sandbox write restrictions are reported as incomplete installation; do not change protections to make a model probe pass. The historical fixture `tests/fixtures/capture.py` is intentionally incomplete for an offline code-edit scenario, not a robot-ready capture template.
