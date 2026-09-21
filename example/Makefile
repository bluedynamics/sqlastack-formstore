SHELL := /bin/bash

.PHONY: help backend frontend-install frontend stop clean

help: ## Show targets
	@grep -hE '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*##/:/'

backend: ## Start PostgreSQL + migration + Plone backend (docker)
	docker compose up -d
	@echo "Backend: http://localhost:8080  (Site 'Plone', admin/admin)"

frontend-install: ## One-time: fetch Volto core (19.4.1) + install deps
	cd frontend && pnpm dlx mrs-developer missdev --no-config --fetch-https
	cd frontend && pnpm install

frontend: ## Start Volto dev server on :3000
	cd frontend && RAZZLE_API_PATH=http://localhost:8080/Plone pnpm start

stop: ## Stop the docker stack
	docker compose down

clean: ## Stop and remove volumes (fresh database!)
	docker compose down -v
