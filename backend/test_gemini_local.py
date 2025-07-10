#!/usr/bin/env python3

import google.generativeai as genai

# Configure the API
api_key = "your-gemini-api-key"
genai.configure(api_key=api_key)

# Test the model
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Simple test
    print("Testing Gemini API...")
    response = model.generate_content("Say hello!")
    print(f"Response: {response.text}")
    
    # Video filtering test
    print("\nTesting video filtering...")
    prompt = '''You are filtering YouTube videos to help a user stay productive.

User says: "I hate gaming videos"
Video title: "Hitman 3 Speedrun World Record"

Should this video be REMOVED (filtered out) or KEPT for this user?

Respond with exactly one word: "keep" or "remove"
'''
    
    response = model.generate_content(prompt)
    print(f"Filtering decision: {response.text.strip()}")
    
except Exception as e:
    print(f"Error: {e}")