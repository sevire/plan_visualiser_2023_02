# Run on remote server, typically after rebuilding docker images, to pull latest image and restart containers

# =======================================================================================
# 1. Check environment variables and set from parameters if necessary.
# =======================================================================================

# Assigning the value from the environment variable or using the parameter passed
export POSTGRES_DB_NAME_ARG=${POSTGRES_DB_NAME_ARG:-$1}
export POSTGRES_USER_ARG=${POSTGRES_USER_ARG:-$2}
export POSTGRES_PASSWORD_ARG=${POSTGRES_PASSWORD_ARG:-$3}
export DJANGO_SECRET_KEY_ARG=${DJANGO_SECRET_KEY_ARG:-$4}
export DOCKER_IMAGE_TAG_ARG=${DOCKER_IMAGE_TAG_ARG:-$5}
export DJANGO_ENVIRONMENT_TYPE_ARG=${DJANGO_ENVIRONMENT_TYPE_ARG:-$6}
export DO_DOCKER_REGISTRY_NAME_ARG=${DO_DOCKER_REGISTRY_NAME_ARG:-$7}
export DO_DOCKER_REGISTRY_API_TOKEN=${DO_DOCKER_REGISTRY_API_TOKEN_ARG:-$8}

# Print out the values of the variables to help with debugging
echo "using POSTGRES_DB_NAME_ARG: ${POSTGRES_DB_NAME_ARG:-<not set>}"
echo "using POSTGRES_USER_ARG: ${POSTGRES_USER_ARG:-<not set>}"
echo "using POSTGRES_PASSWORD_ARG: ${POSTGRES_PASSWORD_ARG:-<not set>}"
echo "using DJANGO_SECRET_KEY_ARG: ${DJANGO_SECRET_KEY_ARG:-<not set>}"
echo "using DOCKER_IMAGE_TAG_ARG: ${DOCKER_IMAGE_TAG_ARG:-<not set>}"
echo "using DJANGO_ENVIRONMENT_TYPE_ARG: ${DJANGO_ENVIRONMENT_TYPE_ARG:-<not set>}"
echo "using DO_DOCKER_REGISTRY_NAME_ARG: ${DO_DOCKER_REGISTRY_NAME_ARG:-<not set>}"
edho "using DO_DOCKER_REGISTRY_API_TOKEN_ARG: ${DO_DOCKER_REGISTRY_API_TOKEN_ARG:-<not set>}"


cd /var/www/app_root/app || exit
git pull https://github.com/sevire/plan_visualiser_2023_02.git master

# Authorise access to registry and login
doctl auth init --access-token $DO_DOCKER_REGISTRY_API_TOKEN_ARG
doctl registry login

# Pull images and restart containers with new images
docker compose -f devops/docker/docker-compose-remote.yml up --detach
