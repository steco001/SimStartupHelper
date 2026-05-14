import threading
from typing import Callable

import pystray
from PIL import Image, ImageDraw


def _make_icon_image(size: int = 32) -> Image.Image:
    img = Image.new("RGBA", (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=size // 5, fill=(245, 166, 35))
    m = size // 5
    draw.text((m + 1, m - 1), "S", fill=(26, 26, 26))
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
            self._icon = None

    def _handle_show(self, icon, item):
        self._on_show()

    def _handle_quit(self, icon, item):
        self.stop()
        self._on_quit()
