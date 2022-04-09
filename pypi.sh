rm -rf build/ dist/ uxf.egg-info/
py setup.py sdist bdist_wheel
twine upload dist/* && rm -rf build/ dist/ uxf.egg-info/
