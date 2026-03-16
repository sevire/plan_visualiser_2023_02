#!/bin/bash

# Script to build Docker images selectively and push them to the container registry
# Usage: ./build-images.sh [environment] [--push]
# Parameters:
#   [environment]         - The target environment (e.g., dev, staging, prod)
#   [--push]              - Optional flag to push images to the container registry.

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting Docker image build process..."

# Parse input arguments
ENVIRONMENT=$1
PUSH_IMAGES=false

# Read optional flags
for arg in "$@"; do
  if [ "$arg" == "--push" ]; then
    PUSH_IMAGES=true
  fi
done

if [ -z "$ENVIRONMENT" ]; then
  echo "Error: Environment not specified. Usage: ./build-images.sh [environment] [--push]."
  exit 1
fi

# Source build-time vars from .env.build
source ./devops/env/.env.build.base

# Source environment dependent build vars from .env.build.<enviuronment>
# May override base vars.

# Disable shellcheck as it can't validate dynamically generated path.
# shellcheck disable=SC1090
source "./devops/env/.env.build.$ENVIRONMENT"

# Generate image tags (based on Git SHA)
# If environment is development then use 'local' tag, otherwise use Git SHA
# Also only include full repository prefix for non development environments
if [ "${ENVIRONMENT}" = "development" ]; then
  echo "Building image names for development environment"
  IMAGE_TAG="dev"
  IMAGE_PREFIX=""
else
  echo "Building image names for staging/production environment"
  GIT_COMMIT=$(git rev-parse --short HEAD)
  IMAGE_TAG="${GIT_COMMIT}"
  IMAGE_PREFIX=$REGISTRY_PREFIX
fi

# Helper function to build Docker images
build_image() {
  local image_name=$1
  local dockerfile_path=$2

  echo "Building image: $image_name with tag: $IMAGE_TAG"
  docker build --no-cache -t "$image_name:$IMAGE_TAG" -f "$dockerfile_path" .
}

# Helper function to push Docker images
push_image() {
  local image_name=$1

  echo "Pushing image: $image_name with tag: $IMAGE_TAG"
  docker push "$image_name:$IMAGE_TAG"
}

# Build Gunicorn and NGINX images
echo "Building core Docker images for environment: $ENVIRONMENT"
build_image "$IMAGE_PREFIX$GUNICORN_IMAGE" "./devops/docker/gunicorn/Dockerfile"
build_image "$IMAGE_PREFIX$NGINX_IMAGE" "./devops/docker/nginx/Dockerfile"

# Optionally push images to the registry
if [ "$PUSH_IMAGES" = true ]; then
  echo "Pushing core images to the registry..."
  push_image "$IMAGE_PREFIX$GUNICORN_IMAGE"
  push_image "$IMAGE_PREFIX$NGINX_IMAGE"
fi

echo "Docker image build process completed successfully!"