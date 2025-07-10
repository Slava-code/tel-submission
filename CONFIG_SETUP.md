# Configuration Setup

This document explains how to set up the configuration files for the YouTube AI Productivity Extension.

## Frontend Configuration

### 1. Create the config file

Copy the example config file and customize it for your project:

```bash
cp src/config.example.ts src/config.ts
```

### 2. Update the config values

Edit `src/config.ts` with your actual values:

```typescript
export const config = {
  // Replace with your actual Google Cloud project ID
  PROJECT_ID: 'your-actual-project-id',
  
  // Replace with your preferred region
  REGION: 'us-central1',
  
  // Replace with your actual Cloud Function URL
  FILTER_VIDEO_URL: 'https://us-central1-your-actual-project-id.cloudfunctions.net/filter_video',
  
  // Firestore collection name for chats
  FIRESTORE_CHAT_COLLECTION: 'chats',
  
  // Debug settings
  DEBUG_MODE: false,
  LOG_FILTERING_DECISIONS: false
};
```

## Backend Configuration

### 1. Create the config file

Copy the example config file and customize it for your project:

```bash
cp backend/config.example.py backend/config.py
```

### 2. Set environment variables

You can set these environment variables in your deployment environment:

```bash
export PROJECT_ID="your-actual-project-id"
export REGION="us-central1"
export VERTEX_AI_MODEL="gemini-1.0-pro"
export FIRESTORE_CHAT_COLLECTION="chats"
export DEBUG_MODE="false"
export LOG_AI_RESPONSES="false"
```

### 3. For local development

Create a `.env` file in the backend directory:

```
PROJECT_ID=your-actual-project-id
REGION=us-central1
VERTEX_AI_MODEL=gemini-1.0-pro
FIRESTORE_CHAT_COLLECTION=chats
DEBUG_MODE=true
LOG_AI_RESPONSES=true
```

## Important Notes

- **Never commit the actual config files** (`src/config.ts` and `backend/config.py`) to version control
- The config files are already added to `.gitignore`
- Always use the example files as templates
- Make sure to update the Cloud Function URL after deploying your backend
- Set appropriate debug flags for your environment (false for production)

## Deployment

### Prerequisites
1. **Service Account Key**: Located at `path/to/your/service-account-key.json`
2. **Google Cloud SDK**: Install from https://cloud.google.com/sdk/docs/install

### Step 1: Set up Authentication
```bash
# Set the service account key
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"

# Authenticate with gcloud
gcloud auth activate-service-account --key-file="path/to/your/service-account-key.json"
gcloud config set project your-gcp-project-id
```

### Step 2: Enable Required APIs
```bash
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 3: Deploy the Cloud Function
```bash
cd backend

gcloud functions deploy filter_video \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point filter_video \
  --source . \
  --region us-central1
```

### Step 4: Test the Deployment
```bash
curl -X POST https://us-central1-your-gcp-project-id.cloudfunctions.net/filter_video \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Video about AI", "preferences": "I like technology and AI content"}'
```

### Expected Function URL
Your function will be available at:
```
https://us-central1-your-gcp-project-id.cloudfunctions.net/filter_video
```

### Security Note
- Service account key is added to .gitignore
- Set proper file permissions: `chmod 600 path/to/your/service-account-key.json`