import time
import pytest
from unittest.mock import MagicMock, patch, call
from process_manager import ProcessManager


@pytest.fixture
def pm():
    mgr = ProcessManager()
    yield mgr
    mgr.stop_all()


def test_start_profile_launches_each_program(pm):
    programs = [
        {"name": "p1", "path": "a.exe", "args": "", "delay": 0},
        {"name": "p2", "path": "b.exe", "args": "", "delay": 0},
    ]
    with patch("subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_popen.return_value = mock_proc
        pm.start_profile(programs)
        time.sleep(0.1)
    assert mock_popen.call_count == 2


def test_start_profile_passes_args(pm):
    programs = [{"name": "p1", "path": "a.exe", "args": "-foo bar", "delay": 0}]
    with patch("subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_popen.return_value = mock_proc
        pm.start_profile(programs)
        time.sleep(0.1)
    mock_popen.assert_called_once_with(["a.exe", "-foo", "bar"])


def test_start_profile_respects_delay(pm):
    programs = [
        {"name": "p1", "path": "a.exe", "args": "", "delay": 0},
        {"name": "p2", "path": "b.exe", "args": "", "delay": 0.3},
    ]
    with patch("subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_popen.return_value = mock_proc
        pm.start_profile(programs)
        time.sleep(0.1)
        assert mock_popen.call_count == 1
        time.sleep(0.35)
        assert mock_popen.call_count == 2


def test_stop_all_terminates_processes(pm):
    programs = [{"name": "p1", "path": "a.exe", "args": "", "delay": 0}]
    with patch("subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_proc.wait.return_value = 0
        mock_popen.return_value = mock_proc
        pm.start_profile(programs)
        time.sleep(0.1)
        pm.stop_all()
    mock_proc.terminate.assert_called_once()


def test_status_callback_called_true_on_successful_launch(pm):
    callback = MagicMock()
    pm._status_callback = callback
    programs = [{"name": "p1", "path": "a.exe", "args": "", "delay": 0}]
    with patch("subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_popen.return_value = mock_proc
        pm.start_profile(programs)
        time.sleep(0.1)
    callback.assert_any_call("0_p1", True)


def test_status_callback_called_false_on_failed_launch(pm):
    callback = MagicMock()
    pm._status_callback = callback
    programs = [{"name": "p1", "path": "missing.exe", "args": "", "delay": 0}]
    with patch("subprocess.Popen", side_effect=OSError("not found")):
        pm.start_profile(programs)
        time.sleep(0.1)
    callback.assert_any_call("0_p1", False)


def test_start_stopped_only_restarts_dead_processes(pm):
    programs = [
        {"name": "p1", "path": "a.exe", "args": "", "delay": 0},
        {"name": "p2", "path": "b.exe", "args": "", "delay": 0},
    ]
    with patch("subprocess.Popen") as mock_popen:
        alive = MagicMock()
        alive.poll.return_value = None  # still running
        dead = MagicMock()
        dead.poll.return_value = 1  # crashed
        mock_popen.side_effect = [alive, dead, MagicMock()]
        pm.start_profile(programs)
        time.sleep(0.1)
        mock_popen.reset_mock()
        pm.start_stopped(programs)
        time.sleep(0.1)
    assert mock_popen.call_count == 1  # only p2 restarted
