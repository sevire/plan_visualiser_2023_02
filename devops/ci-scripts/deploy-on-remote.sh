# Run on remote server, typically after rebuilding docker images, to pull latest image and restart containers

# =======================================================================================
# 1. Check environment variables and set from parameters if necessary.
# =======================================================================================

# Assigning the value from the environment variable or using the parameter passed
echo "Setting env variables from parameters..."
export POSTGRES_DB_NAME=${POSTGRES_DB_NAME_ARG:-$1}
export POSTGRES_USER=${POSTGRES_USER_ARG:-$2}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD_ARG:-$3}
export DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY_ARG:-$4}
export DOCKER_IMAGE_TAG=${DOCKER_IMAGE_TAG_ARG:-$5}
export DJANGO_ENVIRONMENT=${DJANGO_ENVIRONMENT_TYPE_ARG:-$6}
export DO_DOCKER_REGISTRY_NAME=${DO_DOCKER_REGISTRY_NAME_ARG:-$7}
export DO_DOCKER_REGISTRY_API_TOKEN=${DO_DOCKER_REGISTRY_API_TOKEN_ARG:-$8}
export SHARED_USER_NAME=${SHARED_USER_NAME:-$9}
export SHARED_USER_PASSWORD=${SHARED_USER_PASSWORD:-${10}}
export APP_USER_1_NAME=${APP_USER_1_NAME:-${11}}
export APP_USER_1_PASSWORD=${APP_USER_1_PASSWORD:-${12}}
export ADMIN_NAME=${ADMIN_NAME:-${13}}
export ADMIN_PASSWORD=${ADMIN_PASSWORD:-${14}}
export EMAIL_HOST=${SECRET_EMAIL_HOST:-${15}}
export EMAIL_USE_SSL=${SECRET_EMAIL_USE_SSL:-${16}}
export EMAIL_HOST_USER=${SECRET_EMAIL_HOST_USER:-${17}}
export EMAIL_HOST_PASSWORD=${SECRET_EMAIL_HOST_PASSWORD:-${18}}
export EMAIL_PORT=${SECRET_EMAIL_PORT:-${19}}


# Print out the values of the variables to help with debugging
echo "using POSTGRES_DB_NAME: ${POSTGRES_DB_NAME}"
echo "using POSTGRES_USER: ${POSTGRES_USER:0:4}"
echo "using POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:0:4}"
echo "using DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY:0:4}"
echo "using DOCKER_IMAGE_TAG: ${DOCKER_IMAGE_TAG:0:4}"
echo "using DJANGO_ENVIRONMENT: ${DJANGO_ENVIRONMENT:0:4}"
echo "using DO_DOCKER_REGISTRY_NAME: ${DO_DOCKER_REGISTRY_NAME:0:4}"
echo "using DO_DOCKER_REGISTRY_API_TOKEN: ${DO_DOCKER_REGISTRY_API_TOKEN:0:4}"
echo "using SHARED_USER_NAME: ${SHARED_USER_NAME:0:4}"
echo "using SHARED_USER_PASSWORD: ${SHARED_USER_PASSWORD:0:4}"
echo "using APP_USER_1_NAME: ${APP_USER_1_NAME:0:4}"
echo "using APP_USER_1_PASSWORD: ${APP_USER_1_PASSWORD:0:4}"
echo "using ADMIN_NAME: ${ADMIN_NAME:0:4}"
echo "using ADMIN_PASSWORD: ${ADMIN_PASSWORD:0:4}"
echo "using INITIAL_USER_EMAIL_DOMAIN: ${INITIAL_USER_EMAIL_DOMAIN:0:4}"
echo "using EMAIL_HOST: ${EMAIL_HOST:0:4}"
echo "using EMAIL_USE_SSL: ${EMAIL_USE_SSL:0:4}"
echo "using EMAIL_HOST_USER: ${EMAIL_HOST_USER:0:4}"
echo "using EMAIL_HOST_PASSWORD: ${EMAIL_HOST_PASSWORD:0:4}"
echo "using EMAIL_PORT: ${EMAIL_PORT:0:4}"

cd /var/www/app_root/app || exit
pwd

if [ "$DJANGO_ENVIRONMENT" = "staging" ]; then
    git pull https://github.com/sevire/plan_visualiser_2023_02.git Development
elif [ "$DJANGO_ENVIRONMENT" = "production" ]; then
    git pull https://github.com/sevire/plan_visualiser_2023_02.git master
else
    echo "WARNING: DJANGO_ENVIRONMENT is not set to a valid value (staging or production)."
fi

# Authorise access to registry and login
doctl auth init --access-token $DO_DOCKER_REGISTRY_API_TOKEN
doctl registry login

# Pull images and restart containers with new images
docker compose -f devops/docker/docker-compose-remote.yml up --detach
