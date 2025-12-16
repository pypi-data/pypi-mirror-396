#!/usr/bin/env bash
set -euo pipefail

# Ensure twine is installed (may run on different agent than build step)
python -m pip install --upgrade --quiet twine

# Deploy Python packages to AWS CodeArtifact (dev repository)
# This provides better version management and standard pip/uvx installation

# CodeArtifact configuration - adjust these as needed
CODEARTIFACT_DOMAIN="${CODEARTIFACT_DOMAIN:-readyset}"
CODEARTIFACT_REPOSITORY="${CODEARTIFACT_REPOSITORY:-rdst-dev}"
CODEARTIFACT_REGION="${CODEARTIFACT_REGION:-us-east-2}"
CODEARTIFACT_ACCOUNT="${CODEARTIFACT_ACCOUNT:-888984949675}"

echo "Publishing to AWS CodeArtifact..."
echo "  Domain: $CODEARTIFACT_DOMAIN"
echo "  Repository: $CODEARTIFACT_REPOSITORY"
echo "  Region: $CODEARTIFACT_REGION"
echo "  Account: $CODEARTIFACT_ACCOUNT"

# Verify AWS account
CURRENT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "unknown")
if [[ "$CURRENT_ACCOUNT" == "$CODEARTIFACT_ACCOUNT" ]]; then
  echo "✓ Using account $CODEARTIFACT_ACCOUNT"
elif [[ "$CURRENT_ACCOUNT" != "unknown" ]]; then
  echo "ℹ️  Cross-account deployment from $CURRENT_ACCOUNT to account $CODEARTIFACT_ACCOUNT"
else
  echo "⚠️  Could not determine current AWS account, proceeding anyway..."
fi

# Skip artifact download if running locally (artifacts only exist in Buildkite)
if command -v buildkite-agent &> /dev/null; then
  echo "Downloading build artifacts..."
  buildkite-agent artifact download "rdst/dist/*.whl" .
  buildkite-agent artifact download "rdst/dist/*.tar.gz" .
  DIST_PATH="rdst/dist"
else
  echo "Running locally - using existing dist/ folder"
  # Detect if we're in repo root or rdst/ directory
  if [[ -d "rdst/dist" ]]; then
    DIST_PATH="rdst/dist"
  elif [[ -d "dist" ]]; then
    DIST_PATH="dist"
  else
    echo "Error: Cannot find dist/ directory"
    exit 1
  fi
fi

# Get CodeArtifact authentication token (valid for 12 hours)
echo "Authenticating with CodeArtifact..."
CODEARTIFACT_TOKEN=$(aws codeartifact get-authorization-token \
  --domain "$CODEARTIFACT_DOMAIN" \
  --domain-owner "$CODEARTIFACT_ACCOUNT" \
  --region "$CODEARTIFACT_REGION" \
  --query authorizationToken \
  --output text)

# Get CodeArtifact repository endpoint
CODEARTIFACT_ENDPOINT=$(aws codeartifact get-repository-endpoint \
  --domain "$CODEARTIFACT_DOMAIN" \
  --domain-owner "$CODEARTIFACT_ACCOUNT" \
  --repository "$CODEARTIFACT_REPOSITORY" \
  --region "$CODEARTIFACT_REGION" \
  --format pypi \
  --query repositoryEndpoint \
  --output text)

echo "✓ Authenticated with CodeArtifact"
echo "  Endpoint: $CODEARTIFACT_ENDPOINT"

# Publish to CodeArtifact using twine
echo "Publishing packages to CodeArtifact..."
python -m twine upload \
  --repository-url "$CODEARTIFACT_ENDPOINT" \
  --username aws \
  --password "$CODEARTIFACT_TOKEN" \
  "$DIST_PATH"/*.whl \
  "$DIST_PATH"/*.tar.gz

echo ""
echo "✓ Dev deployment complete!"
echo ""
echo "Users can install with:"
echo "  # Configure pip to use CodeArtifact (one-time setup):"
echo "  aws codeartifact login --tool pip \\"
echo "    --domain $CODEARTIFACT_DOMAIN \\"
echo "    --domain-owner $CODEARTIFACT_ACCOUNT \\"
echo "    --repository $CODEARTIFACT_REPOSITORY \\"
echo "    --region $CODEARTIFACT_REGION"
echo ""
echo "  # Then install/upgrade rdst:"
echo "  pip install rdst"
echo "  pipx install rdst"
echo "  uvx rdst"
echo ""
