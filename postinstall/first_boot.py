#!/usr/bin/env python3
"""Interactive first-run configuration for the SafeOS XFCE live session."""

import json
import os
import pwd
import re
import shutil
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


STATE_FILE = Path('/var/lib/safeos/first-run.json')
SUPPORTED_LOCALES = {
    'en_US.UTF-8': 'English (United States)',
    'en_GB.UTF-8': 'English (United Kingdom)',
    'es_ES.UTF-8': 'Spanish',
    'fr_FR.UTF-8': 'French',
    'de_DE.UTF-8': 'German',
}
SUPPORTED_KEYBOARDS = {
    'us': 'English (US)',
    'gb': 'English (UK)',
    'de': 'German',
    'es': 'Spanish',
    'fr': 'French',
}


def validate_configuration(config, require_privacy=True):
    errors = []
    username = config.get('username', '')
    display_name = config.get('display_name', '')
    password = config.get('password', '')
    hostname = config.get('hostname', '')

    if not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', username):
        errors.append('Choose a username using lowercase letters, digits, _ or -, starting with a letter or _.')
    if not display_name.strip() or any(ord(char) < 32 for char in display_name):
        errors.append('Enter a display name without control characters.')
    if len(password) < 10 or any(char in password for char in '\r\n:'):
        errors.append('Use a password of at least 10 characters; colons and line breaks are not supported.')
    if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?', hostname):
        errors.append('Enter a device name of 1-63 letters, digits, or internal hyphens.')
    if config.get('locale') not in SUPPORTED_LOCALES:
        errors.append('Choose a supported system language.')
    if config.get('keyboard') not in SUPPORTED_KEYBOARDS:
        errors.append('Choose a supported keyboard layout.')
    try:
        ZoneInfo(config.get('timezone', ''))
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        errors.append('Enter a valid time zone, such as Europe/London or America/Los_Angeles.')
    if require_privacy and config.get('privacy_acknowledged') is not True:
        errors.append('Review the privacy summary before continuing.')
    if not isinstance(config.get('offline'), bool):
        errors.append('Choose whether to continue setup offline.')
    if not isinstance(config.get('large_text'), bool):
        errors.append('Choose a text-size preference.')
    return errors


def _atomic_write(path, contents, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f'.{path.name}.{os.getpid()}.tmp')
    try:
        with temporary.open('w', encoding='utf-8') as output:
            output.write(contents)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _account_exists(username):
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False


def _configure_locale(locale, root, runner):
    locale_gen = root / 'etc/locale.gen'
    existing = locale_gen.read_text(encoding='utf-8') if locale_gen.exists() else ''
    retained = []
    for line in existing.splitlines():
        fields = line.lstrip('# ').split()
        if fields and fields[0] == locale:
            continue
        retained.append(line)
    retained.append(f'{locale} UTF-8')
    _atomic_write(locale_gen, '\n'.join(retained) + '\n')
    runner(['locale-gen'], check=True)
    _atomic_write(root / 'etc/default/locale', f'LANG={locale}\n')


def _write_user_font(username, large_text, root):
    if not large_text:
        return
    try:
        account = pwd.getpwnam(username)
    except KeyError:
        return
    settings = root / account.pw_dir.lstrip('/') / '.config/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml'
    settings.parent.mkdir(parents=True, exist_ok=True)
    contents = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<channel name="xsettings" version="1.0">\n'
        '  <property name="Gtk" type="empty">\n'
        '    <property name="FontName" type="string" value="Sans 14"/>\n'
        '  </property>\n'
        '</channel>\n'
    )
    _atomic_write(settings, contents, 0o644)
    for directory in (settings.parent, settings.parent.parent, settings.parent.parent.parent):
        os.chown(directory, account.pw_uid, account.pw_gid)
    os.chown(settings, account.pw_uid, account.pw_gid)


