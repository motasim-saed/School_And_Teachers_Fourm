import requests
from django.conf import settings

def send_onesignal_notification(heading, content, user_ids=None, url=None, data=None, filters=None):
    """
    إرسال إشعار عبر OneSignal باستخدام REST API.
    إذا تم تمرير user_ids، سيتم الإرسال لهؤلاء المستخدمين فقط.
    """
    app_id = getattr(settings, 'ONESIGNAL_APP_ID', "09578f3c-1bbf-4ad2-8c90-b7804630a8dc")
    api_key = getattr(settings, 'ONESIGNAL_REST_API_KEY', None)
    
    if not api_key:
        print("OneSignal REST API Key missing in settings. Please check your .env file.")
        return None

    header = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {api_key}"
    }

    payload = {
        "app_id": app_id,
        "headings": {"en": heading, "ar": heading},
        "contents": {"en": content, "ar": content},
    }

    if user_ids:
        # إرسال لمستخدمين محددين عبر الـ External User ID (معرف المستخدم في Django)
        # OneSignal يتوقع قائمة من السلاسل النصية (strings)
        payload["include_external_user_ids"] = [str(uid) for uid in user_ids]
    elif filters:
        # استخدام الفلاتر (مثل user_type)
        payload["filters"] = filters
    else:
        # إرسال لجميع المشتركين إذا لم يتم تحديد مستخدمين أو فلاتر
        payload["included_segments"] = ["Subscribed Users"]
    
    if url:
        payload["url"] = url
        
    if data:
        payload["data"] = data

    try:
        print(f"Sending OneSignal notification: {heading}")
        # print(f"Payload: {payload}") # للتحقق من البيانات المرسلة
        response = requests.post("https://onesignal.com/api/v1/notifications", headers=header, json=payload)
        
        result = response.json()
        print(f"OneSignal Response Status: {response.status_code}")
        print(f"OneSignal Response Body: {result}")
        
        response.raise_for_status()
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error sending OneSignal notification: {e}")
        if hasattr(e.response, 'text'):
            print(f"Server response: {e.response.text}")
        return None
