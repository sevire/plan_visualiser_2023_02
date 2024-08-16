# Run on remote server, typically after rebuilding docker images, to pull latest image and restart containers

# =======================================================================================
# 1. Check environment variables and set from parameters if necessary.
# =======================================================================================

# Assigning the value from the environment variable or using the parameter passed
export POSTGRES_DB_NAME=${POSTGRES_DB_NAME_ARG:-$1}
export POSTGRES_USER=${POSTGRES_USER_ARG:-$2}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD_ARG:-$3}
export DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY_ARG:-$4}
export DOCKER_IMAGE_TAG=${DOCKER_IMAGE_TAG_ARG:-$5}
export DJANGO_ENVIRONMENT_TYPE=${DJANGO_ENVIRONMENT_TYPE_ARG:-$6}
export DO_DOCKER_REGISTRY_NAME=${DO_DOCKER_REGISTRY_NAME_ARG:-$7}
export DO_DOCKER_REGISTRY_API_TOKEN=${DO_DOCKER_REGISTRY_API_TOKEN_ARG:-$8}

# Print out the values of the variables to help with debugging
echo "using POSTGRES_DB_NAME: ${POSTGRES_DB_NAME:-<not set>}"
echo "using POSTGRES_USER: ${POSTGRES_USER:-<not set>}"
echo "using POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-<not set>}"
echo "using DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY:-<not set>}"
echo "using DOCKER_IMAGE_TAG: ${DOCKER_IMAGE_TAG:-<not set>}"
echo "using DJANGO_ENVIRONMENT_TYPE: ${DJANGO_ENVIRONMENT_TYPE:-<not set>}"
echo "using DO_DOCKER_REGISTRY_NAME: ${DO_DOCKER_REGISTRY_NAME:-<not set>}"
echo "using DO_DOCKER_REGISTRY_API_TOKEN: ${DO_DOCKER_REGISTRY_API_TOKEN:-<not set>}"


cd /var/www/app_root/app || exit
git pull https://github.com/sevire/plan_visualiser_2023_02.git master

# Authorise access to registry and login
doctl auth init --access-token $DO_DOCKER_REGISTRY_API_TOKEN
doctl registry login

# Pull images and restart containers with new images
docker compose -f devops/docker/docker-compose-remote.yml up --detach
