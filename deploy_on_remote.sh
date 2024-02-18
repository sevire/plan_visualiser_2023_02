cd /docker_app_root/plan_visualiser_2023_02 || exit
git pull

# Login to registry
doctl registry login

# Pull images and restart containers with new images
docker compose -f devops/docker/docker-compose-remote.yml up