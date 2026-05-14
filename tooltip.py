import tkinter as tk


class Tooltip:
    def __init__(self, widget, text: str):
        self._widget = widget
        self._text = text
        self._win = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _event=None):
        if self._win:
            return
        x = self._widget.winfo_rootx() + self._widget.winfo_width() // 2
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4
        self._win = win = tk.Toplevel(self._widget)
        win.wm_overrideredirect(True)
        win.wm_geometry(f"+{x}+{y}")
        tk.Label(
            win,
            text=self._text,
            background="#242424",
            foreground="#f5a623",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9),
            padx=5,
            pady=3,
        ).pack()

    def _hide(self, _event=None):
        if self._win:
            self._win.destroy()
            self._win = None
