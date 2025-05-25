#!/bin/bash

# Script to build Docker images selectively and push them to the container registry
# Usage: ./build-images.sh [environment] [--push] [--include-postgres]
# Parameters:
#   [environment]         - The target environment (e.g., dev, staging, prod)
#   [--push]              - Optional flag to push images to the container registry.
#   [--include-postgres]  - Optional flag to include the Postgres image in the build.

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting Docker image build process..."

# Parse input arguments
ENVIRONMENT=$1
PUSH_IMAGES=false
INCLUDE_POSTGRES=false

# Read optional flags
for arg in "$@"; do
  if [ "$arg" == "--push" ]; then
    PUSH_IMAGES=true
  elif [ "$arg" == "--include-postgres" ]; then
    INCLUDE_POSTGRES=true
  fi
done

if [ -z "$ENVIRONMENT" ]; then
  echo "Error: Environment not specified. Usage: ./build-images.sh [environment] [--push] [--include-postgres]."
  exit 1
fi

# Source build-time vars from .env.build
source ./devops/env/.env.build

# Generate image tags (based on Git SHA)
GIT_COMMIT=$(git rev-parse --short HEAD)
IMAGE_TAG="${GIT_COMMIT}"

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
build_image "$GUNICORN_IMAGE" "./devops/docker/gunicorn/Dockerfile"
build_image "$NGINX_IMAGE" "./devops/docker/nginx/Dockerfile"

# Build Postgres image optionally
if [ "$INCLUDE_POSTGRES" = true ]; then
  echo "Including Postgres in the build process..."
  build_image "$POSTGRES_IMAGE" "./devops/docker/postgres/Dockerfile"
fi

# Optionally push images to the registry
if [ "$PUSH_IMAGES" = true ]; then
  echo "Pushing core images to the registry..."
  push_image "$GUNICORN_IMAGE"
  push_image "$NGINX_IMAGE"

  if [ "$INCLUDE_POSTGRES" = true ]; then
    echo "Pushing Postgres image to the registry..."
    push_image "$POSTGRES_IMAGE"
  fi
fi

echo "Docker image build process completed successfully!"