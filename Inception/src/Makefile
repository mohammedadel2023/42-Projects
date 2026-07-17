COMPOSE_FILE = srcs/docker-compose.yml

USER_LOGIN = mkhashan
DATA_PATH = /home/$(USER_LOGIN)/data
SERVICE_PATH = srcs/requirements
.PHONY: all build up down clean fclean re

all: build up

build:
	@mkdir -p $(DATA_PATH)/wordpress
	@mkdir -p $(DATA_PATH)/mariadb
	@docker compose -f $(COMPOSE_FILE) build

up:
	@docker compose -f $(COMPOSE_FILE) up -d

down:
	@docker compose -f $(COMPOSE_FILE) down

clean: down
	@docker system prune -a --force

fclean: clean
	@docker volume rm $$(docker volume ls -q) 2>/dev/null || true
	@sudo rm -rf $(DATA_PATH)/wordpress
	@sudo rm -rf $(DATA_PATH)/mariadb
	@sudo rm -rf $(DATA_PATH)

re: fclean all
