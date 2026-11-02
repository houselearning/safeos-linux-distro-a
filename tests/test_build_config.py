import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BuildConfigurationTests(unittest.TestCase):
    def test_installer_is_enabled_and_has_desktop_launcher(self):
        source = (ROOT / 'scripts/prepare_live_build.sh').read_text(encoding='utf-8')

        self.assertIn('--debian-installer live', source)
        self.assertIn('debian-installer-launcher', source)
        self.assertNotIn('--debian-installer false', source)

    def test_first_run_setup_is_packaged_and_autostarted(self):
        source = (ROOT / 'scripts/prepare_live_build.sh').read_text(encoding='utf-8')
        ui_source = (ROOT / 'postinstall/first_boot.py').read_text(encoding='utf-8')

        self.assertIn('python3-gi', source)
        self.assertIn('gir1.2-gtk-3.0', source)
        self.assertIn('network-manager-gnome', source)
        self.assertIn('postinstall/first_boot.py', source)
        self.assertIn('etc/xdg/autostart/safeos-setup.desktop', source)
        self.assertIn('Exec=/usr/local/bin/safeos-setup', source)
        self.assertIn('wallpapers/safeos-dark.png', source)
        self.assertIn('Gtk.Window(title=', ui_source)
        self.assertIn('Gtk.Stack()', ui_source)
        self.assertIn('safeos-rail', ui_source)
        self.assertNotIn('Gtk.Assistant()', ui_source)

    def test_xfce_session_and_window_manager_are_explicit_packages(self):
        package_list = (ROOT / 'live-build/config/package-lists/safeos.list.chroot').read_text(encoding='utf-8')

        self.assertIn('\nxfce4-session\n', f'\n{package_list}\n')
        self.assertIn('\nxfwm4\n', f'\n{package_list}\n')

    def test_live_build_uses_signed_fixed_debian_sources(self):
        source = (ROOT / 'scripts/prepare_live_build.sh').read_text(encoding='utf-8')

        self.assertIn('20261031T210000Z', source)
        self.assertIn('--mirror-chroot-security', source)
        self.assertIn('--mirror-binary-security', source)
        self.assertNotIn('--security false', source)

    def test_only_real_desktop_applications_get_menu_entries(self):
        source = (ROOT / 'scripts/prepare_live_build.sh').read_text(encoding='utf-8')

        for app in ('safebrowser', 'fileexplorer', 'calculator', 'spreadsheet', 'safewriter'):
            self.assertIn(f'write_launcher safeos-', source)
            self.assertIn(f" {app} '", source)
        self.assertNotIn('write_launcher safeos-store', source)
        self.assertNotIn('write_launcher safeos-safeai', source)
        self.assertIn('write_launcher safeos-terminal Terminal ', source)

    def test_hidden_services_are_not_added_to_the_image(self):
        source = (ROOT / 'scripts/prepare_live_build.sh').read_text(encoding='utf-8')

        for forbidden in ('milestone_service', 'milestone-service', 'safeos-session', '--hidden'):
            self.assertNotIn(forbidden, source)
        self.assertFalse((ROOT / 'desktop/autostart/milestone-service.sh').exists())
        self.assertFalse((ROOT / 'desktop/autostart/safeos-session.sh').exists())


if __name__ == '__main__':
    unittest.main()