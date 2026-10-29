"""Der Projektordner reicht den Django-Befehl an rabatti weiter."""

import subprocess
import sys
from pathlib import Path


def test_root_manage_py_runs_django_check() -> None:
    root = Path(__file__).resolve().parents[2]
    completed = subprocess.run(
        [sys.executable, str(root / "manage.py"), "check"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
