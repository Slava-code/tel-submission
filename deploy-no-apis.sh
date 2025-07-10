#!/bin/bash

# YouTube AI Productivity Extension - Deployment Script (No API Enabling)
# This script deploys the Cloud Function without enabling APIs

set -e  # Exit on any error

echo "🚀 Starting deployment of YouTube AI Productivity Extension..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVICE_ACCOUNT_KEY="path/to/your/service-account-key.json"
PROJECT_ID="your-gcp-project-id"
REGION="us-central1"
FUNCTION_NAME="filter_video"

# Check if service account key exists
if [ ! -f "$SERVICE_ACCOUNT_KEY" ]; then
    echo -e "${RED}❌ Service account key not found at: $SERVICE_ACCOUNT_KEY${NC}"
    exit 1
fi

echo -e "${YELLOW}🔐 Setting up authentication...${NC}"

# Set up authentication
export GOOGLE_APPLICATION_CREDENTIALS="$SERVICE_ACCOUNT_KEY"
gcloud auth activate-service-account --key-file="$SERVICE_ACCOUNT_KEY"
gcloud config set project $PROJECT_ID

echo -e "${YELLOW}⚠️  Skipping API enabling (enable manually in console)${NC}"

echo -e "${YELLOW}🔧 Deploying Cloud Function...${NC}"

# Change to backend directory
cd backend

# Deploy the function
gcloud functions deploy $FUNCTION_NAME \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point $FUNCTION_NAME \
  --source . \
  --region $REGION

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