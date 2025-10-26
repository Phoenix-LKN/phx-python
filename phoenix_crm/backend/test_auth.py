import os
from dotenv import load_dotenv
from services.supabase_client import get_supabase_client

load_dotenv()

def test_supabase_connection():
    """Test Supabase connection and create a test user."""
    print("Testing Supabase connection...")
    
    try:
        supabase = get_supabase_client()
        print("✅ Supabase client created successfully")
        
        # Try to create a test user
        test_email = "test@example.com"
        test_password = "TestPassword123!"
        
        print(f"\nAttempting to create test user: {test_email}")
        
        try:
            # Sign up test user
            auth_response = supabase.auth.sign_up({
                "email": test_email,
                "password": test_password
            })
            print(f"✅ Test user created: {auth_response.user.email}")
            print(f"   User ID: {auth_response.user.id}")
            
            # Create user profile in users table
            user_profile = supabase.table("users").insert({
                "id": auth_response.user.id,
                "email": test_email,
                "full_name": "Test User",
                "role": "user"
            }).execute()
            print(f"✅ User profile created in database")
            
        except Exception as signup_error:
            if "already registered" in str(signup_error).lower():
                print(f"ℹ️  Test user already exists, trying to sign in...")
                
                # Try to sign in
                signin_response = supabase.auth.sign_in_with_password({
                    "email": test_email,
                    "password": test_password
                })
                print(f"✅ Successfully signed in as: {signin_response.user.email}")
                print(f"   User ID: {signin_response.user.id}")
            else:
                raise signup_error
        
        print("\n" + "="*50)
        print("TEST CREDENTIALS:")
        print("="*50)
        print(f"Email: {test_email}")
        print(f"Password: {test_password}")
        print("="*50)
        print("\n✅ All tests passed! You can now use these credentials to log in.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_supabase_connection()
