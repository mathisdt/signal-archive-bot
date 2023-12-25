#!/bin/sh
DIR=$(readlink -f $(dirname $0))
# activate venv
. $DIR/venv/bin/activate
# run in venv
python3 $DIR/main.py
