console.log("notification "+ username); 

let notificationSocket = new WebSocket(`ws://localhost:8000/ws/notifications/${username}/`);

notificationSocket.onopen = function(e) {
    console.log("Notification Connection opened");
};
notificationSocket.onmessage = function(e) {
    console.log("received notification");
    var data = JSON.parse(e.data);

    console.log("checking ",data.type == 'send_notification')
    if (data.type == 'send_notification') { // Change 'chat.request' to 'chat.request_message'
        console.log("adding new elemement to dom");
        var notificationDiv = document.querySelector('#notifications');
        var link = document.createElement('a');
        link.href = '/chat/' + username + '/' + data.sender;
        link.textContent = data.message;
        notificationDiv.appendChild(link);
        notificationDiv.innerHTML += '<br>';
    }
};

notificationSocket.onerror = function(error) {
    console.error("WebSocket Error: ", error);
};

notificationSocket.onclose = function(event) {
    console.log("WebSocket Closed: ", event);
};
 
	  
