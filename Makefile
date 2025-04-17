IMAGE_NAME=py-torrent-downloader
TAG=dev
CONTAINER_NAME=py-torrent-downloader-container

build:
	docker build -f devops/container/Dockerfile -t $(IMAGE_NAME):$(TAG) .

run:
	docker run --rm --name $(CONTAINER_NAME) $(IMAGE_NAME):$(TAG)