def apply_configuration(config, root=Path('/'), runner=subprocess.run, user_exists=_account_exists):
    if os.geteuid() != 0:
        raise PermissionError('System configuration must be applied by the administrator.')
    errors = validate_configuration(config)
    if errors:
        raise ValueError('\n'.join(errors))

    state_file = root / STATE_FILE.relative_to('/')
    if state_file.exists():
        raise FileExistsError('SafeOS first-run setup is already complete.')
    username = config['username']
    if user_exists(username):
        raise ValueError(f'The account {username} already exists. Choose another username.')

    _configure_locale(config['locale'], root, runner)
    runner(['timedatectl', 'set-timezone', config['timezone']], check=True)
    _atomic_write(root / 'etc/timezone', config['timezone'] + '\n')
    runner(['localectl', 'set-x11-keymap', config['keyboard']], check=True)
    _atomic_write(
        root / 'etc/default/keyboard',
        'XKBMODEL="pc105"\n'
        f'XKBLAYOUT="{config["keyboard"]}"\n'
        'XKBVARIANT=""\nXKBOPTIONS=""\nBACKSPACE="guess"\n',
    )
    runner(['hostnamectl', 'set-hostname', config['hostname']], check=True)
    _atomic_write(root / 'etc/hostname', config['hostname'] + '\n')
    _atomic_write(
        root / 'etc/lightdm/lightdm.conf.d/99-safeos-first-run.conf',
        '[Seat:*]\nautologin-user=\nautologin-user-timeout=0\n',
    )

    user_created = False
    try:
        runner(
            [
                'useradd', '--create-home', '--shell', '/bin/bash',
                '--comment', config['display_name'], '--groups', 'sudo', username,
            ],
            check=True,
        )
        user_created = True
        runner(
            ['chpasswd'],
            input=f'{username}:{config["password"]}\n',
            text=True,
            check=True,
        )
        _write_user_font(username, config['large_text'], root)
        safe_state = {key: value for key, value in config.items() if key != 'password'}
        _atomic_write(state_file, json.dumps(safe_state, indent=2) + '\n', 0o644)
    except Exception:
        if user_created:
            runner(['userdel', '--remove', username], check=False)
        raise


def _network_status():
    if not shutil.which('nmcli'):
        return 'NetworkManager is unavailable. You can continue offline.'
    result = subprocess.run(
        ['nmcli', '-t', '-f', 'DEVICE,TYPE,STATE', 'device', 'status'],
        check=False,
        capture_output=True,
        text=True,
        timeout=8,
    )
    if result.returncode != 0:
        return 'Network status could not be read. You can continue offline.'
    lines = [line.replace(':', '  ', 2) for line in result.stdout.splitlines() if line.strip()]
    return '\n'.join(lines) if lines else 'No network devices were reported. You can continue offline.'


def _network_connected():
    if not shutil.which('nmcli'):
        return False
    result = subprocess.run(
        ['nmcli', '-t', '-f', 'STATE', 'general'],
        check=False,
        capture_output=True,
        text=True,
        timeout=8,
    )
    return result.returncode == 0 and result.stdout.strip().lower().startswith('connected')


def _live_persistence_available():
    return os.path.ismount('/lib/live/mount/persistence')


def _show_error(Gtk, parent, message):
    dialog = Gtk.MessageDialog(
        transient_for=parent,
        modal=True,
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.CLOSE,
        text='Setup could not be completed',
    )
    dialog.format_secondary_text(str(message))
    dialog.run()
    dialog.destroy()


