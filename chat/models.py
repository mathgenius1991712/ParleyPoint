from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)  # Allows a short bio.
    image = models.ImageField(upload_to='avatars/', null=True, blank=True)  # Allows an avatar photo.
    # upload_to defines where the images will be saved, 

    def __str__(self):
        return self.user.username

class ChatRoom(models.Model):
    # The 'participants' field is a many-to-many field with the User model.
    # This will be empty for a global chat room.
    # For a one-on-one chat, it will contain the two participants.
    participants = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return f"Chat room {self.id}"

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return self.message
        

class GlobalChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="global_chat_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
       

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True)
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        channel_layer = get_channel_layer()
        data = {
            "type": "send_notification",
            "message": self.message,
            "username": self.sender.username
        }
        group_name = f'notifications_{self.recipient.username}'
        async_to_sync(channel_layer.group_send)(group_name, data)
        super().save(*args, **kwargs)
