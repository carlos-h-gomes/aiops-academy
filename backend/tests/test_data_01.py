from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_data_01 import (
    EXPECTED_COUNTS,
    validate_authored_unit,
    valid_fixture_counts,
    verify_invalid_case,
)


class Data01AuthoringTests(unittest.TestCase):
    def test_authored_portuguese_unit_matches_planned_catalog(self):
        result = validate_authored_unit()
        self.assertEqual(result["unit"], "data-01")
        self.assertEqual(result["catalog_status"], "available")
        self.assertEqual(result["available_units"], 50)
        self.assertEqual(result["authored_locale"], "pt-BR")
        self.assertEqual(result["planned_locales"], ["en", "es"])
        self.assertEqual(result["local_links"], 5)
        self.assertEqual(result["dated_primary_sources"], 3)

    def test_valid_relational_fixture_loads_with_expected_counts(self):
        self.assertEqual(valid_fixture_counts(), EXPECTED_COUNTS)

    def test_foreign_key_fixture_is_rejected(self):
        self.assertEqual(verify_invalid_case("foreign_key"), "rejected")

    def test_duplicate_business_key_fixture_is_rejected(self):
        self.assertEqual(verify_invalid_case("unique"), "rejected")

    def test_value_outside_check_fixture_is_rejected(self):
        self.assertEqual(verify_invalid_case("check"), "rejected")


if __name__ == "__main__":
    unittest.main()
