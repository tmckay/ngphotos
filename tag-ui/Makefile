.PHONY: build test

build:
	    docker build --tag ngphotos-backend .

test: | build
	    docker run ngphotos-backend /bin/bash -c "pytest -vv"
