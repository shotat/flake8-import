

dist: flake8_import.py
	python setup.py install

run: dist
	flake8 ../dgm-backend/src/entities --ignore=E501,W503

fmt:
	black flake8_import.py
