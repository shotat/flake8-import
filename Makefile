

dist: flake8_import.py
	python setup.py install

run: dist
	flake8 tests

fmt:
	black flake8_import.py
