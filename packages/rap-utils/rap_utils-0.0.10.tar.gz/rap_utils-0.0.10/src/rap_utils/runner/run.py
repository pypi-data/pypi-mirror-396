import subprocess
from datetime import datetime

from .log import write_log


def run(cmd, id=None):
    start_time = datetime.now()
    process = subprocess.run(cmd)
    run_time = datetime.now() - start_time
    write_log(
        id or " ".join(cmd),
        process.returncode,
        start_time,
        run_time,
    )

