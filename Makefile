COMPOSE_BASE_COMMAND=docker compose
COMPOSE_FILE_ARG=-f deploy/docker-compose.yml
DEV_COMPOSE_FILE_ARG=-f deploy/docker-compose.dev.yml
PROJECT_DIR_ARG=--project-directory .

COMPOSE_COMMAND=$(COMPOSE_BASE_COMMAND) $(COMPOSE_FILE_ARG) $(DEV_COMPOSE_FILE_ARG) $(PROJECT_DIR_ARG)
RUN_IN_API=$(COMPOSE_COMMAND) run --build --rm api


## Migrations:
gen_migrations: down
	# Annoying but you have to manually chmod/chown migrations after they're
	# generated since they're made through the Docker container.
	$(RUN_IN_API) poetry run aerich migrate

upgrade_migrations:
	$(RUN_IN_API) poetry run aerich upgrade

downgrade_migrations:
	$(RUN_IN_API) poetry run aerich downgrade


## Testing:
test:
	$(RUN_IN_API) pytest -p no:cacheprovider -vv .


## Running:
local_serve:
	$(COMPOSE_COMMAND) up --build


## Utils:
down:
	@$(COMPOSE_COMMAND) down

cli:
	@$(RUN_IN_API) bash


## CI Related:
run_ci_locally:
	echo "If you don't have nix-shell installed, go to https://nixos.org/download.html"
	nix-shell -p act --run "act --secret-file env.secrets --env-file env.secrets -j black --insecure-secrets"
