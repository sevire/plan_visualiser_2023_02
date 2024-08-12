# Run on remote server, typically after rebuilding docker images, to pull latest image and restart containers

export DOCKER_IMAGE_TAG=$1
export POSTGRES_DB_NAME_ARG=$POSTGRES_DB_NAME
export POSTGRES_USER_ARG=$POSTGRES_USER
export POSTGRES_PASSWORD_ARG=$POSTGRES_DB_PASSWORD
export DJANGO_SECRET_KEY_ARG="$DJANGO_SECRET_KEY"
export DO_DOCKER_REGISTRY_NAME_ARG=$DO_DOCKER_REGISTRY_NAME
export DJANGO_ENVIRONMENT_TYPE_ARG=$DJANGO_ENVIRONMENT_TYPE

cd /docker_app_root/plan_visualiser_2023_02 || exit
git pull

# Login to registry
doctl registry login

# Pull images and restart containers with new images
docker compose -f devops/docker/docker-compose-remote.yml up --detach
