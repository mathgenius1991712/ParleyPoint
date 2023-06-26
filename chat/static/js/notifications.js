var notificationSocket = new WebSocket('ws://localhost:8000/ws/notifications/');
notificationSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log("Received notification:", data);
    if (data.type === 'chat.request') {
        // Assuming you have a div with id 'notifications' for displaying notifications
        document.querySelector('#notifications').innerHTML += (data.message + '<br>');
    }
};
