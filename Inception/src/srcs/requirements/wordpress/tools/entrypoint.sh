#!/bin/bash


echo "start runing entrypoint script"
# 1. Copy the safe files into the mounted volume if it is empty
if [ ! -f /var/www/html/wp-config.php ]; then
    cp -a /tmp/wordpress-core/. /var/www/html/
    chown -R www-data:www-data /var/www/html/
fi 

# 3. Proceed with wp-cli setup
echo "start wordpress config using wp-cli"
wp config create \
      --dbname="$DB_NAME" \
      --dbuser="$MYSQL_USER" \
      --dbpass="$MYSQL_PASSWORD" \
      --dbhost="$DB_HOST" \
      --allow-root

wp core install \
      --url="$DOMAIN_NAME" \
      --title="$WP_TITLE" \
      --admin_user="$WP_ADMIN_USER" \
      --admin_password="$WP_ADMIN_PASSWORD" \
      --admin_email="$WP_ADMIN_EMAIL" \
      --skip-email \
      --allow-root

wp user create \
      "$WP_USER" \
      "$WP_USER_EMAIL" \
      --user_pass="$WP_USER_PASSWORD" \
      --role=author \
      --allow-root
echo "start the PID1 of wordpress container"        
exec "$@"
