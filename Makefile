

dist: flake8_import.py
	python setup.py install

run: dist
	flake8 tests --ignore=E501,W503,F401

fmt:
	black flake8_import.py

mypy:
	mypy flake8_import.py
