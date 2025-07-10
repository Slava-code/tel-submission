#!/bin/bash

# YouTube AI Productivity Extension - Personal Account Deployment
# This script deploys using your personal Google account

set -e  # Exit on any error

echo "🚀 Starting deployment with personal account..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="your-gcp-project-id"
REGION="us-central1"
FUNCTION_NAME="filter_video"

echo -e "${YELLOW}🔐 Using personal account authentication...${NC}"

# Set the project (assuming you're already logged in)
gcloud config set project $PROJECT_ID

echo -e "${YELLOW}🔧 Deploying Cloud Function...${NC}"

# Change to backend directory
cd backend

# Deploy the function with more memory
gcloud functions deploy $FUNCTION_NAME \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point $FUNCTION_NAME \
  --source . \
  --region $REGION \
  --memory 512MB \
  --timeout 60s

echo -e "${GREEN}✅ Deployment complete!${NC}"

# Get the function URL
FUNCTION_URL="https://$REGION-$PROJECT_ID.cloudfunctions.net/$FUNCTION_NAME"
echo -e "${GREEN}🌐 Function URL: $FUNCTION_URL${NC}"

echo -e "${YELLOW}🧪 Testing the function...${NC}"

# Test the function
curl -X POST $FUNCTION_URL \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Video about AI", "preferences": "I like technology and AI content"}' \
  -s | python3 -m json.tool

echo -e "${GREEN}🎉 Deployment and testing complete!${NC}"
echo -e "${GREEN}Your function is ready at: $FUNCTION_URL${NC}"