.PHONY: build run stop test push clean venv

IMAGE_NAME = pysmtp4dev
DOCKER_REPO = kaelisra/pysmtp4dev
TAG = $(shell git describe --tags --abbrev=0 2>/dev/null || echo latest)
PYTHON := .venv/bin/python

build:
	docker build -t $(IMAGE_NAME):$(TAG) -f docker/Dockerfile .

run:
	docker compose -f docker/docker-compose.yaml up -d

stop:
	docker compose -f docker/docker-compose.yaml down

venv:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@if [ -f requirements-dev.txt ]; then .venv/bin/pip install -r requirements-dev.txt; fi

test:
	$(PYTHON) -m pytest

push:
	docker tag $(IMAGE_NAME):$(TAG) $(DOCKER_REPO):$(TAG)
	docker push $(DOCKER_REPO):$(TAG)

clean: stop
	docker rmi $(IMAGE_NAME):$(TAG)
