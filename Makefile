# Conda-related paths
conda_env_dir := ./env
CONDA_EXE ?= conda
conda_run := $(CONDA_EXE) run --live-stream --prefix $(conda_env_dir)

setup:
	$(CONDA_EXE) env $(shell [ -d $(conda_env_dir) ] && echo update || echo create) -p $(conda_env_dir) --file environment.yaml

dev:
	$(conda_run) fastapi dev app.py

build:
	docker build .
	# -t $(image):$(docker_tag)

.PHONY: $(MAKECMDGOALS)
