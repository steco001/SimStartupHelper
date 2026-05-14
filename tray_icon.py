import threading
from typing import Callable

import pystray
from PIL import Image, ImageDraw


def _make_icon_image() -> Image.Image:
    img = Image.new("RGB", (32, 32), color=(21, 101, 192))
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 22, 22], fill=(255, 255, 255))
    return img


class TrayIcon:
    def __init__(self, on_show: Callable, on_quit: Callable):
        self._on_show = on_show
        self._on_quit = on_quit
        self._icon: pystray.Icon | None = None

    def start(self):
        menu = pystray.Menu(
            pystray.MenuItem("Öffnen", self._handle_show, default=True),
            pystray.MenuItem("Beenden", self._handle_quit),
        )
        self._icon = pystray.Icon(
            "SimStartUpHelper", _make_icon_image(), "SimStartUpHelper", menu
        )
        threading.Thread(target=self._icon.run, daemon=True).start()

    def stop(self):
        if self._icon:
            self._icon.stop()

    def _handle_show(self, icon, item):
        self._on_show()

    def _handle_quit(self, icon, item):
        self._icon.stop()
        self._on_quit()
