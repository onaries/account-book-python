
.PHONY: build
build:
	docker buildx build --platform linux/arm64 -t ksw8954/account-book-python .

.PHONY: push
push:
	docker push ksw8954/account-book-python

.PHONY: up
up:
	docker-compose up -d

.PHONY: down
down:
	docker-compose down

.PHONY: ps
ps:
	docker-compose ps

shell:
	docker exec -it account-server /bin/bash
