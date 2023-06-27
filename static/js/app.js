$(function() {
    // Connect to the WebSocket
    var socket = new WebSocket('ws://localhost:8000/ws/chat/');
    socket.withCredentials = true;


//var notificationSocket = new WebSocket('ws://localhost:8000/ws/notifications/');

socket.onopen = function(e) {
  //  alert("[open] Connection established");
};

// Handle errors.
socket.onerror = function(error) {
    alert(`[error] ${error.message}`);
};

// Listen for new messages from the server.
socket.onmessage = function(event) {
    let incomingData = JSON.parse(event.data);
    let messageBox = document.querySelector('#chat-messages');  // Change #message-box to #chat-messages
    let newMessage = document.createElement('div');
    newMessage.innerHTML = `
    <div class="mb-3">
        <p class="p-0 m-0 text-white"><strong>${incomingData.username}:</strong></p> 
        <span class="chat-message d-inline-block p-2">${incomingData.message}</span>
        </div>
    `;
    messageBox.appendChild(newMessage);
};

// Handle form submission to send messages.
let messageForm = document.querySelector('#messageForm');  // Change #message-form to #messageForm
messageForm.addEventListener('submit', function(e) {
    e.preventDefault();
 //   let messageInput = e.target.elements.message;
    let messageInput = document.querySelector('#messageInput');
    let message = messageInput.value;
    socket.send(JSON.stringify({
        'message': message,
        'username': username,
    }));
    messageInput.value = '';
});

// Handle disconnection.
socket.onclose = function(event) {
    if (event.wasClean) {
        alert(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
    } else {
        // Connection closed abnormally, e.g., server process killed or network down.
        alert('[close] Connection died');
    }
};
 
});


