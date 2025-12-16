
clean:
	find . | grep -E "(__pycache__|\.pyc|\.pyo|\.egg-info)" | xargs rm -rf
	rm -rf build/ dist/

test:
	uv run pytest -vv

lint:
	uv run black midi_utils/*.py tests/*.py

install:
	uv sync

build: clean
	uv build

# To publish to PyPI, you must use an API token (username/password is no longer supported)
# 1. Create a token at https://pypi.org/manage/account/token/
# 2. Add to your ~/.zshrc:
#    export TWINE_USERNAME=__token__
#    export TWINE_PASSWORD=pypi-YourActualTokenHere
# 3. Run: source ~/.zshrc
# 4. Then: make publish
publish: build
	uv run twine upload dist/*

.PHONY: clean test lint install build publish
