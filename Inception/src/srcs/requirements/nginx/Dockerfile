FROM debian:12

RUN apt update
RUN  apt install nginx -y
RUN apt install openssl
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/selfsigned-nginx.key -out /etc/ssl/certs/selfsigned-nginx.crt \
     -subj "/C=JO/ST=Irbid/L=Irbid/O=42/CN=mkhashan.42.fr" 
COPY conf/nginx.conf /etc/nginx/conf.d/nginx.conf


EXPOSE 443
CMD ["nginx", "-g", "daemon off;"]
