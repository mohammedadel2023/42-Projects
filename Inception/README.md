# 🐳 Inception: Systems Architecture Teardown
**This project has been created as part of the 42 curriculum by Mohammad Khashan.**

**This document serves as the technical breakdown and architectural analysis for the 42 Inception project.**

**This repository contains my personal solutions for the 42 curriculum. It is provided for portfolio and educational purposes only. Active 42 students must not copy or use this code, as doing so violates the school's strict academic integrity policies and will result in severe penalties for plagiarism**
## 1. Project Overview
Inception is a System Administration exercise designed to broaden knowledge of containerization and DevOps infrastructure. The objective is to build a small, highly secure, isolated microservice web application cluster from scratch, completely avoiding pre-built vendor images (like the official Docker Hub WordPress or MariaDB images).

**Core Tech Stack:**
* **Orchestration:** Docker Compose
* **OS Base:** Debian 12 (or Alpine)
* **Web Server:** Nginx (TLSv1.2/1.3 only)
* **Application:** WordPress + PHP-FPM
* **Database:** MariaDB

---

## 2. Infrastructure Architecture


![alt text](<LEMP_STACK.png>)

### The "One Container, One Service" Philosophy
This infrastructure strictly adheres to microservice best practices. Process managers (like `systemd` or `supervisord`) are intentionally omitted. Each container executes exactly one foreground process (PID 1), ensuring that if a service fails, the container gracefully crashes and is handled by the Docker daemon's restart policies.

---

## 3. Core System Engineering

### A. The Nginx Edge Router
Nginx serves as the sole entry point to the infrastructure. 
* **Network Isolation:** It is the only container that binds to the host machine's physical network via exposed port `443`.
* **Security:** HTTP traffic (port 80) is either blocked or permanently redirected. All traffic is encrypted using a self-signed SSL/TLS certificate generated during the container build phase.
* **FastCGI Proxying:** Nginx does not render PHP. Instead, it acts as a reverse proxy, translating HTTP requests into the FastCGI protocol and passing them over the internal Docker network to the WordPress container on port `9000`.

### B. WordPress & PHP-FPM
This container houses the core application logic.
* **Dynamic Configuration:** It utilizes `WP-CLI` in its entrypoint script. Upon boot, it reads environment variables (`.env`) to dynamically generate the `wp-config.php` file, create the database tables, and provision the admin and author users without human intervention.
* **Synchronous Bootstrapping:** To prevent race conditions during startup, this container implements healthchecks (or TCP wait-loops) to ensure it does not attempt to contact MariaDB until the database socket is confirmed to be open and listening.

### C. MariaDB Engine
The database is completely isolated from the outside world.
* **Network Security:** It binds to `0.0.0.0` internally but exposes no ports to the host machine. It can only be accessed by containers residing on the shared `inception` bridge network.
* **Initialization:** A custom Bash entrypoint script intercepts the boot process. If the persistent volume is empty, it securely builds the MySQL system tables, bootstraps the WordPress user, sets root passwords, and safely restarts the daemon into normal operational mode.

---

## 4. State Management & Persistence

Containers are ephemeral; their internal writable layers are destroyed upon removal. To ensure data persistence across updates and crashes, this project utilizes **Bind Mounts**.

* **Database Persistence:** The container path `/var/lib/mysql` is mounted directly to the host OS path `/home/$USER/data/mariadb`. 
* **Application Persistence:** The container path `/var/www/html` is mounted to `/home/$USER/data/wordpress`.

This approach ensures that user uploads, theme modifications, and database records remain immutable on the physical hard drive, surviving complete teardowns (`docker compose down`) and rebuilds.