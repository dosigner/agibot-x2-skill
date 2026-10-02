#!/usr/bin/env python3
"""Offline official-link lookup. No network, ROS, robot access or copied schemas."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SENSOR_FEATURES = {'rgbd': ('4.1', 'RGB-D', 14), 'stereo': ('4.1', '전방 스테레오', 14),
                   'rear': ('4.1', '후방 RGB', 14), 'chest': ('4.2', None, 17),
                   'torso': ('4.2', None, 17), 'lidar': ('4.3', None, 16),
                   'gnss': ('4.3', None, 34), 'touch': ('4.3', None, 15)}


def read_routes():
    return json.loads((ROOT / 'references/data/routes.json').read_text(encoding='utf-8'))


def example_record(example, language=None, sensor=None):
    result = dict(example)
    langs = [language] if language else ['python', 'cpp']
    if sensor:
        if example['official_number'] != 14 or sensor not in ('rgbd', 'stereo', 'rear'):
            raise ValueError('Example 14 supports rgbd, stereo and rear only')
        result['urls'] = next(s['urls'] for s in example['subexamples'] if s['name'] == SENSOR_FEATURES[sensor][1])
        result['sensor'] = sensor
        result.pop('subexamples', None)
    result['urls'] = {lang: result['urls'][lang] for lang in langs}
    if 'subexamples' in result:
        result['subexamples'] = [dict(name=s['name'], urls={lang:s['urls'][lang] for lang in langs}) for s in result['subexamples']]
    result['validation'] = 'Official link only; open and review the example before use. Execution unverified.'
    if example['official_number'] == 7:
        result['execution_note'] = 'Review for hand-command publication; do not treat a sensor example as read-only. Robot support must be checked.'
    return result


def run(args):
    routes = read_routes()
    features = routes['features']
    if args.type:
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', args.type):
            raise ValueError('Type must be an unqualified interface name')
        if args.type not in routes['types']:
            raise ValueError('Unknown type; consult official documentation or installed SDK')
        return dict(routes['types'][args.type], validation='Link index only; no bundled field definitions. Inspect the official page and installed SDK.')
    if args.index:
        return [dict(id=k, name=v['name'], local_reference=v['local_reference']) for k, v in features.items()]
    if args.environment:
        return dict(robot='AGIBOT X2 Ultra Edition', environment='Inspect the current machine and target robot; no installed SDK, ROS version or path is assumed.', motion_execution=False)
    if args.search:
        words = args.search.casefold().split()
        result = []
        for fid, item in features.items():
            haystack = ' '.join([fid, item['name'], *item['keywords']]).casefold()
            score = sum(word in haystack for word in words)
            if score:
                result.append(dict(id=fid, name=item['name'], matched_terms=score, local_reference=item['local_reference']))
        return sorted(result, key=lambda x: (-x['matched_terms'], x['id']))
    examples = {e['official_number']: e for e in routes['examples']}
    if args.example is not None:
        if args.example not in examples:
            raise ValueError('Unknown official example number')
        return example_record(examples[args.example], args.language, args.sensor)
    if args.feature not in features:
        raise ValueError('Unknown feature; use --index')
    feature = features[args.feature]
    numbers = feature['primary_examples'] + feature['related_examples']
    if args.sensor:
        sensor_feature, _, number = SENSOR_FEATURES[args.sensor]
        if args.feature != sensor_feature and not (args.feature == '4.2' and args.sensor == 'lidar'):
            raise ValueError('Sensor does not belong to this feature')
        numbers = [number]
    return dict(id=feature['id'], name=feature['name'], reference=feature['local_reference'],
                sensor=args.sensor, sources=feature['sources'],
                examples=[example_record(examples[n], args.language, args.sensor if n == 14 else None) for n in numbers],
                supplemental_references=[r for r in routes['supplemental_references'] if r['feature'] == args.feature],
                contracts_included=False, validation='Official links only. Fetch the selected page or inspect installed definitions before using topic names, fields, units, QoS or rates.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--feature')
    selection.add_argument('--search')
    selection.add_argument('--example', type=int)
    selection.add_argument('--type', help='Type name; returns source links, not a definition')
    selection.add_argument('--index', action='store_true')
    selection.add_argument('--environment', action='store_true')
    parser.add_argument('--sensor', choices=tuple(SENSOR_FEATURES))
    parser.add_argument('--language', choices=('python', 'cpp'))
    args = parser.parse_args()
    if (args.sensor or args.language) and not (args.feature or args.example is not None):
        parser.error('--sensor/--language requires --feature or --example')
    try:
        result = run(args)
    except (ValueError, OSError, KeyError, StopIteration) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
