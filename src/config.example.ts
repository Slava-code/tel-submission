export const config = {
  // Google Cloud Project Configuration
  PROJECT_ID: 'your-actual-project-id',
  REGION: 'us-central1', // or your preferred region
  
  // Cloud Functions URLs
  FILTER_VIDEO_URL: 'https://us-central1-your-actual-project-id.cloudfunctions.net/filter_video',
  
  // Firestore Configuration
  FIRESTORE_CHAT_COLLECTION: 'chats',
  
  // Development/Debug settings
  DEBUG_MODE: false,
  LOG_FILTERING_DECISIONS: false
};

export type Config = typeof config;