#!make
define load_env
    $(eval include .env)
    $(eval export)
endef

up:
	$(call load_env)
	@docker compose -f .deployment/docker-compose.yaml up -d
down:
	$(call load_env)
	@docker compose -f .deployment/docker-compose.yaml down
build:
	$(call load_env)
	@docker compose -f .deployment/docker-compose.yaml build
rebuild:
	$(call load_env)
	@docker compose -f .deployment/docker-compose.yaml up -d --build
