# Inception: User Documentation

## 1. Provided Services
This infrastructure provides a fully functional, secure web application stack:
* **Nginx**: A web server acting as the secure entry point. It strictly accepts traffic over HTTPS (port 443) using TLSv1.2/TLSv1.3 protocols.
* **WordPress**: A dynamic content management system powered by PHP-FPM, processing the website logic.
* **MariaDB**: An isolated relational database securely storing all website content, user data, and site configurations.

## 2. Starting and Stopping the Infrastructure
Administrators can control the stack using the provided `Makefile` at the root of the project:
* **Start**: `make` (Builds and boots all services in the background).
* **Stop**: `make down` (Stops the services safely but preserves all database data and website files).
* **Reset**: `make fclean` (DANGER: Completely destroys the stack, removes all containers, and deletes all persistent data on the hard drive).

## 3. Accessing the Website and Administration Panel
To access the services, ensure your browser is navigating to the correct local domain. Because the project uses self-signed SSL certificates, your browser will display a security warning. You must click "Advanced" and proceed to the site.
* **Main Website**: [https://mkhashan.42.fr](https://mkhashan.42.fr)
* **Admin Panel**: [https://mkhashan.42.fr/wp-admin](https://mkhashan.42.fr/wp-admin)

## 4. Locating and Managing Credentials
Sensitive credentials are not hardcoded into the application. If an administrator needs to update or review the deployment passwords, they are located on the host machine in the `srcs/` directory:
* configurations  are found in `srcs/.env`.


## 5. Checking Service Health
To verify the stack is operating correctly, open a terminal on the host machine and run:
`docker ps`
You should see three containers (`nginx`, `wordpress`, `mariadb`) with a status of **Up**. 
If a service is failing, you can view its internal logs by running:
`docker logs <container_name>` (e.g., `docker logs mariadb`).