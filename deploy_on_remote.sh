# Run on remote server, typically after rebuilding docker images, to pull latest image and restart containers

# =======================================================================================
# 1. Check environment variables and set from parameters if necessary.
# =======================================================================================

# Assigning the value from the environment variable or using the parameter passed
DOCKER_IMAGE_TAG_ARG=${DOCKER_IMAGE_TAG_ARG:-$1}
POSTGRES_DB_NAME_ARG=${POSTGRES_DB_NAME_ARG:-$2}
POSTGRES_USER_ARG=${POSTGRES_USER_ARG:-$3}
POSTGRES_PASSWORD_ARG=${POSTGRES_PASSWORD_ARG:-$4}
DJANGO_SECRET_KEY_ARG=${DJANGO_SECRET_KEY_ARG:-$5}
DO_DOCKER_REGISTRY_NAME_ARG=${DO_DOCKER_REGISTRY_NAME_AR:-$6}
DJANGO_ENVIRONMENT_TYPE_ARG=${DJANGO_ENVIRONMENT_TYPE_ARG:-$7}

# Print out the values of the variables to help with debugging
echo "using DOCKER_IMAGE_TAG_ARG: ${DOCKER_IMAGE_TAG_ARG:-<not set>}"
echo "using POSTGRES_DB_NAME_ARG: ${POSTGRES_DB_NAME_ARG:-<not set>}"
echo "using POSTGRES_USER_ARG: ${POSTGRES_USER_ARG:-<not set>}"
echo "using POSTGRES_PASSWORD_ARG: ${POSTGRES_PASSWORD_ARG:-<not set>}"
echo "using DJANGO_SECRET_KEY_ARG: ${DJANGO_SECRET_KEY_ARG:-<not set>}"
echo "using DO_DOCKER_REGISTRY_NAME_ARG: ${DO_DOCKER_REGISTRY_NAME_ARG:-<not set>}"
echo "using DJANGO_ENVIRONMENT_TYPE_ARG: ${DJANGO_ENVIRONMENT_TYPE_ARG:-<not set>}"


cd /var/www/app_root/app || exit
git pull

# Login to registry
doctl registry login

# Pull images and restart containers with new images
docker compose -f devops/docker/docker-compose-remote.yml up --detach
