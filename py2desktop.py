#!/usr/bin/env python3

import gi
import os
import pathlib
import urllib.parse

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

class DragDropLauncher(Gtk.Window):
    def __init__(self):
        super().__init__(title="Python .desktop Launcher Creator")
        self.set_default_size(420, 220)
        self.set_border_width(20)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_name("MainWindow")

        self.set_dark_theme()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        label = Gtk.Label(label="Drag & Drop a Python (.py) file here\n\nA .desktop launcher will be created on your Desktop.")
        label.set_justify(Gtk.Justification.CENTER)
        label.set_name("InfoLabel")
        label.set_margin_top(10)
        label.set_margin_bottom(5)
        vbox.pack_start(label, True, True, 0)

        # Terminal checkbox
        self.terminal_checkbox = Gtk.CheckButton(label="Run script in terminal?")
        self.terminal_checkbox.set_active(True)
        vbox.pack_start(self.terminal_checkbox, False, False, 0)

        # Status label
        self.status = Gtk.Label(label="")
        self.status.set_name("StatusLabel")
        self.status.set_margin_top(10)
        self.status.set_halign(Gtk.Align.CENTER)
        self.status.set_valign(Gtk.Align.END)
        vbox.pack_start(self.status, False, False, 0)

        # Enable drag & drop
        target_entries = [Gtk.TargetEntry.new("text/uri-list", 0, 0)]
        self.drag_dest_set(Gtk.DestDefaults.ALL, target_entries, Gdk.DragAction.COPY)
        self.connect("drag-data-received", self.on_drag_data_received)

        self.show_all()

    def set_dark_theme(self):
        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        provider.load_from_data(b"""
            #MainWindow {
                background-color: #2e2e2e;
            }
            #InfoLabel {
                color: white;
                font-weight: bold;
                font-size: 16px;
            }
            #StatusLabel {
                color: #a0ffa0;
                font-weight: bold;
                font-size: 14px;
            }
            checkbutton, label {
                color: white;
            }
        """)
        Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        uris = data.get_uris()
        if not uris:
            self.update_status("No file detected in drop.", error=True)
            return

        path = urllib.parse.unquote(uris[0])
        if path.startswith("file://"):
            path = path[7:]
        path = pathlib.Path(path).expanduser().resolve()

        if not path.exists():
            self.update_status(f"File not found:\n{path}", error=True)
            return
        if not path.is_file():
            self.update_status("Dropped item is not a file.", error=True)
            return
        if path.suffix.lower() != ".py":
            self.update_status("Only Python (.py) files are supported.", error=True)
            return

        try:
            self.create_desktop_launcher(path)
            self.update_status(f".desktop launcher created:\n{path.name}")
        except Exception as e:
            self.update_status(f"Error:\n{e}", error=True)

    def create_desktop_launcher(self, script_path):
        desktop_dir = pathlib.Path.home() / "Desktop"
        desktop_dir.mkdir(exist_ok=True)

        launcher_name = script_path.stem + ".desktop"
        launcher_path = desktop_dir / launcher_name

        # Whether to open in terminal
        terminal_flag = "true" if self.terminal_checkbox.get_active() else "false"

        safe_path = f'"{script_path}"'

        content = f"""[Desktop Entry]
Type=Application
Name={script_path.stem}
Exec=python3 {safe_path}
Icon=utilities-terminal
Terminal={terminal_flag}
Categories=Utility;
"""

        with open(launcher_path, "w") as f:
            f.write(content)

        os.chmod(launcher_path, 0o755)

    def update_status(self, message, error=False):
        self.status.set_text(message)
        color = "#ff8080" if error else "#a0ffa0"
        self.status.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(*self.hex_to_rgba(color)))

    @staticmethod
    def hex_to_rgba(hex_color):
        hex_color = hex_color.lstrip("#")
        lv = len(hex_color)
        return tuple(int(hex_color[i:i + lv // 3], 16)/255 for i in range(0, lv, lv // 3)) + (1.0,)

if __name__ == "__main__":
    win = DragDropLauncher()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

