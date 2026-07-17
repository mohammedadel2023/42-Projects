FROM debian:12

RUN apt update && \
    apt install  mariadb-server -y


COPY tools/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh


EXPOSE 3306


ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["mariadbd", "--user=mysql", "--bind-address=0.0.0.0"]