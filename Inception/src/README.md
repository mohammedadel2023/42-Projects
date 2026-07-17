*This activity has been created as part of the 42 curriculum by mkhashan.*

**This repository contains my personal solutions for the 42 curriculum. It is provided for portfolio and educational purposes only. Active 42 students must not copy or use this code, as doing so violates the school's strict academic integrity policies and will result in severe penalties for plagiarism**

## Description
The Inception project is a System Administration exercise designed to broaden knowledge of containerization. The goal is to build a small, isolated infrastructure composed of multiple services (Nginx, WordPress, and MariaDB) running in dedicated Docker containers. This architecture demonstrates how to orchestrate a secure, multi-tier web application stack using Docker Compose, custom Dockerfiles, and persistent local volumes.

## Instructions
To deploy and interact with the infrastructure, you must execute the build process from a Linux Virtual Machine.

1. **Domain Routing**: Ensure your local DNS routes the custom domain to the local machine. Edit `/etc/hosts` and add:
   `127.0.0.1    mkhashan.42.fr`
2. **Environment Variables**: Ensure your `.env` file is properly configured in the `srcs/` directory.
3. **Build and Start**: Run the following command at the root of the repository to build the images and start the containers in detached mode:
   `make` or `make all`
4. **Stop the Stack**: To stop the containers without deleting data:
   `make down`
5. **Full Clean**: To stop the containers, delete all images, networks, and completely wipe the persistent data volumes:
   `make fclean`

## Resources
* [Docker Official Documentation](https://docs.docker.com/)
* [Nginx Core Directives](https://nginx.org/en/docs/)
* [MariaDB Server Documentation](https://mariadb.com/kb/en/documentation/)
* [WP-CLI Commands](https://developer.wordpress.org/cli/commands/)
* **AI Usage**: Artificial Intelligence (Google Gemini) was utilized during the development of this project strictly as an educational tutor. It was used to debug shell script timing issues (race conditions during database bootstrapping), explain the mechanics of Linux mount shadowing, and refine the structural layout of this documentation.

## Project Description & Architectural Choices
This infrastructure relies exclusively on custom-built Docker images running on a custom Docker bridge network. 

### Virtual Machines vs. Docker
A **Virtual Machine (VM)** virtualizes the physical hardware. It requires a Hypervisor and runs a full, independent Guest Operating System, making it resource-heavy. **Docker**, however, virtualizes the Operating System itself. Containers share the host OS kernel and are isolated using Linux namespaces and cgroups. This makes Docker containers incredibly lightweight, fast to boot, and highly portable.

### Secrets vs. Environment Variables
**Environment Variables** (`.env` files) are passed directly into the container's environment space. While convenient, they can be exposed if the container crashes and dumps its environment, or if a user runs `docker inspect`. **Docker Secrets** (or file-based secrets) mount the sensitive data as an in-memory file (usually in `/run/secrets/`). The application reads the file into memory and the secret is never exposed in the environment variables, providing a much higher level of security for passwords and API keys.

### Docker Network vs. Host Network
Using the **Host Network** removes network isolation; the container shares the host machine's exact IP and port space (e.g., binding to port 80 in the container binds directly to port 80 on the host). Using a custom **Docker Network** (specifically a Bridge network) creates an isolated subnet. Containers can securely communicate with each other using their container names as DNS records, and ports are only exposed to the host if explicitly published (like port 443 for Nginx).

### Docker Volumes vs. Bind Mounts
A **Docker Volume** is a storage mechanism completely managed by Docker, stored within Docker's internal directory structure (`/var/lib/docker/volumes/`). A **Bind Mount** maps a specific, absolute path from the host machine directly into the container (e.g., `/home/mkhashan/data/wordpress`). We use Bind Mounts in this project to ensure data persists directly in the user's home directory, allowing easy inspection and backup from the host OS.