import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def test_supabase():
    """Test Supabase connection"""
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    print("=" * 60)
    print("🔌 TESTING SUPABASE CONNECTION")
    print("=" * 60)
    
    if not supabase_url:
        print("❌ SUPABASE_URL not found in .env file")
        return False
    
    if not supabase_key:
        print("❌ SUPABASE_SERVICE_ROLE_KEY not found in .env file")
        return False
    
    print(f"📡 URL: {supabase_url}")
    print(f"🔑 Key: {supabase_key[:15]}...{supabase_key[-10:]}")
    print("-" * 60)
    
    try:
        client: Client = create_client(supabase_url, supabase_key)
        
        # Test Users table
        response = client.table('users').select('*').limit(5).execute()
        print(f"\n✅ Users table: {len(response.data)} users found")
        
        for user in response.data:
            print(f"   - {user.get('email')} ({user.get('role')})")
        
        print("\n" + "=" * 60)
        print("✅ Supabase connection successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_supabase()