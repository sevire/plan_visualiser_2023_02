# Rebuilds all containers and then restarts them.
# NOTE: At the moment there is no intelligence to work out what might have changed and only rebuild changed things.
# The approach is to rebuild everything for safety.  Also note that if it's only source code that has changed, I don't
# believe that triggers a change to the containers so they wouldn't restart just by docker compose up, but at least
# Gunicorn needs to be restarted after code change to ensure that any caches are destroyed so changes are seen.

echo "dev-post-commit-build-docker.sh starting..."

# First check whether we need to override WIP test.
if [ "$1" != "--wip-override" ]
then
  # Check whether last commit was WIP (work in progress) commit.  If so then don't do anything.
  LAST_COMMIT_MSG=$(git log -1 --pretty=%B)
  if [[ $LAST_COMMIT_MSG = *'[WIP]'* ]]
  then
      echo "Work in progress commit, not rebuilding"
      exit 0
  else
      echo "Not work in progress commit so building docker images and deploying locally"
  fi
fi

# Define a directory for isolating the latest commit code
ISOLATED_DIR="/Users/Development/PycharmProjects/project_working_area/plan_visualiser_2023_02/local_docker_build"

# Clean the directory or create it if it doesn't exist
if [ -d "$ISOLATED_DIR" ]; then
  echo "Cleaning up isolated build directory..."
  rm -rf "$ISOLATED_DIR"
fi
mkdir -p "$ISOLATED_DIR"

# Clone the repo or fetch latest code
echo "Cloning the latest commit into the isolated directory..."
git clone . "$ISOLATED_DIR" --quiet
cd "$ISOLATED_DIR" || exit

# Ensure that the directory is "cleaned" to match the latest commit
echo "Resetting to the latest commit..."
git reset --hard HEAD --quiet

# Go back to the original working directory
cd - > /dev/null || exit

echo "Running tests..."
python manage.py test
EXIT_CODE=$?

# Check the exit code and abort if tests fail
if [ $EXIT_CODE -ne 0 ]; then
  echo "Tests failed. Aborting."
  exit $EXIT_CODE
fi

echo "Tests passed successfully."

echo "Re-building Docker images..."
echo "Before building images - working folder is $PWD"
./devops/ci-scripts/build-images.sh development || {
    echo "Error: Failed to build Docker images."
    exit 1
}

echo "Stopping any running containers..."
docker compose --env-file ./devops/env/.env.build.base -f ./devops/docker/docker-compose.base.yml -f ./devops/docker/docker-compose.dev.yml down || {
    echo "Error: Failed to stop existing containers."
    exit 1
}

echo "Starting containers using updated images..."
docker compose --env-file ./devops/env/.env.build.base -f ./devops/docker/docker-compose.base.yml -f ./devops/docker/docker-compose.dev.yml up -d || {
    echo "Error: Failed to start containers from updated images."
    exit 1
}

echo "Deployment to local Docker environment complete."
echo "dev-post-commit-build-docker.sh finishing"
