IMAGE_NAME=py-torrent-downloader
IMAGE_TAG=dev
CONTAINER_NAME=py-torrent-downloader-container
BIND_PATH ?= $(shell pwd)
DOWNLOAD_PATH ?= $(shell pwd)/devops/bind

build:
	docker build -f devops/container/Dockerfile -t $(IMAGE_NAME):$(IMAGE_TAG) .

run: build
	docker run -it --rm \
		--name $(CONTAINER_NAME) \
		--env-file config/dev.env \
		--network host \
		-v $(BIND_PATH):/app \
		-v $(DOWNLOAD_PATH):/root/downloads \
		$(IMAGE_NAME):$(IMAGE_TAG)