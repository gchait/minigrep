PYTHON = python3
APP_NAME = minigrep
IMAGE_NAME = pytest-py37
CONTAINER_NAME = test-minigrep
PYTEST_ARGS = --verbose --color=yes

.PHONY = help build run
.DEFAULT_GOAL = help

help:
	@echo '+------------------------HELP------------------------+'
	@echo '| To build the pytest image, type "make build".      |'
	@echo '| To run the tests in a container, type "make run".  |'
	@echo '+----------------------------------------------------+'

build:
	@sudo docker build -t ${IMAGE_NAME} .

run:
	@sudo docker run --rm -v $(shell pwd):/usr/src/${APP_NAME} -w /usr/src/${APP_NAME} \
		--name ${CONTAINER_NAME} ${IMAGE_NAME} ${PYTHON} -m pytest ${PYTEST_ARGS}

