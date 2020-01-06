include .env
export

build:
	make build-sumosv && make build-worker && make build-canarybot
push:
	make push-sumosv && make push-worker && make push-canarybot

build-sumosv: ## build image
	docker build -f sumosv/Dockerfile -t sudologic/sumosv .
push-sumosv: ## push to ECR
	docker tag sudologic/sumosv:latest 883448249014.dkr.ecr.ap-southeast-2.amazonaws.com/sudologic/sumosv:latest
	docker push 883448249014.dkr.ecr.ap-southeast-2.amazonaws.com/sudologic/sumosv:latest

build-worker: ## build image
	docker build -f worker/Dockerfile -t sudologic/worker .
push-worker: ## push to ECR
	docker tag sudologic/worker:latest 883448249014.dkr.ecr.ap-southeast-2.amazonaws.com/sudologic/worker:latest
	docker push 883448249014.dkr.ecr.ap-southeast-2.amazonaws.com/sudologic/worker:latest

build-canarybot: ## build image
	docker build -f canarybot/Dockerfile -t sudologic/canarybot .
push-canarybot: ## push to ECR
	docker tag sudologic/canarybot:latest 883448249014.dkr.ecr.ap-southeast-2.amazonaws.com/sudologic/canarybot:latest
	docker push 883448249014.dkr.ecr.ap-southeast-2.amazonaws.com/sudologic/canarybot:latest

build-nginx: ## build image
	docker build -f nginx/Dockerfile -t sudologic/nginx .
push-nginx: ## push to ECR
	docker tag sudologic/nginx:latest 883448249014.dkr.ecr.ap-southeast-2.amazonaws.com/sudologic/nginx:latest
	docker push 883448249014.dkr.ecr.ap-southeast-2.amazonaws.com/sudologic/nginx:latest

package:
	cd dist && rm -f sudologic.20* && zip -r sudologic.$$(date +%FT%H%M%S).zip . -x *vendor* *.env* *.DS_Store* *.idea* *.git* *.vscode*