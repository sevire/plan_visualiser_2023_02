#!/bin/sh

# Fail immediately if any commands fail
set -e
   
# Check the ENVIRONMENT variable to select the config file (default to dev)
case "$ENVIRONMENT" in
    production)
        echo "Using production configuration"
        cp /etc/nginx/default-production.conf /etc/nginx/conf.d/default.conf
        ;;
    staging)
        echo "Using staging configuration"
        cp /etc/nginx/default-staging.conf /etc/nginx/conf.d/default.conf
        ;;
    development)
        echo "Using dev configuration"
        cp /etc/nginx/default-dev.conf /etc/nginx/conf.d/default.conf
        ;;
    *)
        echo "Unknown environment: $ENVIRONMENT"
        echo "Defaulting to dev configuration"
        cp /etc/nginx/default-dev.conf /etc/nginx/conf.d/default.conf
        ;;
esac

# Start Nginx
exec "$@"