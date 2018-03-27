# The following are targets that do not exist in the filesystem as real files and should be always executed by make
.PHONY: default deps base build dev shell start stop test_unit test_integration test

# Name of this project
PROJECT_NAME := twoboards

# Name of this service/application
SERVICE_NAME ?= twoboards

# Docker image name for this project
IMAGE_NAME := $(PROJECT_NAME)

# Shell to use for running scripts
SHELL := $(shell which bash)

# Get docker path or an empty string
DOCKER := $(shell command -v docker)

# Get docker-compose path or an empty string
DOCKER_COMPOSE := $(shell command -v docker-compose)

# Docker-compose project
export COMPOSE_PROJECT_NAME = $(PROJECT_NAME)

CREATE_USER_COMMAND =

ifeq ($(PLATFORM), Linux)
    # Get the main unix group for the user running make (to be used by docker-compose later)
    GID := $(shell id -g)

    # Get the unix user id for the user running make (to be used by docker-compose later)
    UID := $(shell id -u)

    # Create user command
    CREATE_USER_COMMAND = --build-arg gid=$(GID) --build-arg uid=$(UID)
endif


# The default action of this Makefile is to build the development docker image
default: build

# Test if the dependencies we need to run this Makefile are installed
deps:
ifndef DOCKER
	@echo "Docker is not available. Please install docker"
	@exit 1
endif
ifndef DOCKER_COMPOSE
	@echo "docker-compose is not available. Please install docker-compose"
	@exit 1
endif


# Build the base docker image which is shared between the development and production images
base: deps
	docker build $(CREATE_USER_COMMAND) -t $(IMAGE_NAME)_base:latest .

# Build the development docker image
build: base
	cd environment/dev && docker-compose build

# Run the development environment in non-daemonized mode (foreground)
dev: build
	cd environment/dev && \
	( docker-compose up; \
		docker-compose stop; \
		docker-compose rm -f; )

# Run a shell into the development docker image
shell: build
	cd environment/dev && docker-compose run --service-ports --rm $(SERVICE_NAME) /bin/bash

# Run the development environment in the background
start: build
	cd environment/dev && \
		docker-compose up -d

# Stop the development environment (background and/or foreground)
stop:
	cd environment/dev && ( \
		docker-compose stop; \
		docker-compose rm -f; \
		)


# Run unit tests
test_unit: build
	cd environment/dev && \
		docker-compose run --rm $(SERVICE_NAME) bash -c "mamba -f documentation test/unit"

# Run integration tests
test_integration: build
	cd environment/dev \
		docker-compose run --rm $(SERVICE_NAME) bash -c "mamba -f documentation test/integration"; \
		docker-compose stop; \
		docker-compose rm -f;

# Run both unit and integration tests
test: test_unit test_integration
