document.onkeydown = updateKey;
document.onkeyup = resetKey;

const net = require('net');

var server_port = 65432;
var server_addr = "192.168.1.135";   // the IP address of your Raspberry PI


function client(message) {
    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        // 'connect' listener.
        console.log('connected to server!');
        // send the message
        client.write(`${message}\r\n`);
    });

    // get the data from the server
    client.on('data', (data) => {
        const receivedData = data.toString();
        console.log(receivedData);

        if (receivedData.startsWith("TEMP:")) {
            const temperature = receivedData.split(":")[1];
            document.getElementById("temperature").innerText = `${temperature} °C`;
        }

        if (receivedData.startsWith("CPU:")) {
            const cpu_use = receivedData.split(":")[1];
            document.getElementById("usage").innerText = `${cpu_use} %`;
        }

        if (receivedData.startsWith("BATTERY:")) {
            const batt_level = receivedData.split(":")[1];
            document.getElementById("battery").innerText = `${batt_level} %`;
        }

        if (receivedData.startsWith("DIR")) {
            const direction = receivedData.split(":")[1];
            document.getElementById("direction").innerText = `${direction}`;
        }

        document.getElementById("bluetooth").innerHTML = data.toString();
        console.log('Server response:', data.toString());
        client.end();
        client.destroy();
    });

    client.on('end', () => {
        console.log('disconnected from server');
    });
}

// for detecting which key is being pressed (W, A, S, D)
function updateKey(e) {
    e = e || window.event;

    if (e.keyCode == '87') {  // W key
        document.getElementById("upArrow").style.color = "green";
        client("87");
    } else if (e.keyCode == '83') {  // S key
        document.getElementById("downArrow").style.color = "green";
        client("83");
    } else if (e.keyCode == '65') {  // A key
        document.getElementById("leftArrow").style.color = "green";
        client("65");
    } else if (e.keyCode == '68') {  // D key
        document.getElementById("rightArrow").style.color = "green";
        client("68");
    }
}

// Reset the key styling when the key is released
function resetKey(e) {
    e = e || window.event;
    document.getElementById("upArrow").style.color = "grey";
    document.getElementById("downArrow").style.color = "grey";
    document.getElementById("leftArrow").style.color = "grey";
    document.getElementById("rightArrow").style.color = "grey";
}

// Update data for every 50ms
function update_data() {
    setInterval(function () {
        // Continuously call client (optional if needed)
        client("GET_TEMP");
        client("GET_BATT");
        client("GET_CPU");
    }, 1000);
}

function kill() {
    client("KILL");
}