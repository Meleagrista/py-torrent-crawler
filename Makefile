IMAGE_NAME=py-torrent-downloader
IMAGE_TAG=dev
CONTAINER_NAME=py-torrent-downloader-container
BIND_PATH ?= $(shell pwd)
DOWNLOAD_DIR ?= $(shell pwd)/devops/volumes/download
CACHE_DIR ?= $(shell pwd)/devops/volumes/cache

build:
	docker build -f devops/container/Dockerfile -t $(IMAGE_NAME):$(IMAGE_TAG) .

run:
	docker run -it --rm \
		--name $(CONTAINER_NAME) \
		--env-file config/dev.env \
		--network host \
		-v $(BIND_PATH):/app \
		-v $(DOWNLOAD_DIR):/root/downloads \
		-v $(CACHE_DIR):/root/.cache/storage \
		$(IMAGE_NAME):$(IMAGE_TAG)