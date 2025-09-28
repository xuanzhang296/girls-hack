"""
AI handler module - encapsulates local API calls and related logic
"""

import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()


class AIHandler:
    """AI handler"""
    
    def __init__(self):
        # Use local API endpoint
        self.api_url = os.getenv('LOCAL_API_URL', 'http://127.0.0.1:7860/api/v1/run/99354137-3d2e-402e-aba1-a954067bf60b')
        self.temperature = 0.7
        self.max_tokens = 4096
    
    def get_ai_response(self, messages, stream=True):
        """
        Get AI response.
        
        Args:
            messages: chat history list
            stream: whether to stream the response
            
        Returns:
            AI response content
        """
        try:
            if stream:
                return self._get_stream_response(messages)
            else:
                return self._get_normal_response(messages)
        except Exception as e:
            st.error(f"AI call error: {str(e)}")
            return "Sorry, I ran into a technical issue. Please try again later."
    
    def _get_stream_response(self, messages):
        """Streamed response via local API (simulated streaming)."""
        # For now, treat as non-streaming since local API may not support streaming
        response = self._get_normal_response(messages)
        # Simulate streaming by writing the response
        return st.write(response)
    
    def _get_normal_response(self, messages):
        """Non-streaming response using local API."""
        # Convert messages to a single prompt
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        
        # Request payload configuration
        payload = {
            "input_value": prompt,
            "output_type": "chat",
            "input_type": "chat"
        }
        
        # Request headers
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            # Send API request
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse response - adjust based on your API's response format
            response_data = response.json()
            
            # Extract text from response (adjust key based on your API response structure)
            if isinstance(response_data, dict):
                # Try common response keys
                for key in ['text', 'response', 'output', 'result', 'content']:
                    if key in response_data:
                        return str(response_data[key])
                # If no common key found, return the whole response as string
                return str(response_data)
            else:
                return str(response_data)
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Local API request failed: {str(e)}")
        except ValueError as e:
            raise Exception(f"Failed to parse API response: {str(e)}")

    def test_connection(self):
        """Test connection to local API."""
        try:
            payload = {
                "input_value": "Hello, this is a test message.",
                "output_type": "chat",
                "input_type": "chat"
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return True, "Connection successful"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def set_model_params(self, model=None, temperature=None, max_tokens=None):
        """Set model parameters"""
        if temperature is not None:
            self.temperature = temperature
        if max_tokens:
            self.max_tokens = max_tokens
    
    def add_system_prompt(self, messages, system_prompt):
        """Prepend a system prompt"""
        system_message = {"role": "system", "content": system_prompt}
        return [system_message] + messages
    
    def filter_messages(self, messages, max_messages=20):
        """Filter messages to keep conversation length reasonable"""
        if len(messages) > max_messages:
            # 保留最近的消息
            return messages[-max_messages:]
        return messages
    
    def process_user_input(self, user_input):
        """Process user input (validation/cleanup can be added here)"""
        return user_input.strip()
    
    def process_ai_output(self, ai_output):
        """Process AI output (post-processing can be added here)"""
        return ai_output


# Helper function
def get_ai_handler():
    """Get a singleton AI handler instance"""
    if 'ai_handler' not in st.session_state:
        st.session_state['ai_handler'] = AIHandler()
    return st.session_state['ai_handler'] 