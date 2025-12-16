#!/usr/bin/env bash
set -euo pipefail

# Ensure twine is installed (may run on different agent than build step)
python -m pip install --upgrade --quiet twine

# Deploy Python packages to AWS CodeArtifact AND public PyPI
# This hybrid approach provides:
# - CodeArtifact: Private repository access for internal teams
# - PyPI: Public access for anyone (pipx install rdst, uvx rdst)

# CodeArtifact configuration - adjust these as needed
CODEARTIFACT_DOMAIN="${CODEARTIFACT_DOMAIN:-readyset}"
CODEARTIFACT_REPOSITORY="${CODEARTIFACT_REPOSITORY:-rdst}"
CODEARTIFACT_REGION="${CODEARTIFACT_REGION:-us-east-2}"
CODEARTIFACT_ACCOUNT="${CODEARTIFACT_ACCOUNT:-888984949675}"

# PyPI configuration
PUBLISH_TO_PYPI="${PUBLISH_TO_PYPI:-true}"  # Set to false to skip PyPI publishing

echo "Publishing to AWS CodeArtifact (RELEASE)..."
echo "  Domain: $CODEARTIFACT_DOMAIN"
echo "  Repository: $CODEARTIFACT_REPOSITORY (PRODUCTION)"
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
    echo "Please run .buildkite/build_package.sh first to create build artifacts"
    exit 1
  fi
fi

