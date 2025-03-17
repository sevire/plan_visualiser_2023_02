# Rebuilds all containers and then restarts them.
# NOTE: At the moment there is no intelligence to work out what might have changed and only rebuild changed things.
# The approach is to rebuild everything for safety.  Also note that if it's only source code that has changed, I don't
# believe that triggers a change to the containers so they wouldn't restart just by docker compose up, but at least
# Gunicorn needs to be restarted after code change to ensure that any caches are destroyed so changes are seen.

# First check whether we need to override WIP test.
if [ "$1" != "--no-wip" ]
then
  # Check whether last commit was WIP commit.  If so then don't do anything.
  LAST_COMMIT_MSG=$(git log -1 --pretty=%B)
  if [[ $LAST_COMMIT_MSG = *'[WIP]'* ]]
  then
      echo "Work in progress commit, not rebuilding"
      exit 0
  fi
fi

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

echo "Checking .env file..."
test -e .env && source .env || echo "$0: warn: no '.env' file in $(pwd): default values will be used"

echo "Setting up log folder and file..."
readonly LOG_DIR=$(pwd)/docker-build-logs
test -d $LOG_DIR || mkdir -p $LOG_DIR

readonly LOGFILE=${LOG_DIR}/plan_visualiser-"$(date '+%Y%m%d-%H%M%S')".log
exec 1>$LOGFILE
exec 2>&1

echo "Docker compose beginning..."
docker compose -f devops/docker/docker-compose-dev.yml up --detach --build

echo "Docker compose complete, pruning beginning..."
docker system prune -f

echo "Restarting containers after rebuild"
docker restart $(docker ps -q)

echo "Deployment to local Docker environment complete."