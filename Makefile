
build: sdist egg

sdist:
	python setup.py sdist

egg:
	python setup.py egg_info

.PHONY: build sdist egg

