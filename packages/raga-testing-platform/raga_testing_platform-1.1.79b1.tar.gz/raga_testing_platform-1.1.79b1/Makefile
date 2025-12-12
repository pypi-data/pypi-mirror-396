uploadtest:
	rm -rf dist
	python3 -m build
	python3 -m twine upload --repository testpypi dist/* -u $(TEST_PYPI_USERNAME) -p $(TEST_PYPI_TOKEN)


release:
	rm -rf dist
	python3 -m build
	python3 -m twine upload --repository pypi dist/* -u $(PYPI_USERNAME) -p $(PYPI_TOKEN)
