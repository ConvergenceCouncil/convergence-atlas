"""Validate production metadata; never equate recovered sources with a built game."""
import argparse
import collections
import json
from pathlib import Path
import re
import sys
import unicodedata

COUNTS = {'figure': 785, 'original': 115, 'beast': 40, 'folklore': 20}
PATTERNS = {'figure': r'C(\d{3})-(0[1-5])', 'original': r'CR\d{3}', 'beast': r'MB\d{3}', 'folklore': r'CMF\d{3}'}


def expected_ids(counts):
    ids = set()
    for category, count in counts.items():
        for i in range(count):
            if category == 'figure':
                ids.add(f'C{i // 5 + 1:03}-{i % 5 + 1:02}')
            else:
                prefix = {'original': 'CR', 'beast': 'MB', 'folklore': 'CMF'}[category]
                ids.add(f'{prefix}{i + 1:03}')
    return ids


def validate(rows, counts, canon, tasks, public=False, shared_sets=None, references=None, supersessions=None, index_metadata=None):
    errors, names = [], collections.defaultdict(list)
    if public and index_metadata is not None:
        allowed = {'schema_version', 'visibility', 'source_label', 'source_sha256', 'coverage_meaning', 'relics'}
        if set(index_metadata) - allowed:
            errors.append('public metadata exposes unapproved fields')
    ids = [row.get('id') for row in rows]
    for id_, n in collections.Counter(ids).items():
        if n > 1:
            errors.append(f'duplicate relic id: {id_}')
    actual = collections.Counter(row.get('category') for row in rows)
    if dict(actual) != counts:
        errors.append(f'category counts differ: {dict(actual)}; expected {counts}')
    for missing in sorted(expected_ids(counts) - set(ids)):
        errors.append(f'missing expected relic id: {missing}')
    for row in rows:
        id_, category = row.get('id', ''), row.get('category')
        if category not in PATTERNS or not re.fullmatch(PATTERNS[category], id_):
            errors.append(f'invalid relic id: {id_}')
        if category == 'figure' and row.get('collection_id') != id_.split('-')[0]:
            errors.append(f'collection mismatch: {id_}')
        allowed_fields = {'id', 'category', 'collection_id', 'redacted', 'source_sha256'}
        if public and (row.get('redacted') is not True or set(row) - allowed_fields):
            errors.append(f'public index exposes private content: {id_}')
        if not re.fullmatch(r'[0-9a-f]{64}', row.get('source_sha256', '')):
            errors.append(f'record needs source fingerprint: {id_}')
        if row.get('redacted'):
            pass
        elif not isinstance(row.get('name'), str) or not row['name'].strip():
            errors.append(f'missing relic name: {id_}')
        else:
            normalized = ' '.join(unicodedata.normalize('NFKC', row['name']).casefold().split())
            names[normalized].append(id_)
    approved_shared = [set(item['ids']) for item in (shared_sets or []) if item.get('approval_source')]
    for name, matched in names.items():
        if len(matched) > 1 and set(matched) not in approved_shared:
            errors.append(f'duplicate relic name: {name}: {matched}')
    for row in canon:
        if row.get('status') not in ('approved', 'proposed', 'superseded', 'needs_review'):
            errors.append(f'invalid canon status: {row.get("id")}')
        if row.get('status') == 'approved' and not row.get('source'):
            errors.append(f'approval needs source: {row.get("id")}')
        if not row.get('statement'):
            errors.append(f'empty canon rule: {row.get("id")}')
    task_ids = [task.get('id') for task in tasks]
    if len(task_ids) != len(set(task_ids)):
        errors.append('duplicate task id')
    canon_ids = [row.get('id') for row in canon]
    if len(canon_ids) != len(set(canon_ids)):
        errors.append('duplicate canon id')
    refs = references or []
    ref_ids = [ref.get('id') for ref in refs]
    if len(ref_ids) != len(set(ref_ids)):
        errors.append('duplicate reference id')
    for ref in refs:
        if ref.get('status') not in ('approved', 'proposed', 'needs_review', 'superseded'):
            errors.append(f'invalid reference status: {ref.get("id")}')
        if ref.get('status') == 'approved' and (not ref.get('approved_file') or not ref.get('source') or not re.fullmatch(r'[0-9a-f]{64}', ref.get('sha256', ''))):
            errors.append(f'approved reference needs exact file, hash and approval source: {ref.get("id")}')
    known_ids = set(canon_ids + ref_ids)
    for supersession in supersessions or []:
        old, new = supersession.get('old_id'), supersession.get('new_id')
        if old not in known_ids or new not in known_ids or old == new or not supersession.get('source'):
            errors.append('invalid supersession: resolved distinct IDs and approval source required')
    graph = {task.get('id'): task.get('depends_on', []) for task in tasks}
    for task in tasks:
        if task.get('status') not in ('backlog', 'in_progress', 'blocked', 'review', 'tested'):
            errors.append(f'invalid production status: {task.get("id")}')
        if not task.get('acceptance'):
            errors.append(f'task needs acceptance criteria: {task.get("id")}')
        if task.get('status') == 'tested' and not task.get('evidence'):
            errors.append(f'tested task needs evidence: {task.get("id")}')
        for dependency in task.get('depends_on', []):
            if dependency not in graph:
                errors.append(f'unknown dependency: {dependency}')
    visited, active = set(), set()

    def visit(node):
        if node in active:
            errors.append(f'dependency cycle: {node}')
            return
        if node in visited:
            return
        active.add(node)
        for dependency in graph.get(node, []):
            visit(dependency)
        active.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--private-registry', type=Path)
    args = parser.parse_args()
    root = args.root / 'production'
    index = json.loads((args.private_registry or root / 'relic-index.json').read_text())
    canon_data = json.loads((root / 'canon.json').read_text())
    canon = canon_data['rules']
    tasks = json.loads((root / 'sunken-temple.json').read_text())['tasks']
    errors = validate(index['relics'], COUNTS, canon, tasks, public=not args.private_registry, shared_sets=index.get('shared_sets'), references=canon_data['reference_register'], supersessions=canon_data['supersessions'], index_metadata=index)
    print(f'Registry coverage: {len(index["relics"])}/960 source-derived identities')
    print('Name validation: ' + ('full private names checked' if args.private_registry else 'not run: public index is redacted'))
    print(f'Sunken Temple tested tasks: {sum(t["status"] == "tested" for t in tasks)}/{len(tasks)}; source recovery is not gameplay completion')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print('Production metadata validation passed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
