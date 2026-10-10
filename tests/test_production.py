import copy
import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / 'scripts/validate_production.py'


class ProductionChecks(unittest.TestCase):
    def setUp(self):
        self.assertTrue(MODULE.exists(), 'production validator has not been implemented')
        spec = importlib.util.spec_from_file_location('validator', MODULE)
        self.v = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.v)
        self.rows = [{'id': 'C001-01', 'category': 'figure', 'collection_id': 'C001', 'name': 'Example', 'redacted': False, 'source_sha256': 'a' * 64}]
        self.counts = {'figure': 1}
        self.canon = [{'id': 'CAN-001', 'status': 'approved', 'statement': 'Example rule', 'source': 'review record'}]
        self.tasks = [{'id': 'ST-001', 'status': 'backlog', 'depends_on': [], 'evidence': [], 'acceptance': ['Playable test']}]

    def test_valid_full_record(self):
        self.assertEqual([], self.v.validate(self.rows, self.counts, self.canon, self.tasks))

    def test_duplicate_identity_fails(self):
        self.assertIn('duplicate relic id', ' '.join(self.v.validate(self.rows * 2, self.counts, self.canon, self.tasks)))

    def test_missing_slot_fails_even_with_correct_count(self):
        self.rows[0]['id'] = 'C001-06'
        self.assertIn('invalid relic id', ' '.join(self.v.validate(self.rows, self.counts, self.canon, self.tasks)))

    def test_missing_collection_fails(self):
        rows = copy.deepcopy(self.rows) * 5
        for i, row in enumerate(rows):
            rows[i] = {**row, 'id': f'C002-{i+1:02}', 'collection_id': 'C002'}
        self.assertIn('missing expected relic id', ' '.join(self.v.validate(rows, {'figure': 5}, self.canon, self.tasks)))

    def test_duplicate_names_need_exact_shared_set_exception(self):
        rows = [self.rows[0], {**self.rows[0], 'id': 'C001-02', 'name': ' example '}]
        self.assertIn('duplicate relic name', ' '.join(self.v.validate(rows, {'figure': 2}, self.canon, self.tasks)))

    def test_public_redaction_is_enforced(self):
        self.assertIn('public index exposes', ' '.join(self.v.validate(self.rows, self.counts, self.canon, self.tasks, public=True)))

    def test_redacted_record_needs_source_fingerprint(self):
        row = {**self.rows[0], 'name': None, 'redacted': True}
        row.pop('source_sha256')
        self.assertIn('source fingerprint', ' '.join(self.v.validate([row], self.counts, self.canon, self.tasks, public=True)))

    def test_approval_requires_source(self):
        self.canon[0]['source'] = ''
        self.assertIn('approval needs source', ' '.join(self.v.validate(self.rows, self.counts, self.canon, self.tasks)))

    def test_completed_task_requires_evidence(self):
        self.tasks[0]['status'] = 'tested'
        self.assertIn('tested task needs evidence', ' '.join(self.v.validate(self.rows, self.counts, self.canon, self.tasks)))

    def test_unknown_dependency_fails(self):
        self.tasks[0]['depends_on'] = ['ST-999']
        self.assertIn('unknown dependency', ' '.join(self.v.validate(self.rows, self.counts, self.canon, self.tasks)))

    def test_dependency_cycle_fails(self):
        self.tasks.append({**self.tasks[0], 'id': 'ST-002', 'depends_on': ['ST-001']})
        self.tasks[0]['depends_on'] = ['ST-002']
        self.assertIn('dependency cycle', ' '.join(self.v.validate(self.rows, self.counts, self.canon, self.tasks)))

    def test_public_unknown_field_is_rejected(self):
        row = {k: v for k, v in self.rows[0].items() if k != 'name'}
        row.update(redacted=True, description='Unreleased private description')
        self.assertIn('public index exposes', ' '.join(self.v.validate([row], self.counts, self.canon, self.tasks, public=True)))

    def test_full_record_needs_source_fingerprint(self):
        self.rows[0].pop('source_sha256')
        self.assertIn('source fingerprint', ' '.join(self.v.validate(self.rows, self.counts, self.canon, self.tasks)))

    def test_approved_reference_needs_exact_file_hash_and_source(self):
        ref = {'id': 'REF-001', 'status': 'approved'}
        self.assertIn('approved reference needs', ' '.join(self.v.validate(self.rows, self.counts, self.canon, self.tasks, references=[ref])))

    def test_reference_approval_with_complete_evidence_passes(self):
        ref = {'id': 'REF-001', 'status': 'approved', 'approved_file': 'exact-file.png', 'sha256': 'a' * 64, 'source': 'User approval record'}
        self.assertEqual([], self.v.validate(self.rows, self.counts, self.canon, self.tasks, references=[ref]))

    def test_supersession_needs_resolved_ids_and_approval(self):
        self.assertIn('invalid supersession', ' '.join(self.v.validate(self.rows, self.counts, self.canon, self.tasks, supersessions=[{'old_id': 'unknown'}])))

    def test_public_unknown_metadata_is_rejected(self):
        row = {k: v for k, v in self.rows[0].items() if k != 'name'}
        row['redacted'] = True
        self.assertIn('public metadata exposes', ' '.join(self.v.validate([row], self.counts, self.canon, self.tasks, public=True, index_metadata={'private_story': 'secret'})))


if __name__ == '__main__':
    unittest.main()
