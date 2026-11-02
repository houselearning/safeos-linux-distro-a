import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from system.registry_editor import get_value, set_value


class LocalSettingsTests(unittest.TestCase):
    def test_allowed_preference_is_persisted_atomically(self):
        build_root = Path(os.environ['SAFEOS_BUILD_ROOT'])
        with tempfile.TemporaryDirectory(dir=build_root / 'tests') as temporary:
            settings_file = Path(temporary) / 'settings.json'
            with patch.dict(os.environ, {'SAFEOS_SETTINGS_FILE': str(settings_file)}):
                set_value('desktop.theme', 'classic')
                self.assertEqual(get_value('desktop.theme'), 'classic')
                self.assertEqual(settings_file.stat().st_mode & 0o777, 0o600)

    def test_unknown_preference_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unsupported SafeOS preference'):
            set_value('storage.raw-sector', 'overwrite')


if __name__ == '__main__':
    unittest.main()