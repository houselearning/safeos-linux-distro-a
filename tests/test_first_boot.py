import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from postinstall.first_boot import STATE_FILE, apply_configuration, validate_configuration


class FirstBootTests(unittest.TestCase):
    def setUp(self):
        self.configuration = {
            'username': 'safeos-user',
            'display_name': 'SafeOS User',
            'password': 'correct-horse-battery',
            'locale': 'en_US.UTF-8',
            'keyboard': 'us',
            'timezone': 'Etc/UTC',
            'hostname': 'safeos-device',
            'privacy_acknowledged': True,
            'offline': True,
            'large_text': False,
        }

    def test_valid_configuration_passes(self):
        self.assertEqual(validate_configuration(self.configuration), [])

    def test_invalid_identity_and_timezone_are_rejected(self):
        invalid = {
            **self.configuration,
            'username': 'Not A User',
            'hostname': '-invalid-',
            'timezone': 'Not/A_Timezone',
        }

        errors = validate_configuration(invalid)

        self.assertTrue(any('username' in error for error in errors))
        self.assertTrue(any('device name' in error for error in errors))
        self.assertTrue(any('time zone' in error for error in errors))

    def test_password_rules_and_privacy_acknowledgement_are_enforced(self):
        invalid = {
            **self.configuration,
            'password': 'short',
            'privacy_acknowledged': False,
        }

        errors = validate_configuration(invalid)

        self.assertTrue(any('password' in error for error in errors))
        self.assertTrue(any('privacy' in error for error in errors))

    def test_account_password_is_not_written_to_setup_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner = Mock()
            with patch('postinstall.first_boot.os.geteuid', return_value=0):
                apply_configuration(
                    self.configuration,
                    root=root,
                    runner=runner,
                    user_exists=lambda _username: False,
                )

            state_file = root / STATE_FILE.relative_to('/')
            saved_state = json.loads(state_file.read_text(encoding='utf-8'))
            self.assertNotIn('password', saved_state)
            self.assertNotIn(self.configuration['password'], state_file.read_text(encoding='utf-8'))
            runner.assert_any_call(
                ['chpasswd'],
                input=f"{self.configuration['username']}:{self.configuration['password']}\n",
                text=True,
                check=True,
            )
            self.assertIn('en_US.UTF-8 UTF-8', (root / 'etc/locale.gen').read_text(encoding='utf-8'))
            self.assertIn('safeos-device', (root / 'etc/hostname').read_text(encoding='utf-8'))
            self.assertTrue((root / 'etc/lightdm/lightdm.conf.d/99-safeos-first-run.conf').is_file())

    def test_existing_account_does_not_change_system_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner = Mock()
            with patch('postinstall.first_boot.os.geteuid', return_value=0):
                with self.assertRaisesRegex(ValueError, 'already exists'):
                    apply_configuration(
                        self.configuration,
                        root=root,
                        runner=runner,
                        user_exists=lambda _username: True,
                    )

            runner.assert_not_called()
            self.assertFalse((root / STATE_FILE.relative_to('/')).exists())


if __name__ == '__main__':
    unittest.main()
