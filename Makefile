
.PHONY:: dist up

dist:
	# If bdist_wheel does not work:
	# pip install wheel twine
	python setup.py sdist bdist_wheel

testup:
	twine upload -r pypitest dist/*

up:
	twine upload dist/*