# Get package version from wheel filename
WHEEL_FILE=$(ls "$DIST_PATH"/*.whl | head -1)
WHEEL_BASENAME=$(basename "$WHEEL_FILE")
# Extract version using semantic versioning pattern (e.g., rdst-0.1.123-py3-none-any.whl)
VERSION=$(echo "$WHEEL_BASENAME" | grep -oP '(?<=rdst-)[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")

echo ""
echo "📦 Publishing RDST version: $VERSION"
echo ""
echo "ℹ️  This version will be published to BOTH:"
echo "   • CodeArtifact (rdst repository)"
echo "   • PyPI (public)"
echo "   Using the same build artifacts to ensure version consistency."
echo ""

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
echo "Publishing packages to CodeArtifact (PRODUCTION)..."
python -m twine upload \
  --repository-url "$CODEARTIFACT_ENDPOINT" \
  --username aws \
  --password "$CODEARTIFACT_TOKEN" \
  "$DIST_PATH"/*.whl \
  "$DIST_PATH"/*.tar.gz

echo ""
echo "✓ Published to CodeArtifact successfully!"
echo ""

# ============================================================================
# Publish to public PyPI
# ============================================================================

if [[ "$PUBLISH_TO_PYPI" != "true" ]]; then
    echo ""
    echo "⚠️  Skipping PyPI publication (PUBLISH_TO_PYPI=$PUBLISH_TO_PYPI)"
    echo ""
    exit 0
fi

echo ""
echo "========================================="
echo "Publishing to PyPI (public)"
echo "========================================="
echo ""

# Get PyPI token from environment or AWS Secrets Manager
# NOTE: Secret buildkite/rdst/pypi-token is stored as JSON: {"PYPI_TOKEN": "pypi-..."}
if [[ -n "${PYPI_TOKEN:-}" ]]; then
    echo "✓ Using PYPI_TOKEN from environment"
elif command -v aws &> /dev/null; then
    echo "Fetching PyPI token from AWS Secrets Manager..."
    echo "  Secret: buildkite/rdst/pypi-token (account 305232526136, region us-east-2)"

    # Fetch the secret JSON
    SECRET_JSON=$(aws secretsmanager get-secret-value \
        --secret-id buildkite/rdst/pypi-token \
        --region us-east-2 \
        --query SecretString \
        --output text 2>/dev/null)

    if [[ -n "$SECRET_JSON" ]]; then
        # Extract PYPI_TOKEN from JSON key-value pair
        PYPI_TOKEN=$(echo "$SECRET_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin).get('PYPI_TOKEN', ''))" 2>/dev/null)

        if [[ -n "$PYPI_TOKEN" ]]; then
            echo "✓ Retrieved PYPI_TOKEN from AWS Secrets Manager"
            export PYPI_TOKEN
        else
            echo "❌ ERROR: Secret found but PYPI_TOKEN key is missing or empty in JSON"
            echo "Secret should be stored as: {\"PYPI_TOKEN\": \"pypi-...\"}"
            exit 1
        fi
    else
        echo ""
        echo "❌ ERROR: Could not retrieve PYPI_TOKEN"
        echo ""
        echo "PyPI token not found in environment or AWS Secrets Manager."
        echo ""
        echo "To fix this, either:"
        echo "  1. Set PYPI_TOKEN environment variable in Buildkite"
        echo "  2. Store token in AWS Secrets Manager (account 305232526136):"
        echo "     aws secretsmanager create-secret \\"
        echo "       --name buildkite/rdst/pypi-token \\"
        echo "       --secret-string '{\"PYPI_TOKEN\":\"pypi-...\"}' \\"
        echo "       --region us-east-2"
        echo ""
        echo "See PYPI_SETUP.md for detailed instructions."
        echo ""
        exit 1
    fi
else
    echo ""
    echo "❌ ERROR: PYPI_TOKEN not set and AWS CLI not available"
    echo ""
    echo "Set PYPI_TOKEN environment variable or install AWS CLI."
    echo "See PYPI_SETUP.md for setup instructions."
    echo ""
    exit 1
fi

# Verify token format
if [[ ! "$PYPI_TOKEN" =~ ^pypi- ]]; then
    echo ""
    echo "⚠️  WARNING: PYPI_TOKEN doesn't start with 'pypi-'"
    echo "This might not be a valid PyPI token."
    echo ""
fi

# Publish to PyPI using twine
echo "Publishing rdst version $VERSION to PyPI..."
echo ""

python -m twine upload \
    --repository pypi \
    --username __token__ \
    --password "$PYPI_TOKEN" \
    --non-interactive \
    --skip-existing \
    --verbose \
    "$DIST_PATH"/*.whl \
    "$DIST_PATH"/*.tar.gz

PYPI_EXIT_CODE=$?

if [[ $PYPI_EXIT_CODE -eq 0 ]]; then
    echo ""
    echo "========================================="
    echo "✓ Published to PyPI successfully!"
    echo "========================================="
    echo ""
    echo "📦 Package: rdst version $VERSION"
    echo ""
    echo "✅ Version Consistency Check:"
    echo "   • CodeArtifact (rdst): $VERSION"
    echo "   • PyPI (public):       $VERSION"
    echo "   → Same version published to both locations ✓"
    echo ""
    echo "🌍 Public Access (PyPI):"
    echo "  PyPI page: https://pypi.org/project/rdst/$VERSION/"
    echo "  Install: pipx install rdst"
    echo "  Run: uvx rdst"
    echo "  Upgrade: pipx upgrade rdst"
    echo ""
    echo "🔒 Internal Access (CodeArtifact):"
    echo "  aws codeartifact login --tool pip \\"
    echo "    --domain $CODEARTIFACT_DOMAIN \\"
    echo "    --domain-owner $CODEARTIFACT_ACCOUNT \\"
    echo "    --repository $CODEARTIFACT_REPOSITORY \\"
    echo "    --region $CODEARTIFACT_REGION"
    echo "  pip install rdst==$VERSION"
    echo ""
else
    echo ""
    echo "========================================="
    echo "⚠️  PyPI publication failed!"
    echo "========================================="
    echo ""
    echo "Exit code: $PYPI_EXIT_CODE"
    echo ""
    echo "Common issues:"
    echo "  - Version $VERSION already exists on PyPI (cannot overwrite)"
    echo "  - Invalid PYPI_TOKEN"
    echo "  - Network connectivity issues"
    echo "  - Package metadata issues"
    echo ""
    echo "The package was successfully published to CodeArtifact."
    echo "Users with AWS credentials can still access it."
    echo ""
    echo "To retry PyPI publication:"
    echo "  1. Fix the issue (see error above)"
    echo "  2. Increment version in _version.py if version conflict"
    echo "  3. Re-run this script or trigger a new build"
    echo ""
    exit 1
fi
