"""
AI handler module - encapsulates Gemini (Google Generative AI) calls and related logic
"""

import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()


class AIHandler:
    """AI handler"""
    
    def __init__(self):
        # Require Gemini key from environment only; no hardcoded fallback
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            st.error("GEMINI_API_KEY (or GOOGLE_API_KEY) is not set. Please add it to your environment or .env file.")
            raise RuntimeError("Missing GEMINI_API_KEY/GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        # Default to a broadly available model; allow override via env
        requested_model = os.getenv('GEMINI_MODEL', 'gemini-pro')
        self.model_name = self._resolve_supported_model(requested_model)
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
        """Streamed response via Gemini's generate_content with streaming."""
        model = genai.GenerativeModel(self.model_name)
        # Convert messages to a single prompt with role prefixes
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        stream = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            ),
            stream=True,
        )
        return st.write_stream((chunk.text for chunk in stream))
    
    def _get_normal_response(self, messages):
        """Non-streaming response using Gemini."""
        model = genai.GenerativeModel(self.model_name)
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        resp = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            ),
            stream=False,
        )
        return resp.text

    def _resolve_supported_model(self, requested_model: str) -> str:
        """Return a model name that exists and supports text generation.
        Falls back through known-good defaults if needed.
        """
        try:
            models = list(genai.list_models())
        except Exception:
            # If listing fails, just return the requested (SDK may still work)
            return requested_model

        def is_text_model(m) -> bool:
            methods = getattr(m, 'supported_generation_methods', None)
            if not methods:
                return False
            return ('generateContent' in methods) or ('generate_content' in methods)

        names = {m.name: m for m in models}
        if requested_model in names and is_text_model(names[requested_model]):
            return requested_model

        # common fallbacks by availability (start with basic gemini-pro)
        for candidate in ['gemini-pro', 'models/gemini-pro', 'gemini-1.5-flash', 'models/gemini-1.5-flash']:
            if candidate in names and is_text_model(names[candidate]):
                if candidate != requested_model:
                    st.warning(f"Requested model '{requested_model}' not available. Falling back to '{candidate}'.")
                return candidate

        # If nothing matched, return requested and let API raise a clear error
        return requested_model
    
    def set_model_params(self, model=None, temperature=None, max_tokens=None):
        """Set model parameters"""
        if model:
            self.model = model
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