"""Logging Runner

Usage:

runner.py <COMMAND TO EXECUTE>

This script runs the command specified, logging the return code, start time and
execution time.

By default the output is written to a file called `runner.log` in the current working
directory. This can be overriden by setting the RUNNER_LOGFILE environment variable
which must include the filename.

The first field of the log will contain either the command executed or an identifier
string, which can be provided using the `-i` or `--id` flags. If running in DVC, the
current stage name is printed out instead of the command executed.
"""

import os
import sys
from getopt import getopt
from .run import run

optlist, args = getopt(sys.argv[1:], "i:", ["id="])

# NB requires DVC > 3.49.0 for DVC_STAGE to be set
id = os.environ.get('DVC_STAGE')
for o, a in optlist:
    if o in ('-i', '--id'):
        id = a
    else:
        assert False, "unhandled option"

run(args, id=id)
