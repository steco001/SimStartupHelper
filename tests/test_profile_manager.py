import pytest
from pathlib import Path
from profile_manager import ProfileManager


@pytest.fixture
def pm(tmp_path):
    return ProfileManager(config_path=tmp_path / "profiles.json")


def test_creates_default_profiles_on_first_run(pm):
    profiles = pm.get_profiles()
    assert len(profiles) == 3
    names = [p["name"] for p in profiles]
    assert "Le Mans Ultimate" in names
    assert "iRacing" in names
    assert "Flight Simulator 24" in names


def test_profiles_have_ids(pm):
    for p in pm.get_profiles():
        assert p["id"]


def test_add_profile(pm):
    pm.add_profile("Test Profile")
    names = [p["name"] for p in pm.get_profiles()]
    assert "Test Profile" in names


def test_add_profile_returns_profile(pm):
    p = pm.add_profile("New")
    assert p["name"] == "New"
    assert p["id"]
    assert p["programs"] == []


def test_clone_profile_copies_programs(pm):
    source_id = pm.get_profiles()[0]["id"]
    pm.add_program(source_id, "SimHub", "C:\\sim.exe", "", 0)
    cloned = pm.clone_profile(source_id, "Clone")
    assert cloned["name"] == "Clone"
    assert cloned["id"] != source_id
    assert len(cloned["programs"]) == 1
    assert cloned["programs"][0]["name"] == "SimHub"


def test_delete_profile(pm):
    pm.add_profile("To Delete")
    pid = next(p["id"] for p in pm.get_profiles() if p["name"] == "To Delete")
    pm.delete_profile(pid)
    assert not any(p["name"] == "To Delete" for p in pm.get_profiles())


def test_delete_active_profile_clears_active_id(pm):
    pid = pm.get_profiles()[0]["id"]
    pm.set_active_profile(pid)
    pm.delete_profile(pid)
    assert pm.get_active_profile_id() is None


def test_add_program(pm):
    pid = pm.get_profiles()[0]["id"]
    pm.add_program(pid, "SimHub", "C:\\sim.exe", "-flag", 3)
    progs = pm.get_profile(pid)["programs"]
    assert len(progs) == 1
    assert progs[0] == {"name": "SimHub", "path": "C:\\sim.exe", "args": "-flag", "delay": 3}


def test_update_program(pm):
    pid = pm.get_profiles()[0]["id"]
    pm.add_program(pid, "Old", "C:\\old.exe", "", 0)
    pm.update_program(pid, 0, "New", "C:\\new.exe", "-x", 5)
    progs = pm.get_profile(pid)["programs"]
    assert progs[0]["name"] == "New"
    assert progs[0]["delay"] == 5


def test_remove_program(pm):
    pid = pm.get_profiles()[0]["id"]
    pm.add_program(pid, "SimHub", "C:\\sim.exe", "", 0)
    pm.remove_program(pid, 0)
    assert pm.get_profile(pid)["programs"] == []


def test_persists_to_disk(tmp_path):
    config_file = tmp_path / "profiles.json"
    pm1 = ProfileManager(config_path=config_file)
    pm1.add_profile("Persisted")
    pm2 = ProfileManager(config_path=config_file)
    assert any(p["name"] == "Persisted" for p in pm2.get_profiles())


def test_recovers_from_corrupt_config(tmp_path):
    config_file = tmp_path / "profiles.json"
    config_file.write_text("not valid json")
    pm = ProfileManager(config_path=config_file)
    assert len(pm.get_profiles()) == 3
