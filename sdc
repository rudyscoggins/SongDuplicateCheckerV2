#!/bin/sh
DIR="$(dirname "$0")"
PYTHONPATH="$DIR/src${PYTHONPATH:+:$PYTHONPATH}" exec python -m sdc "$@"
