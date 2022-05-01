rm -rf build/ dist/ uxf.egg-info/
python3 setup.py sdist bdist_wheel
twine upload dist/* && rm -rf build/ dist/ uxf.egg-info/
