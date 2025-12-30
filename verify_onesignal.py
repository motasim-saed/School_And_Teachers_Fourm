import os
import django
from django.conf import settings
import requests

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'School_And_Teachers_Fourm.settings')
django.setup()

def verify_onesignal():
    print("Verifying OneSignal Configuration...")
    
    app_id = getattr(settings, 'ONESIGNAL_APP_ID', None)
    api_key = getattr(settings, 'ONESIGNAL_REST_API_KEY', None)
    
    print(f"ONESIGNAL_APP_ID: {app_id}")
    if api_key:
        masked_key = api_key[:4] + "*" * (len(api_key) - 4)
        print(f"ONESIGNAL_REST_API_KEY: {masked_key}")
    else:
        print("ONESIGNAL_REST_API_KEY: MISSING")
        
    if not app_id or not api_key:
        print("ERROR: Missing configuration.")
        return

    print("\nAttempting to send a test notification to ALL Subscribed Users...")
    
    header = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {api_key}"
    }

    payload = {
        "app_id": app_id,
        "headings": {"en": "Test Notification", "ar": "إشعار تجريبي"},
        "contents": {"en": "This is a test notification from the verification script.", "ar": "هذا إشعار تجريبي من سكريبت التحقق."},
        "included_segments": ["Subscribed Users"]
    }
    
    try:
        response = requests.post("https://onesignal.com/api/v1/notifications", headers=header, json=payload)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.json()}")
        
        if response.status_code == 200:
            print("SUCCESS: Notification sent successfully.")
        else:
            print("FAILURE: Failed to send notification.")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    verify_onesignal()
