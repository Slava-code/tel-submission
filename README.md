# YouTube AI Productivity Extension

<img width="1440" height="855" alt="Lock-In! Youtube Extension screenshot" src="https://github.com/user-attachments/assets/4d4eebb1-238d-4a6b-ac6d-922bcd276188" />

A Chrome extension that uses AI to filter YouTube videos based on your productivity preferences, helping you stay focused by intelligently hiding distracting content.

## Features

- **AI-Powered Filtering**: Uses Google's Gemini AI to analyze video titles and filter content based on your preferences
- **Smart Loading Screen**: Shows a loading screen while AI processes videos on first load
- **Visual Feedback**: Blurs filtered videos with clear "Filtered by AI" labels
- **Hover to Preview**: Hover over filtered videos to partially reveal them
- **Real-time Processing**: Filters new videos as you scroll
- **Preference Tracking**: Remembers your filtering preferences across sessions

## Prerequisites

Before you can use this extension, you need:

1. **Google Cloud Platform Account**: With billing enabled
2. **Chrome Browser**: For installing the extension
3. **Node.js**: Version 16 or higher
4. **Python**: Version 3.8 or higher (for the backend)
5. **Google Cloud SDK**: For deployment

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/youtube-productivity-extension.git
cd youtube-productivity-extension
```

### 2. Set Up Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Cloud Functions API
   - AI Platform API
   - Firestore API
   - Cloud Build API

### 3. Get Your API Keys

#### Option A: Using Gemini API (Recommended)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key for Gemini
3. Save this key for configuration

#### Option B: Using Vertex AI
1. Create a service account in Google Cloud Console
2. Download the service account key JSON file
3. Grant necessary permissions (AI Platform User, etc.)

### 4. Configure the Extension

#### Frontend Configuration
```bash
# Copy the example config file
cp src/config.example.ts src/config.ts

# Edit src/config.ts with your actual values
```

Edit `src/config.ts`:
```typescript
export const config = {
  PROJECT_ID: 'your-actual-gcp-project-id',
  REGION: 'us-central1',
  FILTER_VIDEO_URL: 'https://us-central1-your-actual-gcp-project-id.cloudfunctions.net/filter_video',
  FIRESTORE_CHAT_COLLECTION: 'chats',
  DEBUG_MODE: false,
  LOG_FILTERING_DECISIONS: false
};
```

#### Backend Configuration
```bash
# Copy the example config file
cp backend/config.example.py backend/config.py

# Set environment variables (recommended)
export PROJECT_ID="your-actual-gcp-project-id"
export GEMINI_API_KEY="your-gemini-api-key"
export VERTEX_AI_MODEL="gemini-1.5-flash"
```

### 5. Deploy the Backend

#### Option A: Using Personal Account
```bash
# Make sure you're logged into gcloud
gcloud auth login
gcloud config set project your-actual-gcp-project-id

# Deploy the function
./deploy-personal.sh
```

#### Option B: Using Service Account
```bash
# Update deploy.sh with your service account path
# Then run:
./deploy.sh
```

### 6. Build the Extension

```bash
# Install dependencies
npm install

# Build the extension
npm run build
```

### 7. Install the Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right toggle)
3. Click "Load unpacked"
4. Select the `dist` folder from this project
5. The extension should now appear in your extensions list

### 8. Configure Your Preferences

1. Click on the extension icon in Chrome
2. Enter your productivity preferences (e.g., "I want to focus on programming tutorials and avoid gaming content")
3. Go to YouTube and watch the AI filter videos in real-time!

## Usage

### Setting Preferences

The extension works by analyzing your natural language preferences. Examples:

- **Focus-based**: "I want to focus on educational content and programming tutorials"
- **Avoidance-based**: "I hate gaming videos and reaction content"
- **Specific topics**: "I love science documentaries but avoid entertainment news"
- **Productivity-focused**: "Help me avoid time-wasting content and focus on skill development"

### How It Works

1. **Page Load**: Shows loading screen while processing initial videos
2. **AI Analysis**: Sends video titles to your deployed AI function
3. **Smart Filtering**: AI decides whether to keep or filter each video
4. **Visual Feedback**: Filtered videos are blurred with clear labels
5. **Continuous Processing**: New videos are filtered as you scroll

### Customization

You can modify the filtering behavior by:

- Editing the AI prompt in `backend/main.py`
- Adjusting the blur effects in `src/youtube-filter.ts`
- Changing the loading screen appearance
- Modifying the filtering logic

## Development

### Running Locally

```bash
# Start the development server
npm run dev

# For backend testing
cd backend
python test_gemini_local.py
```

### Testing the Backend

```bash
# Test your deployed function
curl -X POST https://us-central1-your-project-id.cloudfunctions.net/filter_video \
  -H "Content-Type: application/json" \
  -d '{"title": "How to code Python", "preferences": "I love programming tutorials"}'
```

## Troubleshooting

### Common Issues

1. **Extension not filtering**: Check that your backend function is deployed and accessible
2. **API errors**: Verify your API keys and project configuration
3. **Loading screen stuck**: Check browser console for error messages
4. **Videos not blurring**: Ensure the extension has proper permissions

### Debug Mode

Enable debug mode by setting `DEBUG_MODE: true` in your config files to see detailed logs.

### Checking Logs

```bash
# View Cloud Function logs
gcloud functions logs read filter_video --limit 50
```

## Architecture

- **Frontend**: React + TypeScript Chrome extension
- **Backend**: Python Cloud Function using Google AI
- **AI Service**: Gemini AI for content analysis
- **Storage**: Chrome local storage for preferences

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Security

- Never commit your actual API keys or service account files
- Use environment variables for sensitive configuration
- The example files are safe templates - only edit the actual config files

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the configuration files
3. Check browser console for errors
4. Verify your Google Cloud setup

## Acknowledgments

- Google Gemini AI for content analysis
- Chrome Extensions API
- React and TypeScript communities
