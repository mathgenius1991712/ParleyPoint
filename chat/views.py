from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from .models import Profile, ChatMessage, GlobalChatMessage, ChatRoom, Notification
import json
from .forms import UserUpdateForm, ProfileUpdateForm, ChatMessageForm
from django.shortcuts import get_object_or_404
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def index(request):
    return render(request, 'chat/index.html')
    
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the User and get a reference to the instance
            Profile.objects.create(user=user)  # Create a Profile for the User
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')

            # Log in the user and redirect to global chat
            login(request, user)
            return redirect('edit_profile', username=request.user.username)


    else:
        form = UserCreationForm()
    return render(request, 'chat/register.html', {'form': form})
    
    



@login_required  
def global_chat(request):
    messages = GlobalChatMessage.objects.all()
    users = User.objects.all()
    notifications = request.user.notifications.filter(read=False)
    chat_rooms = ChatRoom.objects.filter(participants=request.user)
    sorted_notifications = []

    for notification in notifications:
        # Skip notifications with no sender
        if notification.sender is None:
            continue
        sorted_usernames = sorted([request.user.username, notification.sender.username])
        sorted_notifications.append((notification, sorted_usernames))

    return render(request, 'chat/global-chat.html', {
        'messages': messages,
        'users': users,
        'notifications': sorted_notifications,
        'chat_rooms': chat_rooms
    })


@login_required
def private_chat(request, username1, username2):
    user1 = get_object_or_404(User, username=username1)
    user2 = get_object_or_404(User, username=username2)

    # Ensure that the logged-in user is one of the two users
    if request.user not in [user1, user2]:
        return HttpResponseForbidden()

    # Identify the other user
    other_user = user2 if request.user == user1 else user1

    # Find a ChatRoom that contains exactly these two users
    chat_room = ChatRoom.objects.filter(participants__in=[user1, user2])
    
    if chat_room.exists():
        # If the chat room exists, take the first one. 
        # This line assumes that there will be only one chat room for each pair of users.
        chat_room = chat_room.first()
    else:
        # If the chat room does not exist, create it and add the two users as participants
        chat_room = ChatRoom.objects.create()
        chat_room.participants.add(user1, user2)

        # Create a notification for the other user
        notification = Notification.objects.create(
            recipient=other_user,
            sender=request.user,
            message=f"{request.user.username} has started a private chat with you."
        )

        # Send a notification to the other user
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{other_user.username}",
            {
                "type": "new_notification",
                "notification": {
                    "id": notification.id,
                    "message": notification.message,
                    # other necessary fields...
                },
            },
        )
        
    # Fetch all messages in this chat room
    chat_messages = ChatMessage.objects.filter(room=chat_room).order_by('timestamp')
    
    context = {
        'recipient': other_user,
        'chat_messages': chat_messages
    }
    return render(request, 'chat/private-chat.html', context)



@login_required
def delete_notification(request, id):
    notification = get_object_or_404(Notification, id=id)
    if request.user != notification.recipient:
        return HttpResponseForbidden()
    notification.delete()
    return redirect('global_chat')


@login_required
def user_profile(request, username):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, 
                                   request.FILES, 
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('user_profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    user = get_object_or_404(User, username=username)
    
    sorted_usernames = sorted([request.user.username, user.username])

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user': user,
        'sorted_usernames': sorted_usernames,
    }
    
    return render(request, 'chat/user-profile.html', context)

@login_required
def edit_profile(request, username):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f'Your profile has been updated!')
            return redirect('user_profile', username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'chat/edit-profile.html', context)




@login_required
def send_message(request):
    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.save()
            return redirect('chat_room')
    else:
        form = ChatMessageForm()
    
    context = {
        'form': form
    }
    
    return render(request, 'chat/chat_room.html', context)
