# في Schools/admin.py

from django.contrib import admin
from .models import SchoolProfile, JobPosting, JobApplication, Notification

@admin.register(SchoolProfile)
class SchoolProfileAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'user', 'school_type', 'location')
    search_fields = ('school_name', 'user__username', 'location')
    list_filter = ('school_type',)

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'school', 'required_specialization', 'posted_at', 'is_active')
    search_fields = ('title', 'required_specialization')
    list_filter = ('is_active', 'school__school_name')
    date_hierarchy = 'posted_at'

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'job', 'status', 'applied_at')
    search_fields = ('teacher__full_name', 'job__title')
    list_filter = ('status',)
    autocomplete_fields = ['job', 'teacher'] # يجعل البحث عن الوظيفة والمعلم سهلاً

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')
    list_filter = ('is_read',)

