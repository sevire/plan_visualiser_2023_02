FROM nginx:1.19.10-alpine

# Copy all versions of nginx conf file to the image and choose which one to use during deployment
COPY ./devops/docker/nginx/default-dev.conf /etc/nginx/default-dev.conf
COPY ./devops/docker/nginx/default-staging.conf /etc/nginx/default-staging.conf
COPY ./devops/docker/nginx/default-production.conf /etc/nginx/default-production.conf

# Add an entry point script to allow runtime setup
COPY ./devops/docker/nginx/docker-nginx-entrypoint.sh /docker-nginx-entrypoint.sh

RUN chmod +x /docker-nginx-entrypoint.sh

# Start Nginx with your default entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
