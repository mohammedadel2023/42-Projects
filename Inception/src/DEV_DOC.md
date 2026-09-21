# Inception: Developer Documentation

## 1. Setting Up the Environment
To deploy this project from scratch, ensure you have a clean Linux environment (Virtual Machine) with `docker`, `docker-compose-plugin`, and `make` installed.

Before building, you must configure your local environment variables and secrets:
1. Navigate to the `srcs/` directory.
2. Create a `.env` file containing the required deployment variables (e.g., `DOMAIN_NAME`, `DB_NAME`, `MYSQL_USER`) or copy the .env.example file.
3. Ensure the host directories required for persistence exist (handled automatically by the Makefile), or create them manually at `/home/mkhashan/data/wordpress` and `/home/mkhashan/data/mariadb`.

## 2. Building and Launching the Stack
The entire lifecycle of the application is managed via the `Makefile` utilizing Docker Compose.
* `make build`: Instructs Docker Compose to parse `srcs/docker-compose.yml`, read the custom Dockerfiles in the respective service directories (`srcs/requirements/`), and compile the images.
* `make up`: Launches the compiled images, attaching them to the custom `inception` bridge network.
* `make re`: A development command that fully cleans the system using `fclean` and rebuilds the stack to test fresh initializations.

## 3. Container and Volume Management Commands
When developing or debugging, these Docker CLI commands are essential:
* **Interactive Shell**: To enter a running container to debug configurations or file permissions:
  `docker exec -it <container_name> /bin/bash`
* **Inspect Network**: To verify that Nginx, WordPress, and MariaDB are communicating on the same subnet:
  `docker network inspect inception`
* **Manage Volumes**: To list current Docker volumes and verify they are mapped correctly:
  `docker volume ls`
  `docker volume inspect <volume_name>`

## 4. Data Storage and Persistence
Containers are ephemeral by nature. To ensure database records and website files survive container restarts or crashes, we use explicit **Bind Mounts** defined in the `docker-compose.yml`.

Data is persisted on the host machine at the following absolute paths:
* **Database Persistence**: MariaDB's `/var/lib/mysql` directory is bound to `/home/mkhashan/data/mariadb`.
* **Website Persistence**: The Nginx and WordPress `/var/www/html` directory is bound to `/home/mkhashan/data/wordpress`.

*Note on Initialization*: The entrypoint scripts inside the custom `mariadb` and `wordpress` containers are designed to check if these mapped host directories are empty on boot. If they are, the scripts will dynamically populate them with the core database system tables and WordPress core files, respectively.