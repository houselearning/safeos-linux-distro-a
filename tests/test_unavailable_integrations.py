import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from safenotify.notify import notify
from safeshell.jiraffescript import run_script
from system.cloud_manager import CloudServiceUnavailable, teacher_dashboard
from system.driver_manager import HardwareDetectionUnavailable, detect_profile
from system.security_suite import SecurityEngineUnavailable, quarantine_site


ROOT = Path(__file__).resolve().parents[1]


class UnavailableIntegrationTests(unittest.TestCase):
    def test_cloud_sync_reports_unavailable_without_claiming_success(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / 'scripts/cloud_sync.py')],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn('no service endpoint', result.stderr)
        self.assertNotIn('policies applied', result.stdout)

    def test_teacher_dashboard_has_no_fabricated_data(self):
        with self.assertRaises(CloudServiceUnavailable):
            teacher_dashboard()

    def test_site_quarantine_does_not_claim_to_work_without_engine(self):
        with self.assertRaisesRegex(SecurityEngineUnavailable, 'was not scanned or quarantined'):
            quarantine_site('example.invalid')

    def test_driver_manager_does_not_fabricate_hardware_profiles(self):
        with self.assertRaisesRegex(HardwareDetectionUnavailable, 'does not detect or select drivers'):
            detect_profile('chromebook')

    def test_jiraffescript_does_not_echo_commands_as_execution(self):
        with self.assertRaisesRegex(RuntimeError, 'was not parsed or executed'):
            run_script('untrusted.jf')

    @patch('safenotify.notify.subprocess.run')
    @patch('safenotify.notify.shutil.which', return_value='/usr/bin/notify-send')
    def test_notification_uses_desktop_service_without_shell(self, _which, run):
        notify('Update available', 'Debian package updates are ready')

        run.assert_called_once_with(
            ['/usr/bin/notify-send', '--app-name=SafeOS', 'Update available', 'Debian package updates are ready'],
            check=True,
        )


if __name__ == '__main__':
    unittest.main()