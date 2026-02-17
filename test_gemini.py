#!/usr/bin/env python3
"""
Quick test script to verify Google Gemini integration.
"""
import os
import json

# Set API key
os.environ['GOOGLE_API_KEY'] = 'AIzaSyDZfgU-dXxfgPOkqVjcYSfrq78F3sTKd20'

try:
    import google.generativeai as genai
    print("✅ google-generativeai library imported successfully")
    
    # Configure API
    genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
    print("✅ API key configured")
    
    # Create model
    model = genai.GenerativeModel('gemini-pro')
    print("✅ Gemini Pro model initialized")
    
    # Test classification
    prompt = """You are a support ticket classification assistant. Analyze this ticket and respond with ONLY a JSON object:
{"category": "billing|technical|account|general", "priority": "low|medium|high|critical"}

Ticket description:
I cannot log into my account after resetting my password. I keep getting an error message."""
    
    print("\n🤖 Testing classification...")
    response = model.generate_content(
        prompt,
        generation_config={
            'temperature': 0,
            'top_p': 1,
            'top_k': 1,
            'max_output_tokens': 200,
        }
    )
    
    response_text = response.text.strip()
    print(f"📝 Raw response: {response_text}")
    
    # Clean up response
    if response_text.startswith('```'):
        lines = response_text.split('\n')
        cleaned_lines = [line for line in lines if not line.startswith('```')]
        response_text = '\n'.join(cleaned_lines).strip()
    
    if response_text.lower().startswith('json'):
        response_text = response_text[4:].strip()
    
    # Parse JSON
    result = json.loads(response_text)
    print(f"✅ Parsed JSON: {result}")
    
    category = result.get('category')
    priority = result.get('priority')
    
    print(f"\n🎯 Classification Result:")
    print(f"   Category: {category}")
    print(f"   Priority: {priority}")
    
    # Validate
    valid_categories = ['billing', 'technical', 'account', 'general']
    valid_priorities = ['low', 'medium', 'high', 'critical']
    
    if category in valid_categories and priority in valid_priorities:
        print("\n✅ ALL TESTS PASSED! Gemini integration is working correctly.")
    else:
        print(f"\n❌ Invalid values returned")
        
except ImportError as e:
    print(f"❌ Failed to import google-generativeai: {e}")
    print("   Install with: pip install google-generativeai")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
