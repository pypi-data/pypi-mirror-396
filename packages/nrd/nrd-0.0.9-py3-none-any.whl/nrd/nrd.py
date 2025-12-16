#!/usr/bin/env python

from .sites import secured_sites
import subprocess
from icecream import ic
import time


def main():
    """Main entry point for NRD."""
    for site in secured_sites:
        ic(site["site"])
        proc = subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd=site["path"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down NRD...")


if __name__ == '__main__':
    main()
