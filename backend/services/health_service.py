import os
import requests
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class HealthService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.api_url = os.getenv('GEMINI_API_URL', 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent')
        
        self.system_prompt = '''You are a Personal Health Assistant AI. Your role is to provide helpful, accurate, and safe health information.

IMPORTANT RULES:
1. ONLY provide health-related information
2. ALWAYS include a medical disclaimer
3. DO NOT diagnose or prescribe medications
4. Encourage users to consult healthcare professionals
5. Be empathetic and supportive
6. Use emojis for better engagement

Always end with: "⚠️ Remember: I'm an AI assistant, not a doctor. Please consult a healthcare professional for medical advice."'''

    def get_health_response(self, user_message: str, chat_history: Optional[List[Dict]] = None) -> str:
        if not self.api_key or self.api_key == 'your_gemini_api_key_here':
            return self._get_fallback_response(user_message)
        
        try:
            history_context = ""
            if chat_history:
                recent_messages = chat_history[-10:]
                history_lines = []
                for msg in recent_messages:
                    sender = "User" if msg.get('sender') == 'user' else "Assistant"
                    text = msg.get('text', '')
                    history_lines.append(f"{sender}: {text}")
                history_context = "\n".join(history_lines)
            
            prompt = f"{self.system_prompt}\n\nPrevious conversation:\n{history_context or 'No previous conversation'}\n\nUser: {user_message}\nAssistant:"
            
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 800,
                    "topP": 0.9,
                    "topK": 40
                }
            }
            
            response = requests.post(f"{self.api_url}?key={self.api_key}", headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                generated_text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                if not generated_text:
                    return "I'm sorry, I couldn't generate a response. Please try again."
                if "consult a healthcare professional" not in generated_text.lower():
                    generated_text += "\n\n⚠️ **Remember:** I'm an AI assistant, not a doctor. Please consult a healthcare professional for medical advice."
                return generated_text
            else:
                return self._get_fallback_response(user_message)
        except Exception as e:
            logger.error(f'Gemini API error: {str(e)}')
            return self._get_fallback_response(user_message)
    
    def _get_fallback_response(self, user_message: str) -> str:
        return '''🔴 **I'm having trouble connecting to the health database.**

Please try again in a moment. If the issue persists, check your internet connection.

Here are some health topics you can ask about:
- 🤒 Fever treatment
- 🤕 Headache relief
- 🤧 Cough remedies
- 😷 Cold and flu care
- 🧠 Stress management
- 🩸 Diabetes care
- ❤️ Blood pressure management

⚠️ **Remember:** I'm an AI assistant, not a doctor. Please consult a healthcare professional for medical advice.'''
