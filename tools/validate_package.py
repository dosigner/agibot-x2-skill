#!/usr/bin/env python3
"""Validate the official-link package offline; manufacturer extracts are excluded."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote, urldefrag, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILL = ROOT / 'skills/agibot-x2-interfaces'


def validate(skill, evidence=None):
    skill = Path(skill)
    errors = []
    if evidence is not None:
        return dict(passed=False, errors=['Raw source caches are not part of this link-only distribution.'], raw_source_audit='not_run')
    text = (skill / 'SKILL.md').read_text(encoding='utf-8')
    front = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
    if not front or 'name: agibot-x2-interfaces' not in front.group(1) or 'description:' not in front.group(1):
        errors.append('Invalid skill frontmatter')
    if skill.name != 'agibot-x2-interfaces':
        errors.append('Skill directory name mismatch')
    for forbidden in ('references/interfaces', 'references/data/contracts.json', 'references/data/example_catalog.json',
                      'references/data/ROBOT_REFERENCE_RULES_KO.md', 'references/data/source_manifest.json'):
        if (skill / forbidden).exists():
            errors.append('Manufacturer snapshot path must be excluded: ' + forbidden)
    for p in skill.rglob('*.md'):
        body = p.read_text(encoding='utf-8')
        if re.search(r'/home/(?!agi/)[^/\s]+/|/tmp/agibot[-]', body):
            errors.append('Machine-specific path: ' + p.relative_to(skill).as_posix())
        for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', body):
            parsed = urlsplit(target)
            if parsed.scheme:
                continue
            path = unquote(urldefrag(target)[0])
            resolved = (p.parent / path).resolve()
            if path and (not resolved.is_relative_to(skill.resolve()) or not resolved.exists()):
                errors.append('Broken relative link: ' + p.relative_to(skill).as_posix() + ' -> ' + target)
    routes = json.loads((skill / 'references/data/routes.json').read_text(encoding='utf-8'))
    allowed = {'distribution','modules','features','examples','types','robot_sources','supplemental_references'}
    if set(routes) != allowed or routes['distribution'] != 'official-links-only':
        errors.append('Unexpected routing schema')
    if len(routes['modules']) != 5 or len(routes['features']) != 23:
        errors.append('Module/feature classification changed')
    if len(routes['types']) != 93:
        errors.append('Expected 93 type-link records')
    examples = routes['examples']
    if sorted(e['official_number'] for e in examples) != list(range(1,37)):
        errors.append('Expected 36 official example groups')
    for name, item in routes['types'].items():
        if set(item) != {'name','sources','definition_included'} or item.get('definition_included') is not False or item['name'] != name:
            errors.append('Type records may contain only a name and source links: ' + name)
    for fid, feature in routes['features'].items():
        if set(feature) != {'id','name','keywords','sources','primary_examples','related_examples','local_reference'}:
            errors.append('Unexpected feature data; contract tables are excluded: ' + fid)
        if not (skill / feature['local_reference']).is_file():
            errors.append('Missing feature reference: ' + fid)
        primary = [e['official_number'] for e in examples if e['primary_feature'] == fid]
        related = [e['official_number'] for e in examples if fid in e['related_features']]
        if feature['primary_examples'] != primary or feature['related_examples'] != related:
            errors.append('Example routing mismatch: ' + fid)
    for item in examples:
        if not set(item) <= {'official_number','title_ko','primary_module','primary_feature','related_features','urls','subexamples'}:
            errors.append('Unexpected example payload')
    for key in ('joint_ranges','sensor_fov'):
        if not isinstance(routes['robot_sources'].get(key), str):
            errors.append('Robot reference must be a URL')
    return dict(passed=not errors, errors=errors, distribution='official-links-only',
                feature_count=len(routes['features']), example_groups=len(examples), type_link_count=len(routes['types']),
                bundled_type_definitions=0, bundled_robot_spec_tables=0, raw_source_audit='not_run')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill', type=Path, default=DEFAULT_SKILL)
    parser.add_argument('--evidence', type=Path, help='Unsupported for this link-only package; returns an explicit error')
    args = parser.parse_args()
    try:
        report = validate(args.skill, args.evidence)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        report = dict(passed=False, errors=[str(exc)])
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
