from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
python = ROOT / ".venv" / "Scripts" / "python.exe"
log = ROOT / "server.log"

with log.open("ab") as output:
    subprocess.Popen(
        [
            str(python),
            "manage.py",
            "runserver",
            "127.0.0.1:8000",
            "--noreload",
        ],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=output,
        stderr=output,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
        close_fds=True,
    )

sys.exit(0)
