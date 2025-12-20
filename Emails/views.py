# في Emails/views.py

import datetime
from django.conf import settings # استيراد الإعدادات
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

def send_welcome_email(username, recipient_email ):
    """
    يرسل بريداً ترحيبياً للمستخدم باستخدام قالب HTML.
    """
    subject = "مرحباً بك في منصة التوظيف التعليمي!"
    from_email = settings.DEFAULT_FROM_EMAIL  # استخدام الإيميل من الإعدادات
    recipient_list = [recipient_email]

    context = {
        'username': username,
        'year': datetime.date.today().year,
    }

    # استخدم المسار الصحيح للقالب مع اسم التطبيق
    html_message = render_to_string('emails/welcome.html', context)
    
    try:
        email_message = EmailMessage(subject, html_message, from_email, recipient_list)
        email_message.content_subtype = 'html'
        email_message.send()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
