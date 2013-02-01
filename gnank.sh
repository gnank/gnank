#!/bin/sh
set -e
GNANK_DIR=`echo $0 | sed 's/[^\/]*$/src/g'`
export GNANK_DIR
exec $GNANK_DIR/gnank.py
