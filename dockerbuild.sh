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

echo "Re-building Docker images..."
test -e .env && source .env || echo "$0: warn: no '.env' file in $(pwd): default values will be used"

readonly LOG_DIR=$(pwd)/docker-build-logs
test -d $LOG_DIR || mkdir -p $LOG_DIR

readonly LOGFILE=${LOG_DIR}/plan_visualiser-"$(date '+%Y%m%d-%H%M%S')".log
exec 1>$LOGFILE
exec 2>&1

#echo "Taking docker down before rebuild"  # Not sure whether this is necessary but haven't found better way yet.
#docker compose down

echo "Docker compose beginning..."
docker compose up -d --detach --build

echo "Docker compose complete, pruning beginning..."
docker system prune -f

echo "Restarting containers after rebuild"
docker restart $(docker ps -q)

echo "Deployment to local Docker environment complete."