install:
	python -m unittest discover -s test -t src
	pip install .

install-skip-test:
	pip install .

test:
	python -m unittest discover -s test -t src	

uninstall:
	pip uninstall openmath-for-python