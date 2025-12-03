#!/bin/bash
# Helper script to set AWS credentials for Terraform
# Usage: source use-credentials.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CREDENTIALS_FILE="$SCRIPT_DIR/../.aws-credentials"

if [ -f "$CREDENTIALS_FILE" ]; then
  export AWS_SHARED_CREDENTIALS_FILE="$CREDENTIALS_FILE"
  echo "✓ AWS credentials loaded from: $CREDENTIALS_FILE"
else
  echo "✗ Credentials file not found: $CREDENTIALS_FILE"
  echo "  Please create it with your AWS credentials"
  return 1
fi


