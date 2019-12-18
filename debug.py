#!/usr/bin/env python

import os
import sys
import ptvsd
from configurations.management import execute_from_command_line

if __name__ == "__main__":

    if os.environ.get('RUN_MAIN') or os.environ.get('WERKZEUG_RUN_MAIN'):
        ptvsd.enable_attach(address=('0.0.0.0', 3000), redirect_output=True)

    execute_from_command_line(sys.argv)
