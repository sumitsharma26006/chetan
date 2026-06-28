from django.contrib import admin
from .models import ChatSession, Message, MoodLog

admin.site.register(ChatSession)
admin.site.register(Message)
admin.site.register(MoodLog)
