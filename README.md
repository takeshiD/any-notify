any-notify: Cross-Environment Notification CLI

=================================

Overview
--------
`any-notify` is a lightweight notification command that can be invoked from tools like Codex-CLI. It prefers GNOME (libnotify), and on WSL2 it falls back to a PowerShell popup.

Install / Run
-------------
- Run directly from the repo:
  - `python -m any_notify --help`
  - `python -m any_notify -t "Title" "Body"`
- If you want it on your PATH, run `pip install -e .` and then use the `any-notify` command.

Examples
--------
- Basic: `any-notify -t "Build" "Completed"`
- Urgency: `any-notify -u critical -t "Warning" "Disk space is low"`
- Timeout (ms): `any-notify -T 5000 -t "Info" "Auto cleanup finished"`
- Explicit backend: `any-notify -b gdbus -t "Title" "Body"`

Backend Selection
-----------------
1. Use `notify-send` if available
2. Otherwise use `gdbus` (org.freedesktop.Notifications)
3. On WSL2, use PowerShell COM Popup
4. Finally, print to stdout

Notes
-----
- `notify-send`/`gdbus` are provided by `libnotify`/`glib2`. Install them on Arch/Ubuntu as needed.
- On WSL2, the PowerShell popup is a simple dialog, not a toast notification.

