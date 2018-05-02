#!/usr/bin/env python
import os, sys

sys.dont_write_bytecode=True

from rsgee.conf import ENVIRONMENT_VARIABLE

if __name__ == "__main__":
    os.environ.setdefault(ENVIRONMENT_VARIABLE, "mapbiomas.settings")
    from rsgee.manage import Manage
    manage = Manage()
    manage.execute_commands(sys.argv[1] if len(sys.argv) > 1 else None)
