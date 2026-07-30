import os
from supabase import create_client, Client
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        if not self.supabase_url or not self.supabase_key:
            logger.warning('⚠️ Supabase credentials not configured')
            self.client = None
        else:
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info('✅ Supabase client initialized')
    
    def get_client(self) -> Client:
        if not self.client:
            raise Exception('Supabase client not initialized')
        return self.client
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            if not self.client:
                return None
            response = self.client.table('users').select('*').eq('email', email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f'Error getting user: {e}')
            return None
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.client:
                raise Exception('Supabase client not initialized')
            if 'id' not in user_data:
                user_data['id'] = str(uuid.uuid4())
            response = self.client.table('users').insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f'Error creating user: {e}')
            raise
    
    def update_last_login(self, user_id: str) -> None:
        try:
            if not self.client:
                return
            self.client.table('users').update({'last_login': datetime.now().isoformat()}).eq('id', user_id).execute()
        except Exception as e:
            logger.error(f'Error updating last login: {e}')
    
    def get_all_users(self, limit: int = 1000) -> List[Dict[str, Any]]:
        try:
            if not self.client:
                return []
            response = self.client.table('users').select('*').order('created_at', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f'Error getting users: {e}')
            return []
    
    def save_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.client:
                raise Exception('Supabase client not initialized')
            if 'id' not in message_data:
                message_data['id'] = str(uuid.uuid4())
            response = self.client.table('messages').insert(message_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f'Error saving message: {e}')
            raise
    
    def get_chat_history(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            if not self.client:
                return []
            response = self.client.table('messages').select('*').eq('session_id', session_id).order('created_at', desc=False).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f'Error getting chat history: {e}')
            return []
