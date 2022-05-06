#!/bin/bash
tokei -f -tPython -esetup.py -eepd2uxf.py -eregression.py
unrecognized.py -q
python3 -m flake8 --ignore=W504,W503,E261,E303 .
python3 -m vulture . | grep -v 60%.confidence
git st
