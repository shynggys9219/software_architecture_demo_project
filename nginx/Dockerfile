FROM alpine:3.20
RUN apk add --no-cache nginx \
    && mkdir -p /run/nginx /var/log/nginx
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]