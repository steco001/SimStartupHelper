import copy
import json
import uuid
from pathlib import Path

APPDATA = Path.home() / "AppData" / "Roaming" / "SimStartUpHelper"
PROFILES_FILE = APPDATA / "profiles.json"

_DEFAULT_NAMES = ["Le Mans Ultimate", "iRacing", "Flight Simulator 24"]


class ProfileManager:
    def __init__(self, config_path: Path = PROFILES_FILE):
        self.config_path = config_path
        self.data = self._load()

    def _load(self) -> dict:
        if not self.config_path.exists():
            return self._create_defaults()
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return self._create_defaults()

    def _create_defaults(self) -> dict:
        data = {
            "active_profile_id": None,
            "profiles": [
                {"id": str(uuid.uuid4()), "name": name, "programs": []}
                for name in _DEFAULT_NAMES
            ],
        }
        self._write(data)
        return data

    def _write(self, data: dict):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save(self):
        self._write(self.data)

    # --- Profile CRUD ---

    def get_profiles(self) -> list:
        return list(self.data["profiles"])

    def get_profile(self, profile_id: str) -> dict | None:
        return next((p for p in self.data["profiles"] if p["id"] == profile_id), None)

    def _name_exists(self, name: str) -> bool:
        return any(p["name"] == name for p in self.data["profiles"])

    def add_profile(self, name: str) -> dict:
        if self._name_exists(name):
            raise ValueError(f"Profile '{name}' already exists")
        profile = {"id": str(uuid.uuid4()), "name": name, "programs": []}
        self.data["profiles"].append(profile)
        self.save()
        return profile

    def clone_profile(self, profile_id: str, new_name: str) -> dict:
        source = self.get_profile(profile_id)
        if source is None:
            raise ValueError(f"Profile {profile_id} not found")
        if self._name_exists(new_name):
            raise ValueError(f"Profile '{new_name}' already exists")
        new_profile = copy.deepcopy(source)
        new_profile["id"] = str(uuid.uuid4())
        new_profile["name"] = new_name
        self.data["profiles"].append(new_profile)
        self.save()
        return new_profile

    def rename_profile(self, profile_id: str, new_name: str):
        if self._name_exists(new_name):
            raise ValueError(f"Profile '{new_name}' already exists")
        profile = self.get_profile(profile_id)
        if profile is None:
            raise ValueError(f"Profile {profile_id} not found")
        profile["name"] = new_name
        self.save()

    def delete_profile(self, profile_id: str):
        self.data["profiles"] = [
            p for p in self.data["profiles"] if p["id"] != profile_id
        ]
        if self.data.get("active_profile_id") == profile_id:
            self.data["active_profile_id"] = None
        self.save()

    def set_active_profile(self, profile_id: str | None):
        self.data["active_profile_id"] = profile_id
        self.save()

    def get_active_profile_id(self) -> str | None:
        return self.data.get("active_profile_id")

    # --- Program CRUD ---

    def add_program(self, profile_id: str, name: str, path: str, args: str, delay: int) -> dict:
        profile = self.get_profile(profile_id)
        if profile is None:
            raise ValueError(f"Profile {profile_id} not found")
        program = {"name": name, "path": path, "args": args, "delay": delay}
        profile["programs"].append(program)
        self.save()
        return program

    def update_program(self, profile_id: str, index: int, name: str, path: str, args: str, delay: int):
        profile = self.get_profile(profile_id)
        if profile is None:
            raise ValueError(f"Profile {profile_id} not found")
        if index < 0 or index >= len(profile["programs"]):
            raise IndexError(f"Program index {index} out of range for profile {profile_id}")
        profile["programs"][index] = {"name": name, "path": path, "args": args, "delay": delay}
        self.save()

    def remove_program(self, profile_id: str, index: int):
        profile = self.get_profile(profile_id)
        if profile is None:
            raise ValueError(f"Profile {profile_id} not found")
        if index < 0 or index >= len(profile["programs"]):
            raise IndexError(f"Program index {index} out of range for profile {profile_id}")
        del profile["programs"][index]
        self.save()
