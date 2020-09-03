python -m pip install --upgrade pip
python -m pip install --user --upgrade setuptools wheel
python -m pip install --user --upgrade twine

rm -rf dist/
rm -rf build/
rm -rf simpleftpserver.egg-info/
rm -f MANIFEST
python setup.py sdist bdist_wheel
python -m twine upload --verbose --repository testpypi dist/*
