#!/bin/bash
tokei -f -slines -tPython,Rust -esetup.py -etarget
cd rs
grep --color=auto --exclude-dir=target --include=*.rs -r format......,
cd ..
unrecognized.py -q
python3 -m flake8 --ignore=W504,W503,E261,E303 .
python3 -m vulture . | grep -v 60%.confidence
git st
