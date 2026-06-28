from django.db import models

class ChatSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.session_id}"

class Message(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('assistant', 'Assistant')]
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"

class MoodLog(models.Model):
    MOOD_CHOICES = [
        ('great', '😄 Great'),
        ('good', '😊 Good'),
        ('okay', '😐 Okay'),
        ('sad', '😢 Sad'),
        ('anxious', '😰 Anxious'),
    ]
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='moods')
    mood = models.CharField(max_length=10, choices=MOOD_CHOICES)
    note = models.TextField(blank=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mood} at {self.logged_at}"
