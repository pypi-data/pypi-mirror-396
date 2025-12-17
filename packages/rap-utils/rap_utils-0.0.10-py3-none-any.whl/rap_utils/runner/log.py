import os
from pathlib import Path

LOGFILE = Path(os.environ.get('RUNNER_LOGFILE')
               or Path(os.getcwd()).parent / 'runner.log')


def setup_log():
    LOGFILE.parent.mkdir(exist_ok=True, parents=True)
    if not LOGFILE.exists():
        write_log(
            'id',
            'status',
            'start_time',
            'run_time'
        )


def write_log(*fields):
    with open(LOGFILE, 'a', encoding='utf-8') as log:
        log.write(','.join((str(f) for f in fields)) + '\n')
