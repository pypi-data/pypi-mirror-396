#!/usr/bin/env bash

set -euo pipefail

# Get database type from argument
DB_TYPE="${1:-}"

if [[ -z "$DB_TYPE" ]]; then
  echo "ERROR: Database type argument required (postgresql or mysql)" >&2
  echo "Usage: $0 [postgresql|mysql]" >&2
  exit 1
fi

if [[ "$DB_TYPE" != "postgresql" && "$DB_TYPE" != "mysql" ]]; then
  echo "ERROR: Invalid database type: $DB_TYPE" >&2
  echo "Must be 'postgresql' or 'mysql'" >&2
  exit 1
fi

echo "================================================================="
echo "RDST CLI Integration Tests - $DB_TYPE"
echo "================================================================="
echo ""

# Set up environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TEST_SCRIPT="${REPO_ROOT}/rdst/tests/integration/run_tests.sh"

# Verify test script exists
if [[ ! -f "$TEST_SCRIPT" ]]; then
  echo "ERROR: Test script not found at: $TEST_SCRIPT" >&2
  exit 1
fi

# Ensure script is executable
chmod +x "$TEST_SCRIPT"

# Determine API base URL based on environment
if [[ -z "${DUPLO_ENV:-}" ]] || [[ -z "${DUPLO_TENANT:-}" ]]; then
  echo "ERROR: DUPLO_ENV and DUPLO_TENANT must be set" >&2
  exit 1
fi

if [[ "${DUPLO_ENV}" == "dev" ]]; then
  if [[ "${DUPLO_TENANT}" == "dev01" ]]; then
    API_PREFIX="api-dev01.apps"
  elif [[ "${DUPLO_TENANT}" == "dev02" ]]; then
    API_PREFIX="api-dev02.apps"
  else
    API_PREFIX="api-${DUPLO_TENANT}.apps"
  fi
elif [[ "${DUPLO_ENV}" == "stage" ]]; then
  API_PREFIX="api-stage"
elif [[ "${DUPLO_ENV}" == "prod" ]]; then
  API_PREFIX="api"
else
  echo "ERROR: Unsupported environment: ${DUPLO_ENV}" >&2
  exit 1
fi

export API_BASE_URL="https://${API_PREFIX}.readyset.cloud"

# Obtain Supabase authentication token for admin API
echo "Obtaining authentication token..."

# Get Supabase project secrets
SUPABASE_PROJECT_SECRETS_NAME="supabase/${DUPLO_TENANT}"
SUPABASE_PROJECT_SECRETS=$(aws secretsmanager get-secret-value --secret-id ${SUPABASE_PROJECT_SECRETS_NAME} --cli-connect-timeout 1 | jq -r .SecretString)

SUPABASE_PROJECT_URL=$(echo ${SUPABASE_PROJECT_SECRETS} | jq -r '.SUPABASE_PROJECT_URL')
SUPABASE_PROJECT_API_KEY=$(echo ${SUPABASE_PROJECT_SECRETS} | jq -r '.SUPABASE_PROJECT_API_KEY')

# Get Supabase user credentials for authentication
SUPABASE_BUILDKITE_SECRETS_NAME="supabase-buildkite-creds/${DUPLO_TENANT}"
SUPABASE_BUILDKITE_SECRETS=$(aws secretsmanager get-secret-value --secret-id ${SUPABASE_BUILDKITE_SECRETS_NAME} --cli-connect-timeout 1 | jq -r .SecretString)

SUPABASE_USERNAME=$(echo ${SUPABASE_BUILDKITE_SECRETS} | jq -r '.username')
SUPABASE_PASSWORD=$(echo ${SUPABASE_BUILDKITE_SECRETS} | jq -r '.password')

# Obtain an access token from Supabase
TMP_CREDS=$(curl -s --location --request POST "${SUPABASE_PROJECT_URL}/auth/v1/token?grant_type=password" \
             --header "Content-Type: application/json" \
             --header "apikey: ${SUPABASE_PROJECT_API_KEY}" \
             --data-raw '{"email": "'${SUPABASE_USERNAME}'", "password": "'${SUPABASE_PASSWORD}'"}')

export ADMIN_API_TOKEN=$(echo ${TMP_CREDS} | jq -r '.access_token')

if [[ -z "$ADMIN_API_TOKEN" || "$ADMIN_API_TOKEN" == "null" ]]; then
  echo "ERROR: Failed to obtain authentication token" >&2
  echo "Response: $TMP_CREDS" >&2
  exit 1
fi

echo "✓ Authentication token obtained"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
cd "$REPO_ROOT/rdst"
if [[ -f "requirements.txt" ]]; then
  pip3 install --quiet --user -r requirements.txt 2>&1 | grep -v "WARNING: The script" || true
  echo "✓ Python dependencies installed"
fi

USER_SITE=$(python3 -c "import site; print(site.getusersitepackages())")
if [[ -n "$USER_SITE" ]]; then
  export PYTHONPATH="${USER_SITE}${PYTHONPATH:+:${PYTHONPATH}}"
fi

echo ""
echo "Configuration:"
echo "  Environment: ${DUPLO_ENV}"
echo "  Tenant: ${DUPLO_TENANT}"
echo "  Database Type: $DB_TYPE"
echo "  API Base URL: $API_BASE_URL"
echo ""

# Run the tests for the specified database type
exec "$TEST_SCRIPT" "$DB_TYPE"
