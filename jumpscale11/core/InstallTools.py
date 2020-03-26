from __future__ import unicode_literals
import getpass
import pickle
import re
import copy


import socket
import grp
import os
import random
import shutil
import stat
import subprocess
import sys
import textwrap
import time
import re
import inspect

from fcntl import F_GETFL, F_SETFL, fcntl
from os import O_NONBLOCK
from pathlib import Path
from subprocess import Popen, check_output
import inspect

# try:
#     import colored_traceback
#     colored_traceback.add_hook(always=True)
# except ImportError:
#     pass
#


class BaseInstallerror(Exception):
    pass


class InputError(Exception):
    pass


from string import Formatter


j.core.myenv.registry = Registry()
