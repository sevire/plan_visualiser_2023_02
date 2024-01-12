echo "Re-building Docker images..."
#set -o errexit
#test -e .env && source .env || echo "$0: warn: no '.env' file in $(pwd): default values will be used"
#
readonly TMPDIR="/tmp/git-post-commit"
test -d $TMPDIR || mkdir -p $TMPDIR

readonly LOGFILE=$(mktemp -q ${TMPDIR}/plan_visualiser-"$(date '+%Y%m%d-%H%M%S')"-XXX.log)
exec 1>$LOGFILE
exec 2>&1

echo "Docker compose beginning..."
docker compose up -d --build

echo "Docker compose complete, pruning beginning..."
docker system prune -f

echo "Deployment to local Docker environment complete."