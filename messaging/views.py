from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Conversation, Message
from .forms import MessageForm
from user.models import User 
from Schools.models import Notification # Import Notification model

@login_required
def inbox(request):
    """
    Displays a list of conversations for the logged-in user, grouped by the other participant.
    """
    # جلب كل المحادثات
    all_conversations = Conversation.objects.filter(participants=request.user).order_by('-updated_at')
    
    # تجميع المحادثات حسب المستخدم الآخر لمنع التكرار
    unique_conversations_dict = {}
    
    for conversation in all_conversations:
        other_participant = conversation.participants.exclude(id=request.user.id).first()
        if other_participant:
            if other_participant.id not in unique_conversations_dict:
                 # تجهيز البيانات للعرض
                conversation.other_participant_name = other_participant.username 
                conversation.other_participant_image = None
                conversation.other_participant_id = other_participant.id # Important for linking
                
                if other_participant.user_type == 'SCHOOL':
                    if hasattr(other_participant, 'schoolprofile'):
                        conversation.other_participant_name = other_participant.schoolprofile.school_name
                        conversation.other_participant_image = other_participant.schoolprofile.logo
                elif other_participant.user_type == 'TEACHER':
                    if hasattr(other_participant, 'teacher_profile'):
                        conversation.other_participant_name = other_participant.teacher_profile.full_name
                        conversation.other_participant_image = other_participant.teacher_profile.profile_picture
                
                unique_conversations_dict[other_participant.id] = conversation

    # تحويل القاموس إلى قائمة وترتيبها
    conversations = list(unique_conversations_dict.values())
    
    # تحديث الإشعارات المتعلقة بالرسائل لتصبح مقروءة
    # (اختياري: يمكننا فعل ذلك فقط داخل المحادثة، لكن Inobx يظهر فيه علامة إجمالية)
    # لكن الأفضل أن يتم مسحها عند فتح المحادثة، ولكن المستخدم طلب "بمجرد فتح الاشعار"
    # وبما أن الإشعار في الهيدر يفتح الـ Inbox العام أحياناً، سنقوم بمسح إشعارات الرسائل هنا للتبسيط
    # أو يمكننا الاكتفاء بمسحها داخل المحادثة.
    # سأقوم بمسح إشعارات الرسائل العامة عند فتح الـ Inbox
    Notification.objects.filter(user=request.user, is_read=False, link__contains='/messages/').update(is_read=True)
    
    return render(request, 'messaging/inbox.html', {'conversations': conversations})

@login_required
def conversation_between_users(request, user_id):
    """
    Aggregates all messages between the logged-in user and the target user_id.
    """
    other_user = get_object_or_404(User, id=user_id)
    
    # 1. البحث عن كل المحادثات المشتركة
    conversations = Conversation.objects.filter(participants=request.user).filter(participants=other_user)
    
    # 2. جلب وتجميع كل الرسائل
    all_messages = Message.objects.filter(conversation__in=conversations).order_by('timestamp')
    
    # 3. تحديث حالة القراءة للرسائل الواردة
    conversations.first() # Trigger query just to be safe or iterate?
    # Better: Update using the messages queryset directly
    Message.objects.filter(conversation__in=conversations, sender=other_user, is_read=False).update(is_read=True)

    # 4. إعداد بيانات الطرف الآخر للعرض
    display_name = other_user.username
    display_image = None
    
    if other_user.user_type == 'SCHOOL':
        if hasattr(other_user, 'schoolprofile'):
            display_name = other_user.schoolprofile.school_name
            display_image = other_user.schoolprofile.logo
    elif other_user.user_type == 'TEACHER':
        if hasattr(other_user, 'teacher_profile'):
            display_name = other_user.teacher_profile.full_name
            display_image = other_user.teacher_profile.profile_picture
            
    # Mock visual object for template consistency
    other_participant = {
        'display_name': display_name,
        'display_image': display_image,
        'username': other_user.username,
        'first_name': other_user.first_name,
        # Pass full objects if needed, but dict is enough for display
    }

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            # العثور على محادثة "رئيسية" نشطة أو إنشاء واحدة جديدة
            # سنجعل أول محادثة تم العثور عليها هي "النشطة" أو ننشئ جديدة
            active_conversation = conversations.first()
            if not active_conversation:
                active_conversation = Conversation.objects.create()
                active_conversation.participants.add(request.user, other_user)
            
            message = form.save(commit=False)
            message.conversation = active_conversation
            message.sender = request.user
            message.save()
            active_conversation.save() # Update timestamp
            return redirect('messaging:conversation_with_user', user_id=other_user.id)
    else:
        form = MessageForm()

    return render(request, 'messaging/conversation_detail.html', {
        #'conversation': active_conversation, # No longer single conversation context
        'messages': all_messages,
        'form': form,
        'other_participant': other_participant,
    })

# Keeping legacy for safety but it shouldn't be used ideally in new UI
@login_required
def conversation_detail(request, conversation_id):
    """
    Redirects to the user-based view (wrapper for backward compatibility).
    """
    conversation = get_object_or_404(Conversation, id=conversation_id)
    other_participant = conversation.participants.exclude(id=request.user.id).first()
    if other_participant:
        return redirect('messaging:conversation_with_user', user_id=other_participant.id)
    else:
        messages.error(request, "محادثة غير صالحة")
        return redirect('messaging:inbox')

@login_required
def start_conversation(request, recipient_id):
    """
    Redirects immediately to the user-based conversation view.
    """
    return redirect('messaging:conversation_with_user', user_id=recipient_id)