#!/bin/bash
###############################################################################
# (c) Copyright 2025 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
# Script to update lbapcommon version in LbAPI repository
# Usage: ./update_lbapi_version.sh <version>

set -e

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Error: Version argument required"
    echo "Usage: $0 <version>"
    exit 1
fi

# Define branch name
BRANCH_NAME="update-lbapcommon-${VERSION}"

# Clone LbAPI repository
echo "Cloning LbAPI repository..."
git clone "https://gitlab-ci-token:${LBAPI_UPDATE_TOKEN}@gitlab.cern.ch/lhcb-dpa/analysis-productions/LbAPI.git" lbapi-update
cd lbapi-update

# Configure git
git config user.email "noreply@cern.ch"
git config user.name "LbAPCommon GitLab CI"

# Create and checkout new branch
echo "Creating branch ${BRANCH_NAME}..."
git checkout -b "${BRANCH_NAME}"

# Update environment.yaml
echo "Updating environment.yaml..."
sed -i "s/lbapcommon >=.*/lbapcommon >=${VERSION}/" environment.yaml

# Update setup.cfg
echo "Updating setup.cfg..."
sed -i "s/LbAPCommon>=.*/LbAPCommon>=${VERSION}/" setup.cfg

# Check if there are changes
if git diff --quiet; then
    echo "No changes detected. Version might already be up to date."
    exit 0
fi

# Commit and push
echo "Committing changes..."
git add environment.yaml setup.cfg
git commit -m "chore: update lbapcommon to ${VERSION}"

echo "Pushing branch..."
git push -u origin "${BRANCH_NAME}"

# Create merge request using GitLab API
echo "Creating merge request..."
MR_RESPONSE=$(curl --silent --request POST \
  --header "PRIVATE-TOKEN: ${LBAPI_UPDATE_TOKEN}" \
  --header "Content-Type: application/json" \
  --data "{
    \"source_branch\": \"${BRANCH_NAME}\",
    \"target_branch\": \"main\",
    \"title\": \"chore: update lbapcommon to ${VERSION}\",
    \"description\": \"Automated update of lbapcommon dependency to version ${VERSION}.\\n\\nTriggered by lbapcommon release tag.\"
  }" \
  "https://gitlab.cern.ch/api/v4/projects/lhcb-dpa%2Fanalysis-productions%2FLbAPI/merge_requests")

# Extract MR URL from response
MR_URL=$(echo "$MR_RESPONSE" | grep -o '"web_url":"[^"]*' | cut -d'"' -f4)

if [ -n "$MR_URL" ]; then
    echo "Successfully created merge request: ${MR_URL}"
else
    echo "Warning: Merge request may have been created but URL could not be extracted."
    echo "Response: ${MR_RESPONSE}"
fi

echo "Successfully updated LbAPI to use lbapcommon ${VERSION}"
