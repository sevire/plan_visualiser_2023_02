#!/bin/sh

# =============================
# Git Post-Commit Hook Script
# Handles Jira updates and Docker rebuilds in development environment
# =============================

# Exit on any error
set -e

# =============================
# Load environment variables
# =============================
REPO_ROOT="$(git rev-parse --show-toplevel)"
ENV_FILE="$REPO_ROOT/devops/env/.env.git-hooks"

if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$ENV_FILE"
    set +a
else
    echo "Warning: .env file not found at $ENV_FILE"
fi

# =============================
# Extract commit message + Jira key
# =============================
COMMIT_MSG=$(git log -1 --pretty=%B)
GIT_HOOK_DEBUG_LOG_FILE="devops/logs/git_hook_debug.log"
JIRA_ISSUE=$(echo "$COMMIT_MSG" | grep -oE '\[[A-Z]+-[0-9]+\]' | tr -d '[]')

echo "Debug Info: Commit message: $COMMIT_MSG" >> "$GIT_HOOK_DEBUG_LOG_FILE"
echo "Debug Info: Jira issue: $JIRA_ISSUE" >> "$GIT_HOOK_DEBUG_LOG_FILE"

# =============================
# Post to Jira (if key + env present)
# =============================
if [ -n "$JIRA_ISSUE" ] && [ -n "$JIRA_URL" ] && [ -n "$JIRA_USER" ] && [ -n "$JIRA_API_TOKEN" ]; then
    if ! command -v jq >/dev/null 2>&1; then
        echo "Error: 'jq' is not installed or not in PATH."
        exit 1
    fi

    RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/jira_response.json \
        -X POST -u "$JIRA_USER:$JIRA_API_TOKEN" \
        -H "Content-Type: application/json" \
        --data "$(echo "$COMMIT_MSG" | jq -Rs '{"body": .}')" \
        "$JIRA_URL/rest/api/2/issue/$JIRA_ISSUE/comment")

    HTTP_CODE="$RESPONSE"
    echo "Jira API HTTP Status: $HTTP_CODE" >> "$GIT_HOOK_DEBUG_LOG_FILE"
    cat /tmp/jira_response.json >> "$GIT_HOOK_DEBUG_LOG_FILE"

    if [ "$HTTP_CODE" -ge 300 ]; then
        echo "Error: Jira API call failed with status $HTTP_CODE"
        exit 1
    fi
else
    echo "Info: Skipping Jira update (missing issue key or credentials)"
fi

# =============================
# Rebuild Docker image
# =============================
echo "Running dev-post-commit-build-docker.sh..."
"$REPO_ROOT/devops/ci-scripts/dev-build-docker.sh" || {
    echo "Error: Docker build failed"
    exit 1
}