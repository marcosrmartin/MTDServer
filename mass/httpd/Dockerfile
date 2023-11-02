FROM alpine:latest

RUN apk add --no-cache apache2 \
    && sed -i 's/Listen 80/Listen 8008/' /etc/apache2/httpd.conf 

ENTRYPOINT ["httpd", "-D", "FOREGROUND"]