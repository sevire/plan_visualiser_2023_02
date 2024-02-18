# Script to be run as github action which rebuilds all three Docker images and pushes them to the Digital Ocean
# registry.
#
# Doesn't do anything if the last commit was a Work In Progress [WIP] commit, so that non-working code can still be
# merged and pushed without generating a non-working Staging environment.  This check can be overridden with the
# --no-wip-check flag. This allows for the case when a commit is unintentionally flageed as [WIP]

# First check whether we need to override WIP test.
if [ "$1" == "--no-wip-check" ]
then
  echo "Overriding WIP check, building anyway"
else
  # Check whether last commit was WIP commit.  If so then don't do anything.
  LAST_COMMIT_MSG=$(git log -1 --pretty=%B)
  if [[ $LAST_COMMIT_MSG = *'[WIP]'* ]]
  then
      echo "WIP commit, not rebuilding"
      exit 0
  fi
fi

echo "Re-building Docker images..."
test -e .env && source .env || echo "$0: warn: no '.env' file in $(pwd): default values will be used"

readonly LOG_DIR=$(pwd)/docker-build-logs
test -d $LOG_DIR || mkdir -p $LOG_DIR

readonly LOGFILE=${LOG_DIR}/plan_visualiser-staging-build-"$(date '+%Y%m%d-%H%M%S')".log
exec 1>$LOGFILE
exec 2>&1

echo "Starting build..."
docker build .

echo "Docker build complete, pruning beginning..."
docker system prune -f

echo "Build complete, beginning push to Digital Ocean registry"

echo "Pushing nginx..."
docker tag nginx-1 registry.digitalocean.com/gen-business-docker-rep-01/nginx-1
docker push registry.digitalocean.com/gen-business-docker-rep-01/plan_visualiser_2023_02-nginx








echo "Docker compose beginning..."
docker compose up -d --detach --build

echo "Restarting containers after rebuild"
docker restart $(docker ps -q)

echo "Deployment to local Docker environment complete."