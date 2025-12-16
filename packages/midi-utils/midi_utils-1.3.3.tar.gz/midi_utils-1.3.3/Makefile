
clean:
	find . | grep -E "(__pycache__|\.pyc|\.pyo|\.egg-info)" | xargs rm -rf
	rm -rf build/ dist/

test:
	uv run pytest -vv

lint:
	uv run ruff check midi_utils/ tests/
	uv run ruff format --check midi_utils/ tests/

install:
	uv sync

build: clean
	uv build

# To avoid entering token each time, add to ~/.zshrc:
# export TWINE_USERNAME=__token__
# export TWINE_PASSWORD=pypi-YourActualTokenHere
publish: build
	uv run twine upload dist/*

.PHONY: clean test lint install build publish
