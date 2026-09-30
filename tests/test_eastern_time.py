import unittest
from datetime import datetime, timezone, timedelta
from scripts.eastern_time import eastern
from scripts.collect_usage import week_start


class EasternTests(unittest.TestCase):
    def test_offsets_and_transition_instants(self):
        zone = eastern()
        cases = [
            ('2026-01-15T12:00:00+00:00', '2026-01-15T07:00:00-05:00', 0),
            ('2026-07-15T12:00:00+00:00', '2026-07-15T08:00:00-04:00', 0),
            ('2026-03-08T06:59:59+00:00', '2026-03-08T01:59:59-05:00', 0),
            ('2026-03-08T07:00:00+00:00', '2026-03-08T03:00:00-04:00', 0),
            ('2026-11-01T05:30:00+00:00', '2026-11-01T01:30:00-04:00', 0),
            ('2026-11-01T06:30:00+00:00', '2026-11-01T01:30:00-05:00', 1),
            ('2027-01-01T02:00:00+00:00', '2026-12-31T21:00:00-05:00', 0),
            ('2006-03-20T12:00:00+00:00', '2006-03-20T07:00:00-05:00', 0),
        ]
        for source, expected, fold in cases:
            with self.subTest(source=source):
                utc = datetime.fromisoformat(source)
                local = utc.astimezone(zone)
                self.assertEqual(local.isoformat(), expected)
                self.assertEqual(local.fold, fold)
                self.assertEqual(local.astimezone(timezone.utc), utc)

    def test_week_boundary_across_dst(self):
        cutoff = datetime.fromisoformat('2026-03-08T18:00:00+00:00')
        self.assertEqual(week_start(cutoff, eastern()).isoformat(), '2026-03-02T05:00:00+00:00')

    def test_gap_fold_and_non_eastern_rejected(self):
        wall = datetime(2026, 3, 8, 2, 30, tzinfo=eastern())
        self.assertEqual(wall.utcoffset(), timedelta(hours=-5))
        self.assertEqual(wall.replace(fold=1).utcoffset(), timedelta(hours=-4))
        with self.assertRaises(ValueError):
            eastern('America/Chicago')
