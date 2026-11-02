import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'apps/milestoneService/main.py'
from apps.milestoneService.main import inspect


class MilestonePrivacyTests(unittest.TestCase):
    def test_inspection_removes_records_older_than_retention(self):
        build_root = Path(os.environ['SAFEOS_BUILD_ROOT'])
        with tempfile.TemporaryDirectory(dir=build_root / 'tests') as temporary:
            log_path = Path(temporary) / 'milestones.log'
            old_timestamp = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
            log_path.write_text(f'{old_timestamp}\tboot\tBoot sequence started\n', encoding='utf-8')
            with patch.dict(os.environ, {'SAFEOS_MILESTONE_LOG': str(log_path)}):
                self.assertEqual(inspect(), [])
            self.assertFalse(log_path.exists())

    def test_record_requires_consent_and_can_be_inspected_and_cleared(self):
        build_root = Path(os.environ['SAFEOS_BUILD_ROOT'])
        with tempfile.TemporaryDirectory(dir=build_root / 'tests') as temporary:
            log_path = Path(temporary) / 'milestones.log'
            environment = {**os.environ, 'SAFEOS_MILESTONE_LOG': str(log_path)}

            denied = subprocess.run(
                [sys.executable, str(SCRIPT), 'record', 'boot'],
                env=environment,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(denied.returncode, 0)
            self.assertFalse(log_path.exists())

            allowed = subprocess.run(
                [sys.executable, str(SCRIPT), 'record', 'boot', '--consent'],
                env=environment,
                check=False,
            )
            self.assertEqual(allowed.returncode, 0)
            self.assertEqual(log_path.stat().st_mode & 0o777, 0o600)

            inspected = subprocess.run(
                [sys.executable, str(SCRIPT), 'inspect'],
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn('\tboot\t', inspected.stdout)

            subprocess.run([sys.executable, str(SCRIPT), 'clear'], env=environment, check=True)
            self.assertFalse(log_path.exists())


if __name__ == '__main__':
    unittest.main()