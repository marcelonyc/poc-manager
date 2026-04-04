FROM nginx:alpine

ARG VERSION=latest
LABEL org.opencontainers.image.version="${VERSION}"

# Bake in the reverse-proxy configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
