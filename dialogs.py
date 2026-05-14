import customtkinter as ctk
from tkinter import filedialog
from typing import Callable


class ProgramDialog(ctk.CTkToplevel):
    """Modal dialog for adding or editing a program entry."""

    def __init__(
        self,
        parent,
        title: str,
        program: dict = None,
        on_save: Callable[[dict], None] = None,
    ):
        super().__init__(parent)
        self.title(title)
        self.geometry("420x300")
        self.resizable(False, False)
        self.grab_set()
        self._on_save = on_save
        self._build(program or {})

    def _build(self, program: dict):
        pad = {"padx": 16, "pady": 4}

        ctk.CTkLabel(self, text="Name", anchor="w").pack(fill="x", **pad)
        self._name = ctk.CTkEntry(self, width=385)
        self._name.insert(0, program.get("name", ""))
        self._name.pack(**pad)

        ctk.CTkLabel(self, text="Pfad zur .exe", anchor="w").pack(fill="x", **pad)
        path_row = ctk.CTkFrame(self, fg_color="transparent")
        path_row.pack(fill="x", **pad)
        self._path = ctk.CTkEntry(path_row, width=325)
        self._path.insert(0, program.get("path", ""))
        self._path.pack(side="left")
        ctk.CTkButton(path_row, text="...", width=50, command=self._browse).pack(
            side="left", padx=(6, 0)
        )

        ctk.CTkLabel(self, text="Argumente (optional)", anchor="w").pack(fill="x", **pad)
        self._args = ctk.CTkEntry(self, width=385)
        self._args.insert(0, program.get("args", ""))
        self._args.pack(**pad)

        ctk.CTkLabel(self, text="Startverzögerung in Sekunden", anchor="w").pack(
            fill="x", **pad
        )
        self._delay = ctk.CTkEntry(self, width=100)
        self._delay.insert(0, str(program.get("delay", 0)))
        self._delay.pack(anchor="w", **pad)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(12, 8))
        ctk.CTkButton(btn_row, text="Abbrechen", fg_color="gray", command=self.destroy).pack(
            side="right", padx=(6, 0)
        )
        ctk.CTkButton(btn_row, text="Speichern", command=self._save).pack(side="right")

    def _browse(self):
        path = filedialog.askopenfilename(
            filetypes=[("Programme", "*.exe"), ("Alle Dateien", "*.*")]
        )
        if path:
            self._path.delete(0, "end")
            self._path.insert(0, path)

    def _save(self):
        name = self._name.get().strip()
        path = self._path.get().strip()
        if not name or not path:
            return
        try:
            delay = max(0, int(self._delay.get().strip()))
        except ValueError:
            delay = 0
        if self._on_save:
            self._on_save(
                {"name": name, "path": path, "args": self._args.get().strip(), "delay": delay}
            )
        self.destroy()


class ProfileNameDialog(ctk.CTkToplevel):
    """Modal dialog for naming a new or cloned profile."""

    def __init__(
        self,
        parent,
        title: str,
        initial_name: str = "",
        on_save: Callable[[str], None] = None,
    ):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x150")
        self.resizable(False, False)
        self.grab_set()
        self._on_save = on_save
        self._build(initial_name)

    def _build(self, initial_name: str):
        pad = {"padx": 16, "pady": 6}
        ctk.CTkLabel(self, text="Profilname", anchor="w").pack(fill="x", **pad)
        self._name = ctk.CTkEntry(self, width=265)
        self._name.insert(0, initial_name)
        self._name.pack(**pad)
        self._name.focus()

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(8, 8))
        ctk.CTkButton(btn_row, text="Abbrechen", fg_color="gray", command=self.destroy).pack(
            side="right", padx=(6, 0)
        )
        ctk.CTkButton(btn_row, text="OK", command=self._save).pack(side="right")

    def _save(self):
        name = self._name.get().strip()
        if not name:
            return
        if self._on_save:
            self._on_save(name)
        self.destroy()
