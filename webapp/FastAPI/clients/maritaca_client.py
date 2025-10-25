"""
Maritaca AI client module
"""
import openai
import os

# Global variables
_maritaca_client = None

def get_maritaca_client():
    global _maritaca_client
    
    if _maritaca_client is None:
        api_key = os.getenv("MARITACA_API_KEY")
        
        if not api_key:
            raise ValueError("MARITACA_API_KEY environment variable not set")
        
        _maritaca_client = openai.OpenAI(
            api_key=api_key,
            base_url="https://chat.maritaca.ai/api",
        )
        print("✅ Maritaca AI client initialized")
    
    return _maritaca_client