import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from content_catalog import validate_module, write_catalog


class ContentCatalogTests(unittest.TestCase):
    def setUp(self):
        self.module = json.loads((ROOT / 'backend/content/modules/tools-n8n.json').read_text(encoding='utf-8'))

    def test_rejects_bad_identity_metadata_and_untrusted_links(self):
        mutations = [('id', '../escape'), ('id', 'start'), ('minutes', True),
                     ('recommended_after', 31), ('category', 'unknown'), ('body', ''),
                     ('sources', []), ('sources', [{'title': 'bad', 'url': 'javascript:alert(1)'}]),
                     ('sources', [{'title': 'bad', 'url': 'https://user:secret@example.org'}])]
        for field, value in mutations:
            with self.subTest(field=field, value=value):
                bad = copy.deepcopy(self.module)
                bad[field] = value
                with self.assertRaises(ValueError):
                    validate_module(bad, {'start'})

    def test_invalid_module_preserves_previous_catalog(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); modules = root / 'modules'; modules.mkdir()
            target = root / 'catalog.json'; target.write_text('previous valid content', encoding='utf-8')
            (modules / 'bad.json').write_text('{"id":"incomplete"}', encoding='utf-8')
            with self.assertRaises(ValueError):
                write_catalog([], modules, target)
            self.assertEqual(target.read_text(encoding='utf-8'), 'previous valid content')

    def test_duplicate_between_modules_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ('first', 'second'):
                (root / f'{name}.json').write_text(json.dumps(self.module), encoding='utf-8')
            with self.assertRaises(ValueError):
                write_catalog([], root, root / 'output.json')

    def test_catalog_has_core_extensions_and_tooling_without_changing_course(self):
        from author_manuals import MANUALS
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'manuals.json'
            write_catalog(MANUALS, ROOT / 'backend/content/modules', output)
            content = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(content[:len(MANUALS)], MANUALS)
            self.assertEqual(sum(m.get('category') == 'extension' for m in content), 6)
            self.assertEqual(sum(m.get('category') == 'tooling' for m in content), 7)
            self.assertEqual(sum(m.get('minutes', 0) for m in content if m.get('category') == 'extension'), 480)
            self.assertEqual(output.read_bytes(), (ROOT / 'backend/content/manuals.json').read_bytes())
