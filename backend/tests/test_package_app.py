import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))

from package_app import PUBLISHED_LESSON_PATHS, is_package_path, select_package_paths


class PackageSelectionTests(unittest.TestCase):
    def test_observability_lab_is_assertively_excluded_from_minimal_beta(self):
        candidates = [
            'labs/observability-pilot/README.md',
            'labs/observability-pilot/compose.yaml',
            'labs/observability-pilot/dashboard/index.html',
        ]
        self.assertEqual(select_package_paths(candidates), [])

    def test_published_lesson_bodies_are_selected_without_authoring_or_pilots(self):
        candidates = [
            *PUBLISHED_LESSON_PATHS,
            'backend/content/planned-units/future.json',
            'backend/content/fixtures/data-01/schema.sql',
            'backend/content/fixtures/security-06/scenarios.json',
            'backend/content/fixtures/agents-01-04/policy.json',
            'backend/tests/test_data_01.py',
            'backend/tests/test_security_06.py',
            'backend/tests/test_agents_01_04.py',
            'backend/app/services/agent_controller.py',
            'scripts/validate_data_01.py',
            'scripts/validate_security_06.py',
            'scripts/validate_agents_01_04.py',
            'labs/agents-processes-pilot/README.md',
        ]
        self.assertEqual(select_package_paths(candidates), sorted(PUBLISHED_LESSON_PATHS))

    def test_private_sensitive_qa_and_draft_paths_are_excluded(self):
        excluded = [
            'docs/ai/tasks/private.md',
            'data/academy.sqlite3',
            'backend/content/planned-units/future.json',
            'backend/.env',
            'frontend/.env.production',
            'scripts/qa/audit.html',
            'backend/_qa/probe.json',
            'backend/runtime.log',
            'backend/secret.key',
            'backend/certificate.pem',
            'backend/archive.p12',
            'backend/state.sqlite3',
            'backend/cache.pyc',
            'artifacts/release-manifest.json',
        ]
        for candidate in excluded:
            with self.subTest(candidate=candidate):
                self.assertFalse(is_package_path(candidate))

    def test_existing_public_boundaries_remain_selected(self):
        included = [
            'README.md',
            'docs/USER-MANUAL.md',
            'backend/app/main.py',
            'frontend/src/main.tsx',
            'scripts/bounded.py',
            'labs/real/fixtures/logs.json',
            'schemas/curriculum.schema.json',
            '.github/workflows/ci.yml',
            'artifacts/kit-manifest.json',
        ]
        self.assertEqual(select_package_paths(included), sorted(included))

    def test_unsafe_or_out_of_boundary_paths_are_rejected(self):
        for candidate in ['/absolute.txt', '../escape.txt', 'backend/../escape.txt']:
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                is_package_path(candidate)
        self.assertFalse(is_package_path('notes/private.md'))


if __name__ == '__main__':
    unittest.main()
