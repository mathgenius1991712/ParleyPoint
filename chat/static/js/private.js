let username = document.querySelector('#username').dataset.username;
console.log("private  "+username);
let recipient = document.querySelector('#recipient').dataset.recipient;
console.log("private "+recipient);
var notificationSocket = new WebSocket(`ws://localhost:8000/ws/notifications/${username}/`);

// Connect to the appropriate WebSocket for private chat with the recipient
var chatSocket = new WebSocket(`ws://localhost:8000/ws/private_chat/${recipient}/`);
chatSocket.withCredentials = true;

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    document.querySelector('#private-chat-messages').innerHTML += (data.username + ': ' + data.message + '<br>');
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#messageForm').onsubmit = function(e) {
    console.log('Form submitted');
    e.preventDefault();

    let messageInputDom = document.querySelector('#privateinput');
    let message = messageInputDom.value;

    chatSocket.send(JSON.stringify({
        'message': message,
        'username': username  // Your own username
    }));

    messageInputDom.value = '';
    console.log('Message sent: ' + message);
};

chatSocket.onopen = function(e) {
    console.log('WebSocket connection established');
};