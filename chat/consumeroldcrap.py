import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = f'user_{self.user.username}'  # create a unique room name for each user

        # Join the user's room
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        # Join the general room
        await self.channel_layer.group_add(
            "general_chat",
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the user's room
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

        # Leave the general room
        await self.channel_layer.group_discard(
            "general_chat",
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        message = data.get('message', '[No message]')
        username = data.get('username', '[No username]')
        recipient_username = data.get('recipient')  # this should be sent from the frontend when a private message is sent

        outgoing_message = {
            'message': message,
            'username': username,
            'timestamp': str(timezone.now().strftime('%Y-%m-%d %H:%M:%S'))
        }

        if recipient_username:  # If a recipient is specified, it's a private message
            recipient_room = f'user_{recipient_username}'
            # Send the message to the recipient's room
            await self.channel_layer.group_send(
                recipient_room,
                {
                    'type': 'chat_message',
                    'message': outgoing_message
                }
            )
        else:  # No recipient specified, so it's a group message
            # Send message to general chat room group
            await self.channel_layer.group_send(
                "general_chat",
                {
                    'type': 'chat_message',
                    'message': outgoing_message
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))
        
        


class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.recipient_username = self.scope['url_route']['kwargs']['username']  # get the recipient username from the URL
        self.room_name = f'private_{self.scope["user"].username}_{self.recipient_username}'  # create a unique room name for each chat

        # Join the chat room
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the chat room
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = f'notifications_{self.user.username}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Do something with received data if necessary

    # Call this method when a new notification is created
    async def new_notification(self, event):
        await self.send(text_data=json.dumps(event["notification"]))