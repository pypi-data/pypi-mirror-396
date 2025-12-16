
clean:
	find . | grep -E "(__pycache__|\.pyc|\.pyo|\.egg-info)" | xargs rm -rf
	rm -rf build/ dist/

test:
	.venv/bin/pytest -vv

lint:
	.venv/bin/black midi_utils/*.py tests/*.py *.py

build: clean
	.venv/bin/pip install -r requirements-dev.txt
	.venv/bin/pip install -e .

pypi: clean
	python setup.py sdist
	twine upload dist/*
	
