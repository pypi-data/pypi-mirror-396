#!/usr/bin/env python

from sites import secured_sites
import subprocess
from icecream import ic


for site in secured_sites:
    ic(site["site"])
    proc=subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd=site["path"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
proc.communicate()
