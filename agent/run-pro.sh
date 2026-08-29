#!/bin/bash
export PYTHONPATH="/home/ruser/containerguard-pro:$PYTHONPATH"
cd /home/ruser/containerguard-new
source venv/bin/activate
exec python agent/runner.py
