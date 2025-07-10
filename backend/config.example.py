import os

class Config:
    # Google Cloud Project Configuration
    PROJECT_ID = os.environ.get('PROJECT_ID', 'your-actual-project-id')
    REGION = os.environ.get('REGION', 'us-central1')
    
    # Vertex AI Configuration
    VERTEX_AI_MODEL = os.environ.get('VERTEX_AI_MODEL', 'gemini-1.0-pro')
    
    # Firestore Configuration
    FIRESTORE_CHAT_COLLECTION = os.environ.get('FIRESTORE_CHAT_COLLECTION', 'chats')
    
    # Development/Debug settings
    DEBUG_MODE = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
    LOG_AI_RESPONSES = os.environ.get('LOG_AI_RESPONSES', 'false').lower() == 'true'

config = Config()