FROM alpine:latest

RUN addgroup -g 101 -S nginx \
    && adduser -S -D -H -u 101 -s /sbin/nologin -G nginx -g nginx nginx \
    && apk add --no-cache nginx

COPY /mass/nginx/nginx.conf /etc/nginx/

USER nginx
ENTRYPOINT ["nginx", "-g", "daemon off;"]