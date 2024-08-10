#!/bin/bash
# Script Name: live_server_setup.sh
# Author: Thomas Gaylard
# Date: 2024-08-10
# Description:
#   This script is used when deploying the app to the live server for the first time.  It carries out a number of one
#   off tasks which need to be carried out when setting up a new server, such as creating the folder structure and
#   git repository and link to remote repository to allow git pulling the updated app.
#
#   It also sets up the SSL certificates.
#
# Usage:
#   Usually invoked from a github action but can be run manually if environment variables have been set up correctly.
#   Access environment variables for key parameters and
#
# Version: 1.0

set -e

# =======================================================================================
# 1. Check environment variables and set from parameters if necessary.
# =======================================================================================

# Assigning the value from the environment variable or using the parameter passed
DOMAIN_NAME=${DOMAIN_NAME:-$1}
EMAIL=${EMAIL:-$2}
DNS_UPDATE_API=${DNS_UPDATE_API:-$3}

# Print out the values of the variables to help with debugging
echo "Using DOMAIN_NAME: $DOMAIN_NAME"
echo "Using EMAIL: ${EMAIL:-<not set>}"
echo "Using DNS_UPDATE_API: ${DNS_UPDATE_API:-<not set>}"

# =======================================================================================
# 2. Don't run script if has server already set up.
# =======================================================================================

if [ -f "/var/www/.setup_done" ]; then
    echo "Setup has already been done. Exiting live_server_setup."
    exit 0
fi

# =======================================================================================
# 3. Initialise key variables which aren't passed in as parameters or env.
# =======================================================================================

APP_ROOT="/var/www/app_root"
APP="/var/www/app_root/app"
STATIC_DIR="$APP_ROOT/static"
MEDIA_DIR="$APP_ROOT/media"
POSTGRES_DIR="$APP_ROOT/postgres"
SSL_DIR="$APP_ROOT/ssl"

# =======================================================================================
# 4. Update packages required for set up.
# =======================================================================================

echo "Updating packages..."
sudo apt-get update && sudo apt-get upgrade -y

echo "Installing certbot"
sudo apt install -y git certbot

echo "Installing pip"
sudo apt install python3-pip

echo "installing certbot-dns-digitalocean"
sudo pip install certbot-dns-digitalocean

# =======================================================================================
# 5. Create folders for the app and initialise git repo.
# =======================================================================================

echo "Creating app root folder..."
sudo mkdir -p $APP_ROOT
sudo chown $USER:$USER $APP_ROOT

# Navigate to the app root directory
cd $APP_ROOT || exit

# Create directories for static files, media files, postgres, and SSL
mkdir -p $APP
mkdir -p $STATIC_DIR
mkdir -p $MEDIA_DIR
mkdir -p $POSTGRES_DIR
mkdir -p $SSL_DIR

# Initialize git repository
echo "Initialising git repo and setting up remote to pull app code"

# Add the remote repository
git clone --bare https://github.com/sevire/plan_visualiser_2023_02.git $APP

# =======================================================================================
# 6. Set up SSL certificate.
# =======================================================================================

# Create Digital Ocean ini file which allows API access to support DNS challenge...

# Ensure the API token is available
if [ -z "$DNS_UPDATE_API" ]; then
  echo "Error: DNS_UPDATE_API is not set."
  exit 1
fi

# Create the digitalocean.ini file
cat << EOF > /etc/letsencrypt/digitalocean.ini
dns_digitalocean_token=$DNS_UPDATE_API
EOF

# Set appropriate permissions
sudo chmod 600 /etc/letsencrypt/digitalocean.ini

# Obtain and set up SSL certificates using Certbot
sudo certbot certonly \
  --non-interactive \
  --agree-tos \
  --email "$EMAIL" \
  --dns-digitalocean \
  --dns-digitalocean-credentials /etc/letsencrypt/digitalocean.ini \
  -d "$DOMAIN_NAME" \
  -d www."$DOMAIN_NAME"

sudo certbot certonly --standalone -d "$DOMAIN_NAME" -d www."$DOMAIN_NAME" --email "$EMAIL" --agree-tos --non-interactive

# Move the SSL certificates to the SSL directory
sudo cp /etc/letsencrypt/live/"$DOMAIN_NAME"/fullchain.pem $SSL_DIR
sudo cp /etc/letsencrypt/live/"$DOMAIN_NAME"/privkey.pem $SSL_DIR

# Change ownership of the SSL directory to the current user
sudo chown -R "$USER":"$USER" $SSL_DIR

# Final instructions
echo "Setup complete. Folders for static, media, postgres, and SSL files have been created."
echo "SSL certificates are stored in the $SSL_DIR directory."

# Create marker file to indicate that setup is complete.
touch "/var/www/.setup_done"