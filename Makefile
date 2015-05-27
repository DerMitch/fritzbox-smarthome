
.PHONY:: dist up

dist:
	python setup.py sdist bdist_wheel

up:
	twine upload -r pypitest dist/*
