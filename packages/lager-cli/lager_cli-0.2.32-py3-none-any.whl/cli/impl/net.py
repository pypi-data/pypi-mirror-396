#!/usr/bin/env python3
"""
Net management implementation for direct execution in container.
This script runs directly in the gateway container and imports the net module.
"""
import sys
import os

# Add the gateway python path to sys.path so we can import lager modules
sys.path.insert(0, '/app/lager')

# Now import and run the net module's CLI
from lager.pcb.net import _cli

if __name__ == "__main__":
    _cli()