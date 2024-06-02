FROM alpine:latest

RUN apk add --no-cache apache2 

ENTRYPOINT ["httpd", "-D", "FOREGROUND"]