def _run_wizard():
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        gi.require_version('GdkPixbuf', '2.0')
        from gi.repository import Gdk, GdkPixbuf, Gtk
    except (ImportError, ValueError) as error:
        raise RuntimeError('GTK 3 Python bindings are not installed in this image.') from error

    window = Gtk.Window(title='SafeOS Setup')
    window.set_default_size(1080, 680)
    window.set_position(Gtk.WindowPosition.CENTER)
    window.set_resizable(True)
    window.set_size_request(860, 600)
    window.get_style_context().add_class('safeos-window')

    style_provider = Gtk.CssProvider()
    style_provider.load_from_data(b"""
        * { font-family: "Cantarell", "DejaVu Sans", sans-serif; }
        .safeos-window { background-color: #f3f8f6; color: #102d3a; }
        .safeos-shell { background-color: #f3f8f6; }
        .safeos-rail { background-color: #071c2a; padding: 24px 20px; }
        .safeos-brand { color: #f3f8f6; font-size: 23px; font-weight: 800; }
        .safeos-kicker { color: #50d3d5; font-size: 10px; font-weight: 700; }
        .safeos-rail-note { color: #a7bdc5; font-size: 11px; }
        button.safeos-step { background-image: none; background-color: transparent; color: #bdd0d4; border: 1px solid transparent; border-radius: 7px; padding: 10px 12px; }
        button.safeos-step:hover { background-color: #123447; color: #f5fbfa; }
        button.safeos-step-active { background-image: none; background-color: #bce746; color: #092431; font-weight: 700; }
        button.safeos-step-done { color: #64d5d3; }
        .safeos-main { background-color: #f3f8f6; padding: 38px 44px 24px 44px; }
        .safeos-eyebrow { color: #087c89; font-size: 10px; font-weight: 700; }
        .safeos-position { color: #506873; font-size: 11px; font-weight: 700; }
        .safeos-page-title { color: #0c2b3b; font-size: 29px; font-weight: 700; }
        .safeos-page-summary { color: #51666f; font-size: 14px; }
        .safeos-copy { color: #29444f; font-size: 13px; }
        .safeos-progress trough { min-height: 5px; background-color: #dce8e5; border-radius: 3px; }
        .safeos-progress progress { background-color: #13aebe; border-radius: 3px; }
        .safeos-footer { padding-top: 16px; }
        button.safeos-secondary { background-image: none; background-color: #e2ece9; color: #173a47; border: 1px solid #d2e0dc; border-radius: 7px; padding: 9px 18px; }
        button.safeos-primary { background-image: none; background-color: #087f8d; color: #ffffff; border: 1px solid #087f8d; border-radius: 7px; padding: 9px 22px; font-weight: 700; }
        button.safeos-primary:disabled { background-color: #aebfbe; color: #f6f8f7; border-color: #aebfbe; }
        entry, combobox, textview { color: #102d3a; background-color: #ffffff; border: 1px solid #b7c9c8; border-radius: 5px; padding: 7px; }
        checkbutton { color: #173a47; }
    """)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    shell = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    shell.get_style_context().add_class('safeos-shell')
    window.add(shell)

    rail = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
    rail.set_size_request(270, -1)
    rail.get_style_context().add_class('safeos-rail')
    shell.pack_start(rail, False, False, 0)

    wallpaper_path = Path('/usr/share/safeos/setup-wallpaper.png')
    if wallpaper_path.is_file():
        artwork = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(wallpaper_path), 228, 145, True)
        brand_image = Gtk.Image.new_from_pixbuf(artwork)
        rail.pack_start(brand_image, False, False, 4)
    brand = Gtk.Label(label='SAFEOS')
    brand.set_xalign(0)
    brand.get_style_context().add_class('safeos-brand')
    rail.pack_start(brand, False, False, 0)
    brand_kicker = Gtk.Label(label='DEVICE SETUP  /  LOCAL FIRST')
    brand_kicker.set_xalign(0)
    brand_kicker.get_style_context().add_class('safeos-kicker')
    rail.pack_start(brand_kicker, False, False, 0)

    step_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    rail.pack_start(step_list, True, True, 12)
    rail_note = Gtk.Label(label='Your choices stay on this device.\nNo SafeOS cloud account is required.')
    rail_note.set_xalign(0)
    rail_note.set_line_wrap(True)
    rail_note.get_style_context().add_class('safeos-rail-note')
    rail.pack_end(rail_note, False, False, 4)

    main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
    main.get_style_context().add_class('safeos-main')
    shell.pack_start(main, True, True, 0)

    header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    header_line = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    eyebrow = Gtk.Label(label='SAFEOS  /  FIRST-RUN')
    eyebrow.set_xalign(0)
    eyebrow.get_style_context().add_class('safeos-eyebrow')
    header_line.pack_start(eyebrow, True, True, 0)
    step_position = Gtk.Label(label='STEP 01 / 06')
    step_position.set_xalign(1)
    step_position.get_style_context().add_class('safeos-position')
    header_line.pack_end(step_position, False, False, 0)
    header.pack_start(header_line, False, False, 0)

    page_heading = Gtk.Label()
    page_heading.set_xalign(0)
    page_heading.get_style_context().add_class('safeos-page-title')
    header.pack_start(page_heading, False, False, 0)
    page_summary = Gtk.Label()
    page_summary.set_xalign(0)
    page_summary.set_line_wrap(True)
    page_summary.get_style_context().add_class('safeos-page-summary')
    header.pack_start(page_summary, False, False, 0)
    progress = Gtk.ProgressBar()
    progress.get_style_context().add_class('safeos-progress')
    header.pack_start(progress, False, False, 0)
    main.pack_start(header, False, False, 0)

    page_stack = Gtk.Stack()
    page_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
    page_stack.set_transition_duration(160)
    page_stack.set_vexpand(True)
    main.pack_start(page_stack, True, True, 0)

    footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    footer.get_style_context().add_class('safeos-footer')
    main.pack_end(footer, False, False, 0)
    back_button = Gtk.Button(label='Back')
    back_button.get_style_context().add_class('safeos-secondary')
    footer.pack_start(back_button, False, False, 0)
    next_button = Gtk.Button(label='Continue')
    next_button.get_style_context().add_class('safeos-primary')
    footer.pack_end(next_button, False, False, 0)

    page_order = []
    page_titles = {}
    page_descriptions = {
        'welcome': 'A few choices will prepare this device for its first session.',
        'region': 'Set the language, keyboard, time zone, and device name.',
        'network': 'Connect with NetworkManager or choose to continue offline.',
        'account': 'Create the local account that will use this device.',
        'privacy': 'Review what setup saves and what it does not collect.',
        'accessibility': 'Choose a text preference before entering the desktop.',
    }
    page_complete = {}
    step_buttons = {}
    current_page = [None]
    furthest_page = [0]
    fields = {}

    def update_navigation():
        if current_page[0] is None:
            return
        current_index = page_order.index(current_page[0])
        step_position.set_text(f'STEP {current_index + 1:02d} / {len(page_order):02d}')
        progress.set_fraction((current_index + 1) / max(1, len(page_order)))
        page_heading.set_text(page_titles[current_page[0]])
        page_summary.set_text(page_descriptions[current_page[0]])
        back_button.set_sensitive(current_index > 0)
        next_button.set_label('Finish setup' if current_index == len(page_order) - 1 else 'Continue')
        next_button.set_sensitive(page_complete[current_page[0]])
        for index, name in enumerate(page_order):
            button = step_buttons[name]
            context = button.get_style_context()
            context.remove_class('safeos-step-active')
            context.remove_class('safeos-step-done')
            if index == current_index:
                context.add_class('safeos-step-active')
            elif index < current_index and page_complete[name]:
                context.add_class('safeos-step-done')
            button.set_sensitive(index <= furthest_page[0])

    def set_page_complete(name, complete):
        page_complete[name] = bool(complete)
        update_navigation()

    def show_page(name):
        if name not in page_order or page_order.index(name) > furthest_page[0]:
            return
        current_page[0] = name
        page_stack.set_visible_child_name(name)
        update_navigation()
        if name == 'network':
            refresh_network_status()
        elif name == 'account':
            update_account_page()

    def go_back(_button=None):
        if current_page[0] is None:
            return
        current_index = page_order.index(current_page[0])
        if current_index > 0:
            show_page(page_order[current_index - 1])

    def go_forward(_button=None):
        if current_page[0] is None or not page_complete[current_page[0]]:
            return
        current_index = page_order.index(current_page[0])
        if current_index == len(page_order) - 1:
            on_apply()
            return
        furthest_page[0] = max(furthest_page[0], current_index + 1)
        show_page(page_order[current_index + 1])

    def add_page(name, title, child):
        child.get_style_context().add_class('safeos-page')
        page_stack.add_named(child, name)
        page_order.append(name)
        page_titles[name] = title
        page_complete[name] = name == 'welcome' or name == 'accessibility'
        step_button = Gtk.Button()
        step_button.set_relief(Gtk.ReliefStyle.NONE)
        step_button.set_halign(Gtk.Align.FILL)
        step_button.get_style_context().add_class('safeos-step')
        step_label = Gtk.Label(label=f'{len(page_order):02d}    {title.upper()}')
        step_label.set_xalign(0)
        step_button.add(step_label)
        step_button.connect('clicked', lambda _button, target=name: show_page(target))
        step_list.pack_start(step_button, False, False, 0)
        step_buttons[name] = step_button
        return name

    def section(text):
        label = Gtk.Label(label=text)
        label.set_xalign(0)
        label.set_line_wrap(True)
        label.set_max_width_chars(76)
        label.get_style_context().add_class('safeos-copy')
        return label

    def page_box():
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_border_width(24)
        return box

    welcome = page_box()
    welcome.pack_start(section('Welcome to SafeOS. This setup creates a local account and applies your language, keyboard, time zone, and device name.'), False, False, 0)
    if _live_persistence_available():
        persistence_text = 'A live persistence mount is available. Changes can be retained by that configured persistence store.'
    else:
        persistence_text = 'This is a live session without a detected persistence mount. Accounts and system settings may be lost at reboot; the Debian Installer in this image has not been certified to install the custom SafeOS profile.'
    welcome.pack_start(section(persistence_text), False, False, 0)
    welcome.pack_start(section('The setup wizard does not enable telemetry or connect to a SafeOS cloud service.'), False, False, 0)
    add_page('welcome', 'Welcome', welcome)

    region = page_box()
    region_grid = Gtk.Grid(column_spacing=12, row_spacing=12)
    region.pack_start(region_grid, False, False, 0)
    locale = Gtk.ComboBoxText()
    for value, label in SUPPORTED_LOCALES.items():
        locale.append(value, label)
    locale.set_active_id('en_US.UTF-8')
    keyboard = Gtk.ComboBoxText()
    for value, label in SUPPORTED_KEYBOARDS.items():
        keyboard.append(value, label)
    keyboard.set_active_id('us')
    timezone = Gtk.Entry()
    timezone.set_text('Etc/UTC')
    hostname = Gtk.Entry()
    hostname.set_text('safeos-device')
    for row, (label, widget) in enumerate((
        ('Language', locale),
        ('Keyboard layout', keyboard),
        ('Time zone', timezone),
        ('Device name', hostname),
    )):
        region_grid.attach(section(label), 0, row, 1, 1)
        region_grid.attach(widget, 1, row, 1, 1)
    fields.update(locale=locale, keyboard=keyboard, timezone=timezone, hostname=hostname)
    add_page('region', 'Language and device', region)

    def update_region_page(_widget=None):
        try:
            ZoneInfo(timezone.get_text().strip())
            timezone_valid = True
        except (ZoneInfoNotFoundError, ValueError):
            timezone_valid = False
        hostname_valid = bool(re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?', hostname.get_text().strip()))
        set_page_complete(
            'region',
            locale.get_active_id() in SUPPORTED_LOCALES
            and keyboard.get_active_id() in SUPPORTED_KEYBOARDS
            and timezone_valid
            and hostname_valid,
        )

    for widget in (timezone, hostname):
        widget.connect('changed', update_region_page)
    locale.connect('changed', update_region_page)
    keyboard.connect('changed', update_region_page)
    update_region_page()

    network = page_box()
    network.pack_start(section('NetworkManager handles wired and Wi-Fi connections. Open Network Connections to join a network, or continue offline.'), False, False, 0)
    network_status = Gtk.Label(label=_network_status())
    network_status.set_xalign(0)
    network_status.set_selectable(True)
    network_status.set_line_wrap(True)
    network.pack_start(network_status, False, False, 0)
    network_buttons = Gtk.Box(spacing=8)
    refresh = Gtk.Button(label='Refresh status')
    def refresh_network_status(_button=None):
        network_status.set_text(_network_status())
        set_page_complete('network', _network_connected() or offline.get_active())
    refresh.connect('clicked', refresh_network_status)
    connect_network = Gtk.Button(label='Open Network Connections')
    def open_network_editor(_button):
        if not shutil.which('nm-connection-editor'):
            _show_error(Gtk, window, 'Network Connections is not installed. Wired connections are managed automatically; setup can continue offline.')
            return
        subprocess.Popen(['nm-connection-editor'], start_new_session=True)
    connect_network.connect('clicked', open_network_editor)
    network_buttons.pack_start(refresh, False, False, 0)
    network_buttons.pack_start(connect_network, False, False, 0)
    network.pack_start(network_buttons, False, False, 0)
    offline = Gtk.CheckButton(label='Continue setup offline')
    network.pack_start(offline, False, False, 0)
    fields['offline'] = offline
    add_page('network', 'Network', network)
    set_page_complete('network', _network_connected())
    offline.connect('toggled', refresh_network_status)

    account = page_box()
    account.pack_start(section('Create a local account. The password is sent only to the system password service and is not written to the setup record.'), False, False, 0)
    account_grid = Gtk.Grid(column_spacing=12, row_spacing=12)
    account.pack_start(account_grid, False, False, 0)
    username = Gtk.Entry()
    username.set_text('safeos')
    display_name = Gtk.Entry()
    display_name.set_text('SafeOS User')
    password = Gtk.Entry()
    password.set_visibility(False)
    password.set_input_purpose(Gtk.InputPurpose.PASSWORD)
    password_again = Gtk.Entry()
    password_again.set_visibility(False)
    password_again.set_input_purpose(Gtk.InputPurpose.PASSWORD)
    for row, (label, widget) in enumerate((
        ('Username', username),
        ('Display name', display_name),
        ('Password', password),
        ('Confirm password', password_again),
    )):
        account_grid.attach(section(label), 0, row, 1, 1)
        account_grid.attach(widget, 1, row, 1, 1)
    account_error = section('')
    account.pack_start(account_error, False, False, 0)
    fields.update(username=username, display_name=display_name, password=password, password_again=password_again)
    add_page('account', 'Local account', account)

    privacy = page_box()
    privacy_text = Gtk.TextView()
    privacy_text.set_editable(False)
    privacy_text.set_cursor_visible(False)
    privacy_text.set_wrap_mode(Gtk.WrapMode.WORD)
    privacy_text.get_buffer().set_text(
        'SafeOS does not send setup choices, passwords, usage, screen contents, or browsing activity to a SafeOS service. '
        'Network traffic from applications is governed by those applications and their providers. '
        'Your local password is processed by the operating system password service; this wizard does not store it in its configuration record. '
        'The account and system settings are written to the current root filesystem. A standard live session is temporary unless live persistence is configured.'
    )
    privacy_scroll = Gtk.ScrolledWindow()
    privacy_scroll.set_min_content_height(220)
    privacy_scroll.add(privacy_text)
    privacy.pack_start(privacy_scroll, True, True, 0)
    privacy_ack = Gtk.CheckButton(label='I have reviewed this privacy summary and want to continue.')
    privacy.pack_start(privacy_ack, False, False, 0)
    fields['privacy_ack'] = privacy_ack
    add_page('privacy', 'Privacy', privacy)
    set_page_complete('privacy', False)

    accessibility = page_box()
    accessibility.pack_start(section('Keyboard navigation is available throughout setup. Choose a larger default font for the new XFCE account if it improves readability.'), False, False, 0)
    large_text = Gtk.CheckButton(label='Use larger text in the XFCE desktop')
    accessibility.pack_start(large_text, False, False, 0)
    fields['large_text'] = large_text
    add_page('accessibility', 'Accessibility', accessibility)

    def current_configuration(include_password=False):
        config = {
            'username': username.get_text().strip(),
            'display_name': display_name.get_text().strip(),
            'locale': locale.get_active_id(),
            'keyboard': keyboard.get_active_id(),
            'timezone': timezone.get_text().strip(),
            'hostname': hostname.get_text().strip(),
            'offline': offline.get_active(),
            'privacy_acknowledged': privacy_ack.get_active(),
            'large_text': large_text.get_active(),
        }
        if include_password:
            config['password'] = password.get_text()
        return config

    def update_account_page(_widget=None):
        config = current_configuration(include_password=True)
        errors = validate_configuration(config, require_privacy=False)
        if password.get_text() != password_again.get_text():
            errors.append('The passwords do not match.')
        account_error.set_text(errors[0] if errors else '')
        set_page_complete('account', not errors)

    for widget in (username, display_name, password, password_again, timezone, hostname):
        widget.connect('changed', update_account_page)
    locale.connect('changed', update_account_page)
    keyboard.connect('changed', update_account_page)
    privacy_ack.connect('toggled', lambda button: set_page_complete('privacy', button.get_active()))

    def on_apply(_button=None):
        config = current_configuration(include_password=True)
        if password.get_text() != password_again.get_text():
            _show_error(Gtk, window, 'The passwords do not match.')
            return
        try:
            if os.geteuid() == 0:
                apply_configuration(config)
            else:
                result = subprocess.run(
                    ['sudo', '-n', sys.executable, str(Path(__file__).resolve()), '--apply-config'],
                    input=json.dumps(config),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode != 0:
                    raise RuntimeError(result.stderr.strip() or 'Administrator authorization failed.')
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
            _show_error(Gtk, window, error)
            Gtk.main_quit()
            return

        window.hide()
        if _live_persistence_available():
            summary = 'Setup is complete. Your choices were saved to the configured persistence-backed root filesystem.'
        else:
            summary = 'Setup is complete for this live session. The ISO has no detected persistence mount, so account and system changes may be lost at reboot. This image does not claim a tested SafeOS disk-install workflow.'
        dialog = Gtk.MessageDialog(
            transient_for=window,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.NONE,
            text='SafeOS setup complete',
        )
        dialog.format_secondary_text(summary)
        dialog.add_button('Continue this session', Gtk.ResponseType.CANCEL)
        dialog.add_button('Log out to the new account', Gtk.ResponseType.ACCEPT)
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.ACCEPT and shutil.which('xfce4-session-logout'):
            subprocess.Popen(['xfce4-session-logout', '--logout'], start_new_session=True)
        Gtk.main_quit()

    back_button.connect('clicked', go_back)
    next_button.connect('clicked', go_forward)

    def on_close(*_args):
        Gtk.main_quit()
        return False

    window.connect('delete-event', on_close)
    window.connect('destroy', lambda *_args: Gtk.main_quit())
    show_page('welcome')
    window.show_all()
    Gtk.main()


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv == ['--apply-config']:
        if os.geteuid() != 0:
            return 77
        try:
            apply_configuration(json.load(sys.stdin))
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
            print(str(error), file=sys.stderr)
            return 1
        return 0
    if argv:
        print('Usage: safeos-setup [--apply-config]', file=sys.stderr)
        return 64
    if STATE_FILE.exists():
        return 0
    try:
        _run_wizard()
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
