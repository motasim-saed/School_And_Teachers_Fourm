from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('chat/<int:user_id>/', views.conversation_between_users, name='conversation_with_user'),
    path('start/<int:recipient_id>/', views.start_conversation, name='start_conversation'),
]
