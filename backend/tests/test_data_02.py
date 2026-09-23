from pathlib import Path
import sqlite3
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from validate_data_02 import database, query, validate


class Data02Tests(unittest.TestCase):
    def test_lesson_and_reference_results(self):
        self.assertEqual(validate()['result_checks'], 5)

    def test_inner_omits_incident_without_runbook(self):
        with database() as db:
            self.assertEqual(query(db, 'inner', 'svc-ledger-demo'), [])

    def test_filter_on_preserves_incidents_without_matching_runbook(self):
        with database() as db:
            rows = query(db, 'left', 'svc-quotes', 'arquivado')
            self.assertEqual(len(rows), 5)
            self.assertTrue(all(row[2] is None for row in rows))
            misplaced = db.execute("SELECT i.incidente_id FROM incidentes i LEFT JOIN runbooks r ON r.runbook_id=i.runbook_id WHERE r.estado='arquivado'").fetchall()
            self.assertEqual(misplaced, [])

    def test_wrong_join_doubles_events(self):
        with database() as db:
            inflated = db.execute("SELECT COUNT(*) FROM incidentes i JOIN eventos e ON e.incidente_id=i.incidente_id JOIN runbooks r ON r.servico_id=i.servico_id WHERE i.incidente_id='inc-100'").fetchone()[0]
            self.assertEqual(inflated, 8)
            self.assertEqual(query(db, 'summary', 'svc-quotes')[0][1], 4)

    def test_equal_messages_are_distinct_events(self):
        with database() as db:
            self.assertEqual(db.execute("SELECT COUNT(*), COUNT(DISTINCT mensagem) FROM eventos WHERE incidente_id='inc-100'").fetchone(), (4, 3))

    def test_zero_events_count_is_not_count_star(self):
        with database() as db:
            self.assertEqual(db.execute("SELECT COUNT(*), COUNT(e.evento_id) FROM incidentes i LEFT JOIN eventos e ON e.incidente_id=i.incidente_id WHERE i.incidente_id='inc-300'").fetchone(), (1, 0))

    def test_parameters_are_literals_for_all_queries(self):
        with database() as db:
            for name in ('inner', 'left', 'summary'):
                for service in ('missing', "svc-quotes' OR 1=1 --", "'; DROP TABLE eventos; --"):
                    self.assertEqual(query(db, name, service), [])
            self.assertEqual(db.execute('SELECT COUNT(*) FROM eventos').fetchone()[0], 5)

    def test_writes_denied_and_connections_are_disposable(self):
        with database() as db:
            with self.assertRaises(sqlite3.OperationalError):
                db.execute('DELETE FROM eventos')
        with self.assertRaises(sqlite3.ProgrammingError):
            db.execute('SELECT 1')
        with database() as fresh:
            self.assertEqual(fresh.execute('SELECT COUNT(*) FROM eventos').fetchone()[0], 5)

    def test_unknown_query_rejected(self):
        with database() as db:
            with self.assertRaises(ValueError):
                query(db, '../data-01/schema', 'svc-quotes')


if __name__ == '__main__':
    unittest.main()
