# Run after new droplet is created for live server and sets up some elements like
# folder structure.

#!/bin/bash

# Variables
APP_ROOT="/var/www/my_django_app"
DOMAIN="yourdomain.com"
STATIC_DIR="$APP_ROOT/static"
MEDIA_DIR="$APP_ROOT/media"
POSTGRES_DIR="$APP_ROOT/postgres"
SSL_DIR="$APP_ROOT/ssl"

# Update and upgrade the system
sudo apt update && sudo apt upgrade -y

# Install necessary packages
sudo apt install -y git certbot

# Create the root directory for the app and set ownership to the current user
sudo mkdir -p $APP_ROOT
sudo chown $USER:$USER $APP_ROOT

# Navigate to the app root directory
cd $APP_ROOT || exit

# Initialize git repository
git init

# Create directories for static files, media files, postgres, and SSL
mkdir -p $STATIC_DIR
mkdir -p $MEDIA_DIR
mkdir -p $POSTGRES_DIR
mkdir -p $SSL_DIR

# Obtain and set up SSL certificates using Certbot
sudo certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN

# Move the SSL certificates to the SSL directory
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $SSL_DIR
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $SSL_DIR

# Change ownership of the SSL directory to the current user
sudo chown -R $USER:$USER $SSL_DIR

# Final instructions
echo "Setup complete. Folders for static, media, postgres, and SSL files have been created."
echo "SSL certificates are stored in the $SSL_DIR directory."