import customtkinter as ctk

from pathlib import Path

from PIL import Image

from dialogs import ProfileNameDialog, ProgramDialog
from process_manager import ProcessManager
from profile_manager import ProfileManager
from tooltip import Tooltip
from tray_icon import _make_icon_image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

_ACCENT       = "#f5a623"
_ACCENT_HOVER = "#c8861a"
_ACCENT_TEXT  = "#1a1a1a"
_BG_HEADER    = "#1e1e1e"
_BG_CARD      = "#242424"
_SEPARATOR    = "#2d2d2d"
_TEXT_MUTED   = "#999999"
_STATUS_BG    = "#141414"
_DANGER       = "#ef5350"
_DANGER_HOVER = "#3d1414"


class App(ctk.CTk):
    def __init__(self, profile_manager: ProfileManager, process_manager: ProcessManager):
        super().__init__()
        self._pm = profile_manager
        self._proc = process_manager
        self._proc._status_callback = self._on_status_update
        self._program_rows: list[dict] = []

        self.title("SimStartUpHelper")
        self.geometry("380x540")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(0, self._set_icon)

        self._build_ui()
        self._refresh_profiles()
        self._poll_status()

    def _poll_status(self):
        profile = self._get_selected_profile()
        if profile:
            for i, prog in enumerate(profile["programs"]):
                key = self._proc.get_key(i, prog["name"])
                running = self._proc.is_running(key)
                for row in self._program_rows:
                    if row["key"] == key:
                        row["status_lbl"].configure(
                            text="●" if running else "○",
                            text_color="#4caf50" if running else "gray",
                        )
            self._update_status()
        self.after(1000, self._poll_status)

    def _set_icon(self):
        ico_path = Path(__file__).parent / "assets" / "app.ico"
        ico_path.parent.mkdir(exist_ok=True)
        if not ico_path.exists():
            _make_icon_image(64).save(str(ico_path), format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
        self.iconbitmap(str(ico_path))

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        # Profile header
        header = ctk.CTkFrame(self, fg_color=_BG_HEADER, corner_radius=0, height=82)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="AKTIVES PROFIL", font=("", 10, "bold"), text_color=_TEXT_MUTED).pack(
            anchor="w", padx=12, pady=(8, 0)
        )
        ctrl_row = ctk.CTkFrame(header, fg_color="transparent")
        ctrl_row.pack(fill="x", padx=12, pady=(2, 0))

        self._profile_var = ctk.StringVar()
        self._profile_dropdown = ctk.CTkOptionMenu(
            ctrl_row, variable=self._profile_var, width=195,
            fg_color=_ACCENT, button_color=_ACCENT_HOVER, button_hover_color="#a07010",
            text_color=_ACCENT_TEXT,
            command=self._on_profile_selected,
        )
        self._profile_dropdown.pack(side="left")

        btn_add_profile = ctk.CTkButton(
            ctrl_row, text="+", width=28,
            fg_color=_ACCENT, hover_color=_ACCENT_HOVER, text_color=_ACCENT_TEXT,
            command=self._create_profile,
        )
        btn_add_profile.pack(side="left", padx=(6, 2))
        Tooltip(btn_add_profile, "Neues Profil erstellen")

        btn_rename = ctk.CTkButton(
            ctrl_row, text="✏", width=28,
            fg_color=_ACCENT, hover_color=_ACCENT_HOVER, text_color=_ACCENT_TEXT,
            command=self._rename_profile,
        )
        btn_rename.pack(side="left", padx=2)
        Tooltip(btn_rename, "Profil umbenennen")

        btn_clone = ctk.CTkButton(
            ctrl_row, text="Clone", width=48,
            fg_color=_ACCENT, hover_color=_ACCENT_HOVER, text_color=_ACCENT_TEXT,
            command=self._clone_profile,
        )
        btn_clone.pack(side="left", padx=2)
        Tooltip(btn_clone, "Aktives Profil klonen")

        btn_del_profile = ctk.CTkButton(
            ctrl_row,
            text="✕", width=28,
            fg_color="transparent",
            border_width=1,
            text_color=_ACCENT,
            hover_color=_ACCENT_HOVER,
            command=self._delete_profile,
        )
        btn_del_profile.pack(side="left", padx=2)
        Tooltip(btn_del_profile, "Profil löschen")

        self._active_label = ctk.CTkLabel(
            header, text="", font=("", 10), text_color="gray", anchor="w"
        )
        self._active_label.pack(anchor="w", padx=12)

        ctk.CTkFrame(self, height=1, fg_color=_SEPARATOR).pack(fill="x")

        # Programs section
        prog_header = ctk.CTkFrame(self, fg_color="transparent")
        prog_header.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkLabel(prog_header, text="PROGRAMME", font=("", 10, "bold"), text_color=_TEXT_MUTED).pack(
            side="left"
        )
        btn_add_prog = ctk.CTkButton(
            prog_header, text="+ Hinzufügen", width=100, height=26,
            fg_color=_ACCENT, hover_color=_ACCENT_HOVER, text_color=_ACCENT_TEXT,
            command=self._add_program,
        )
        btn_add_prog.pack(side="right")
        Tooltip(btn_add_prog, "Programm zum Profil hinzufügen")

        self._programs_frame = ctk.CTkScrollableFrame(self, height=290)
        self._programs_frame.pack(fill="x", padx=12)

        ctk.CTkFrame(self, height=1, fg_color=_SEPARATOR).pack(fill="x", pady=(8, 0))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=8)
        self._start_btn = ctk.CTkButton(
            btn_row,
            text="▶ Profil starten",
            fg_color=_ACCENT,
            hover_color=_ACCENT_HOVER,
            text_color=_ACCENT_TEXT,
            font=("", 13, "bold"),
            command=self._start_profile,
        )
        self._start_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))
        Tooltip(self._start_btn, "Alle Programme des aktiven Profils starten")

        btn_stop = ctk.CTkButton(
            btn_row,
            text="■ Stoppen",
            fg_color="transparent",
            border_width=1,
            text_color=_ACCENT,
            hover_color=_ACCENT_HOVER,
            command=self._stop_profile,
        )
        btn_stop.pack(side="left", expand=True, fill="x")
        Tooltip(btn_stop, "Alle laufenden Programme stoppen")

        self._status_bar = ctk.CTkLabel(
            self,
            text="Kein aktives Profil",
            font=("", 10),
            fg_color=_STATUS_BG,
            text_color=_ACCENT,
            corner_radius=0,
            height=24,
        )
        self._status_bar.pack(fill="x", side="bottom")

    # ------------------------------------------------------------------
    # Profile logic
    # ------------------------------------------------------------------

    def _refresh_profiles(self):
        profiles = self._pm.get_profiles()
        if not profiles:
            self._profile_dropdown.configure(values=["(keine Profile)"])
            self._profile_var.set("(keine Profile)")
            self._refresh_programs()
            return
        names = [p["name"] for p in profiles]
        self._profile_dropdown.configure(values=names)
        active_id = self._pm.get_active_profile_id()
        active = self._pm.get_profile(active_id) if active_id else None
        self._profile_var.set(active["name"] if active else names[0])
        self._refresh_programs()

    def _get_selected_profile(self) -> dict | None:
        name = self._profile_var.get()
        return next((p for p in self._pm.get_profiles() if p["name"] == name), None)

    def _on_profile_selected(self, _name: str):
        self._proc.stop_all()
        profile = self._get_selected_profile()
        if profile:
            self._pm.set_active_profile(profile["id"])
        self._refresh_programs()
        self._update_status()

    def _create_profile(self):
        ProfileNameDialog(self, "Neues Profil", on_save=self._save_new_profile)

    def _save_new_profile(self, name: str):
        try:
            self._pm.add_profile(name)
        except ValueError:
            return
        profiles = self._pm.get_profiles()
        names = [p["name"] for p in profiles]
        self._profile_dropdown.configure(values=names)
        self._profile_var.set(name)
        self._refresh_programs()

    def _rename_profile(self):
        profile = self._get_selected_profile()
        if not profile:
            return
        ProfileNameDialog(
            self,
            "Profil umbenennen",
            initial_name=profile["name"],
            on_save=lambda name: self._save_renamed_profile(profile["id"], name),
        )

    def _save_renamed_profile(self, profile_id: str, new_name: str):
        try:
            self._pm.rename_profile(profile_id, new_name)
        except ValueError:
            return
        profiles = self._pm.get_profiles()
        names = [p["name"] for p in profiles]
        self._profile_dropdown.configure(values=names)
        self._profile_var.set(new_name)
        self._refresh_programs()

    def _clone_profile(self):
        profile = self._get_selected_profile()
        if not profile:
            return
        ProfileNameDialog(
            self,
            "Profil klonen",
            initial_name=f"{profile['name']} (Kopie)",
            on_save=lambda name: self._save_cloned_profile(profile["id"], name),
        )

    def _save_cloned_profile(self, source_id: str, new_name: str):
        try:
            self._pm.clone_profile(source_id, new_name)
        except ValueError:
            return
        profiles = self._pm.get_profiles()
        names = [p["name"] for p in profiles]
        self._profile_dropdown.configure(values=names)
        self._profile_var.set(new_name)
        self._refresh_programs()

    def _delete_profile(self):
        profile = self._get_selected_profile()
        if not profile:
            return
        self._proc.stop_all()
        self._pm.delete_profile(profile["id"])
        self._refresh_profiles()

    # ------------------------------------------------------------------
    # Program logic
    # ------------------------------------------------------------------

    def _refresh_programs(self):
        for w in self._programs_frame.winfo_children():
            w.destroy()
        self._program_rows.clear()
        profile = self._get_selected_profile()
        if profile:
            for i, prog in enumerate(profile["programs"]):
                self._add_program_row(i, prog)
        self._update_status()

    def _add_program_row(self, index: int, prog: dict):
        row = ctk.CTkFrame(self._programs_frame, fg_color=_BG_CARD, corner_radius=6)
        row.pack(fill="x", pady=2)

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=4)
        ctk.CTkLabel(info, text=prog["name"], font=("", 12, "bold"), anchor="w").pack(anchor="w")
        args_str = prog["args"] if prog["args"] else "Keine Argumente"
        ctk.CTkLabel(
            info,
            text=f"Delay: {prog['delay']}s · {args_str}",
            font=("", 10),
            text_color="gray",
            anchor="w",
        ).pack(anchor="w")

        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.pack(side="right", padx=6, pady=4)

        key = self._proc.get_key(index, prog['name'])
        status_lbl = ctk.CTkLabel(actions, text="○", font=("", 14), text_color="gray", width=20)
        status_lbl.pack(side="left", padx=(0, 4))
        btn_edit = ctk.CTkButton(
            actions, text="✏", width=28, height=26,
            fg_color=_ACCENT, hover_color=_ACCENT_HOVER, text_color=_ACCENT_TEXT,
            command=lambda i=index: self._edit_program(i),
        )
        btn_edit.pack(side="left", padx=2)
        Tooltip(btn_edit, "Programm bearbeiten")

        btn_del_prog = ctk.CTkButton(
            actions,
            text="✕",
            width=28,
            height=26,
            fg_color="transparent",
            border_width=1,
            text_color=_DANGER,
            hover_color=_DANGER_HOVER,
            command=lambda i=index: self._remove_program(i),
        )
        btn_del_prog.pack(side="left", padx=2)
        Tooltip(btn_del_prog, "Programm entfernen")

        self._program_rows.append({"key": key, "status_lbl": status_lbl})

    def _add_program(self):
        profile = self._get_selected_profile()
        if not profile:
            return
        ProgramDialog(
            self,
            "Programm hinzufügen",
            on_save=lambda data: self._save_new_program(profile["id"], data),
        )

    def _save_new_program(self, profile_id: str, data: dict):
        self._pm.add_program(profile_id, data["name"], data["path"], data["args"], data["delay"])
        self._refresh_programs()

    def _edit_program(self, index: int):
        profile = self._get_selected_profile()
        if not profile or index >= len(profile["programs"]):
            return
        prog = profile["programs"][index]
        ProgramDialog(
            self,
            "Programm bearbeiten",
            program=prog,
            on_save=lambda data: self._save_edited_program(profile["id"], index, data),
        )

    def _save_edited_program(self, profile_id: str, index: int, data: dict):
        self._pm.update_program(profile_id, index, data["name"], data["path"], data["args"], data["delay"])
        self._refresh_programs()

    def _remove_program(self, index: int):
        profile = self._get_selected_profile()
        if not profile:
            return
        self._pm.remove_program(profile["id"], index)
        self._refresh_programs()

    def _start_profile(self):
        profile = self._get_selected_profile()
        if not profile:
            return
        running = {r["key"] for r in self._program_rows if r["status_lbl"].cget("text") == "●"}
        if not running:
            self._proc.start_profile(profile["programs"])
        else:
            self._proc.start_stopped(profile["programs"])

    def _stop_profile(self):
        self._proc.stop_all()

    # ------------------------------------------------------------------
    # Status updates (called from background thread via after())
    # ------------------------------------------------------------------

    def _on_status_update(self, key: str | None, is_running: bool):
        self.after(0, self._apply_status, key, is_running)

    def _apply_status(self, key: str | None, is_running: bool):
        if key is None:
            for row in self._program_rows:
                row["status_lbl"].configure(text="○", text_color="gray")
        else:
            for row in self._program_rows:
                if row["key"] == key:
                    row["status_lbl"].configure(
                        text="●" if is_running else "○",
                        text_color="#4caf50" if is_running else "#f44336",
                    )
        self._update_status()

    def _update_status(self):
        profile = self._get_selected_profile()
        if not profile:
            self._status_bar.configure(text="Kein aktives Profil")
            self._active_label.configure(text="")
            return
        total = len(profile["programs"])
        running = sum(1 for r in self._program_rows if r["status_lbl"].cget("text") == "●")
        if total == 0:
            self._active_label.configure(text="Keine Programme konfiguriert", text_color="gray")
            self._start_btn.configure(state="normal")
        elif running == total:
            self._active_label.configure(
                text=f"● Aktiv — {running} von {total} laufen", text_color="#4caf50"
            )
            self._start_btn.configure(state="disabled")
        else:
            self._active_label.configure(
                text=f"○ {running} von {total} laufen", text_color="orange"
            )
            self._start_btn.configure(state="normal")
        self._status_bar.configure(text=f"{profile['name']} · {running}/{total} laufen")

    # ------------------------------------------------------------------
    # Window / lifecycle
    # ------------------------------------------------------------------

    def _on_close(self):
        self.quit_app()

    def show(self):
        self.after(0, self._do_show)

    def _do_show(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def quit_app(self):
        self._proc.stop_all()
        self.after(0, self.destroy)  # must run on main thread
