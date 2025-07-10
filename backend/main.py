import json
import functions_framework
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel
import vertexai
import requests
import os
from config import config
from google.cloud import storage
from google import genai
from google.genai import types
import google.generativeai as genai_api

def search_for_context(query, max_results=3):
    """
    Search for additional context about a video title using a search API.
    Returns relevant information to help with categorization.
    """
    try:
        # Using DuckDuckGo Instant Answer API as a free option
        search_url = f"https://api.duckduckgo.com/?q={requests.utils.quote(query)}&format=json&no_redirect=1"
        
        response = requests.get(search_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant information
            context_info = []
            
            # Add abstract if available
            if data.get('Abstract'):
                context_info.append(f"Description: {data['Abstract']}")
            
            # Add definition if available
            if data.get('Definition'):
                context_info.append(f"Definition: {data['Definition']}")
            
            # Add related topics
            if data.get('RelatedTopics'):
                topics = [topic.get('Text', '') for topic in data['RelatedTopics'][:2] if topic.get('Text')]
                if topics:
                    context_info.append(f"Related: {'; '.join(topics)}")
            
            return ' | '.join(context_info) if context_info else None
            
    except Exception as e:
        print(f"Search error: {str(e)}")
        return None
    
    return None

@functions_framework.http
def filter_video(request):
    """
    HTTP Cloud Function for filtering YouTube videos based on user preferences.
    """
    # Handle CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    # Set CORS headers for actual request
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    try:
        print(f"Function called with method: {request.method}")
        
        # Parse request JSON
        request_json = request.get_json(silent=True)
        print(f"Request JSON: {request_json}")
        
        if not request_json:
            print("ERROR: No JSON body provided")
            return json.dumps({'error': 'No JSON body provided', 'decision': 'keep'}), 400, headers

        title = request_json.get('title', '')
        preferences = request_json.get('preferences', '')
        print(f"Title: {title}, Preferences: {preferences}")

        if not title or not preferences:
            print("ERROR: Missing title or preferences")
            return json.dumps({'error': 'Title and preferences are required', 'decision': 'keep'}), 400, headers

        print(f"Using Gemini API for intelligent filtering")
        print(f"Model: {config.GEMINI_MODEL}")
        
        try:
            # Configure Gemini API
            genai_api.configure(api_key=config.GEMINI_API_KEY)
            
            # Initialize the model
            model = genai_api.GenerativeModel(config.GEMINI_MODEL)

            # User-centric prompt focused on productivity
            prompt = f"""You are filtering YouTube videos to help a user stay productive.

User says: "{preferences}"
Video title: "{title}"

Should this video be REMOVED (filtered out) or KEPT for this user?

Rules:
- If user says they "hate" or "avoid" something and the video is clearly about that topic, respond "remove"
- If user says they "love" or "want" something and the video is about that topic, respond "keep"  
- If video matches what user wants to avoid, respond "remove"
- If video supports what user wants to focus on, respond "keep"
- When uncertain, respond "keep" to avoid over-filtering

Examples:
- User: "I hate gaming videos" + Video: "Hitman gameplay" → "remove"
- User: "I love programming" + Video: "Python tutorial" → "keep"

Respond with exactly one word: "keep" or "remove"
"""

            print(f"Sending prompt to {config.GEMINI_MODEL}...")
            
            # Generate response using the Gemini API
            response = model.generate_content(prompt)
            ai_response = response.text.strip().lower()
            
            print(f"{config.GEMINI_MODEL} raw response: '{ai_response}'")
            
            # Parse the response
            if 'remove' in ai_response:
                decision = 'remove'
            else:
                decision = 'keep'
                
            print(f"AI filtering decision: {decision}")
            
        except Exception as ai_error:
            print(f"Gemini API error: {str(ai_error)}")
            print("AI processing failed - defaulting to keep video to avoid false positives")
            
            # If AI completely fails, default to keeping the video
            decision = 'keep'
            print(f"Error fallback decision: {decision}")
        
        print(f"Final decision: {decision}")
        
        return json.dumps({'decision': decision}), 200, headers

    except ImportError as e:
        error_msg = f"Import error: {str(e)}"
        print(f"ERROR: {error_msg}")
        return json.dumps({'error': error_msg, 'decision': 'keep'}), 500, headers
    except Exception as e:
        error_msg = f"Error processing video filter request: {str(e)}"
        print(f"ERROR: {error_msg}")
        return json.dumps({'error': error_msg, 'decision': 'keep'}), 500, headers


@functions_framework.cloud_event
def chat_reply(cloud_event):
    """
    Cloud Function triggered by Firestore document creation for chat replies.
    """
    try:
        # Extract event data
        data = cloud_event.data
        
        # Check if this is a user message
        if data.get('sender') != 'user':
            return
        
        message_text = data.get('text', '')
        if not message_text:
            return

        # Initialize Vertex AI
        vertexai.init(project=config.PROJECT_ID, location=config.REGION)
        
        # Initialize the Gemini model
        model = GenerativeModel(config.VERTEX_AI_MODEL)

        # Create conversational prompt
        prompt = f"""
You are a helpful AI assistant having a conversation about YouTube videos. 
Respond to the user's message in a conversational and helpful way.

User message: {message_text}
"""

        # Generate response
        response = model.generate_content(prompt)
        
        if response.text:
            # Import Firestore here to avoid issues if not available
            from google.cloud import firestore
            
            # Initialize Firestore client
            db = firestore.Client()
            
            # Extract chat ID from the event path
            # Path format: chats/{chatId}/messages/{messageId}
            path_parts = cloud_event.data.get('path', '').split('/')
            if len(path_parts) >= 2:
                chat_id = path_parts[1]
                
                # Add AI response to the chat
                chat_ref = db.collection(config.FIRESTORE_CHAT_COLLECTION).document(chat_id).collection('messages')
                chat_ref.add({
                    'text': response.text,
                    'sender': 'ai',
                    'timestamp': firestore.SERVER_TIMESTAMP
                })

    except Exception as e:
        if config.DEBUG_MODE:
            print(f"Error in chat_reply function: {str(e)}")
        return


@functions_framework.http
def test_gcp_services(request):
    """
    Test endpoint to check if Google Cloud services work.
    """
    # Handle CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    results = {}
    
    try:
        # Test 1: Check project info
        results['project_id'] = config.PROJECT_ID
        results['region'] = config.REGION
        
        # Test 2: Try to list Cloud Storage buckets (basic GCP service)
        try:
            storage_client = storage.Client()
            buckets = list(storage_client.list_buckets())
            results['storage_access'] = f"SUCCESS - Found {len(buckets)} buckets"
        except Exception as e:
            results['storage_access'] = f"FAILED - {str(e)}"
        
        # Test 3: Try to initialize Vertex AI
        try:
            vertexai.init(project=config.PROJECT_ID, location=config.REGION)
            results['vertex_ai_init'] = "SUCCESS - Vertex AI initialized"
        except Exception as e:
            results['vertex_ai_init'] = f"FAILED - {str(e)}"
        
        # Test 4: Try to create a model instance
        try:
            model = GenerativeModel(config.VERTEX_AI_MODEL)
            results['vertex_ai_model'] = f"SUCCESS - Model {config.VERTEX_AI_MODEL} created"
        except Exception as e:
            results['vertex_ai_model'] = f"FAILED - {str(e)}"
        
        # Test 5: Try to make a simple AI request
        try:
            vertexai.init(project=config.PROJECT_ID, location=config.REGION)
            model = GenerativeModel(config.VERTEX_AI_MODEL)
            response = model.generate_content("Say hello")
            results['vertex_ai_request'] = f"SUCCESS - Response: {response.text[:50]}..."
        except Exception as e:
            results['vertex_ai_request'] = f"FAILED - {str(e)}"
            
        return json.dumps(results, indent=2), 200, headers
        
    except Exception as e:
        results['error'] = f"General error: {str(e)}"
        return json.dumps(results, indent=2), 500, headers


@functions_framework.http
def test_gemini_api(request):
    """
    Test the Gemini API directly.
    """
    # Handle CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    results = {}
    
    try:
        # Test 1: Configure API
        try:
            genai_api.configure(api_key=config.GEMINI_API_KEY)
            results['api_config'] = "SUCCESS - API configured"
        except Exception as e:
            results['api_config'] = f"FAILED - {str(e)}"
            return json.dumps(results, indent=2), 500, headers
        
        # Test 2: Initialize model
        try:
            model = genai_api.GenerativeModel(config.GEMINI_MODEL)
            results['model_init'] = f"SUCCESS - Model {config.GEMINI_MODEL} initialized"
        except Exception as e:
            results['model_init'] = f"FAILED - {str(e)}"
            return json.dumps(results, indent=2), 500, headers
        
        # Test 3: Simple prompt
        try:
            response = model.generate_content("Say hello!")
            results['simple_test'] = f"SUCCESS - Response: {response.text[:100]}..."
        except Exception as e:
            results['simple_test'] = f"FAILED - {str(e)}"
        
        # Test 4: Video filtering test
        try:
            prompt = '''You are filtering YouTube videos to help a user stay productive.

User says: "I hate gaming videos"
Video title: "Hitman 3 Speedrun World Record"

Should this video be REMOVED (filtered out) or KEPT for this user?

Respond with exactly one word: "keep" or "remove"
'''
            response = model.generate_content(prompt)
            results['filtering_test'] = f"SUCCESS - Response: {response.text[:50]}..."
        except Exception as e:
            results['filtering_test'] = f"FAILED - {str(e)}"
            
        return json.dumps(results, indent=2), 200, headers
        
    except Exception as e:
        results['error'] = f"General error: {str(e)}"
        return json.dumps(results, indent=2), 500, headers


@functions_framework.http
def test_new_genai_sdk(request):
    """
    Test the new Google GenAI SDK with Vertex AI.
    """
    # Handle CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    results = {}
    
    try:
        # Test 1: Initialize new GenAI client with Vertex AI
        try:
            client = genai.Client(
                vertexai=True, 
                project=config.PROJECT_ID, 
                location=config.REGION
            )
            results['genai_client_init'] = "SUCCESS - GenAI client initialized"
        except Exception as e:
            results['genai_client_init'] = f"FAILED - {str(e)}"
            return json.dumps(results, indent=2), 500, headers
        
        # Test 2: Try Gemini 1.5 Flash
        try:
            model = "gemini-1.5-flash-002"
            response = client.models.generate_content(
                model=model,
                contents=["Say hello and confirm you're working!"]
            )
            results['gemini_1_5_flash'] = f"SUCCESS - Response: {response.text[:100]}..."
        except Exception as e:
            results['gemini_1_5_flash'] = f"FAILED - {str(e)}"
        
        # Test 3: Try Gemini 1.5 Pro
        try:
            model = "gemini-1.5-pro-002"
            response = client.models.generate_content(
                model=model,
                contents=["What's 2+2?"]
            )
            results['gemini_1_5_pro'] = f"SUCCESS - Response: {response.text[:100]}..."
        except Exception as e:
            results['gemini_1_5_pro'] = f"FAILED - {str(e)}"
        
        # Test 4: Try chat-bison
        try:
            model = "publishers/google/models/chat-bison"
            response = client.models.generate_content(
                model=model,
                contents=["Test message"]
            )
            results['chat_bison_test'] = f"SUCCESS - Response: {response.text[:100]}..."
        except Exception as e:
            results['chat_bison_test'] = f"FAILED - {str(e)}"
        
        # Test 5: Try to list available models
        try:
            models = client.models.list()
            model_names = [model.name for model in models]
            results['available_models'] = f"SUCCESS - Found {len(model_names)} models: {model_names[:5]}"
        except Exception as e:
            results['available_models'] = f"FAILED - {str(e)}"
            
        return json.dumps(results, indent=2), 200, headers
        
    except Exception as e:
        results['error'] = f"General error: {str(e)}"
        return json.dumps(results, indent=2), 500, headers


@functions_framework.http
def test_gemini_api(request):
    """
    Test the Gemini API directly.
    """
    # Handle CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    results = {}
    
    try:
        # Test 1: Configure API
        try:
            genai_api.configure(api_key=config.GEMINI_API_KEY)
            results['api_config'] = "SUCCESS - API configured"
        except Exception as e:
            results['api_config'] = f"FAILED - {str(e)}"
            return json.dumps(results, indent=2), 500, headers
        
        # Test 2: Initialize model
        try:
            model = genai_api.GenerativeModel(config.GEMINI_MODEL)
            results['model_init'] = f"SUCCESS - Model {config.GEMINI_MODEL} initialized"
        except Exception as e:
            results['model_init'] = f"FAILED - {str(e)}"
            return json.dumps(results, indent=2), 500, headers
        
        # Test 3: Simple prompt
        try:
            response = model.generate_content("Say hello!")
            results['simple_test'] = f"SUCCESS - Response: {response.text[:100]}..."
        except Exception as e:
            results['simple_test'] = f"FAILED - {str(e)}"
        
        # Test 4: Video filtering test
        try:
            prompt = '''You are filtering YouTube videos to help a user stay productive.

User says: "I hate gaming videos"
Video title: "Hitman 3 Speedrun World Record"

Should this video be REMOVED (filtered out) or KEPT for this user?

Respond with exactly one word: "keep" or "remove"
'''
            response = model.generate_content(prompt)
            results['filtering_test'] = f"SUCCESS - Response: {response.text[:50]}..."
        except Exception as e:
            results['filtering_test'] = f"FAILED - {str(e)}"
            
        return json.dumps(results, indent=2), 200, headers
        
    except Exception as e:
        results['error'] = f"General error: {str(e)}"
        return json.dumps(results, indent=2), 500, headers