import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from scripts.check_image_manifest import REQUIRED_PACKAGES, main


class ImageManifestTests(unittest.TestCase):
    def test_complete_manifest_passes(self):
        build_root = Path(os.environ['SAFEOS_BUILD_ROOT'])
        with tempfile.TemporaryDirectory(dir=build_root / 'tests') as temporary:
            manifest = Path(temporary) / 'binary.packages'
            manifest.write_text(
                ''.join(f'{package} 1.0 amd64\n' for package in sorted(REQUIRED_PACKAGES)),
                encoding='utf-8',
            )
            with patch.object(sys, 'argv', ['check_image_manifest.py', str(manifest)]):
                self.assertEqual(main(), 0)

    def test_missing_installer_package_fails(self):
        build_root = Path(os.environ['SAFEOS_BUILD_ROOT'])
        with tempfile.TemporaryDirectory(dir=build_root / 'tests') as temporary:
            manifest = Path(temporary) / 'binary.packages'
            manifest.write_text('live-boot 1.0 amd64\n', encoding='utf-8')
            output = StringIO()
            with patch.object(sys, 'argv', ['check_image_manifest.py', str(manifest)]):
                with redirect_stderr(output):
                    self.assertEqual(main(), 1)
            self.assertIn('debian-installer-launcher', output.getvalue())


if __name__ == '__main__':
    unittest.main()