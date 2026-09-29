import tempfile
import unittest
from pathlib import Path
from scripts.delivery_ledger import ledger


class DeliveryTests(unittest.TestCase):
    def test_claim_success_and_duplicate(self):
        root=Path(__file__).resolve().parents[1]/'private'
        root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as folder:
            db=Path(folder)/'receipts.sqlite'
            self.assertTrue(ledger(db,'claim','synthetic-key')['send_allowed'])
            self.assertFalse(ledger(db,'claim','synthetic-key')['send_allowed'])
            self.assertEqual(ledger(db,'complete','synthetic-key','synthetic-success')['status'],'sent')
            self.assertFalse(ledger(db,'claim','synthetic-key')['send_allowed'])
            self.assertTrue(ledger(db,'claim','different-trigger')['send_allowed'])

    def test_no_completion_without_pending(self):
        root=Path(__file__).resolve().parents[1]/'private'
        root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as folder:
            with self.assertRaises(ValueError):ledger(Path(folder)/'receipts.sqlite','complete','missing','success')


if __name__=='__main__':unittest.main()
