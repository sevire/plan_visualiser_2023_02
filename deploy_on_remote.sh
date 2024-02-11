DO_DOCKER_REGISTRY_NAME=$1
GITHUB_SHA=$2

echo $DO_DOCKER_REGISTRY_NAME
echo $GITHUB_SHA

cd /docker_app_root/plan_visualiser_2023_02 || exit
git pull

# Login to registry
doctl registry login
docker ps

# Stop running Nginx container and remove old container.
docker stop plan_visualiser_2023_02-nginx-1
docker rm plan_visualiser_2023_02-nginx-1

# Stop running Gunicorn container and remove old container.
docker stop plan_visualiser_2023_02-django_gunicorn-1
docker rm plan_visualiser_2023_02-django_gunicorn-1

# Stop running Postgres container and remove old container.
docker stop plan_visualiser_2023_02-db-1
docker rm plan_visualiser_2023_02-db-1

# Run a new Nginx container from a new image
docker run -d \
--restart always \
--name plan_visualiser_2023_02-nginx-1 \
--port 80:80 \
"${DO_DOCKER_REGISTRY_NAME}"/plan_visualiser_2023_02-nginx:$(echo $GITHUB_SHA | head -c7)

# Run a new Gunicorn container from a new image
docker run -d \
--restart always \
--name plan_visualiser_2023_02-django_gunicorn-1 \
--volume .:/app \
--volume static:/static \
--port 8000:8000 \
"${DO_DOCKER_REGISTRY_NAME}"/plan_visualiser_2023_02-django_gunicorn:$(echo $GITHUB_SHA | head -c7)

# Run a new Postgres container from a new image
docker run -d \
--restart always \
--name plan_visualiser_2023_02-db-1 \
--volume data:/var/lib/postgresql/data \
"${DO_DOCKER_REGISTRY_NAME}"/postgres:$(echo $GITHUB_SHA | head -c7)