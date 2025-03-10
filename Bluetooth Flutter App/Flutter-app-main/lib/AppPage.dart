import 'package:flutter/material.dart';
import 'package:flutter_bluetooth_serial/flutter_bluetooth_serial.dart';
import 'dart:convert';
import 'dart:typed_data';
import 'dart:async';

class AppPage extends StatefulWidget {
  final BluetoothDevice server;

  AppPage({required this.server});

  @override
  _AppPageState createState() => _AppPageState();
}

class _AppPageState extends State<AppPage> {
  BluetoothConnection? connection;
  String batteryLevel = "Waiting...";
  String cpuUsage = "Waiting...";
  String cpuTemp = "Waiting...";

  @override
  void initState() {
    super.initState();
    _connectToDevice();
  }

  void _connectToDevice() async {
    try {
      connection = await BluetoothConnection.toAddress(widget.server.address);
      print("Connected to ${widget.server.name}");

      connection!.input!.listen((data) {
        String receivedData = String.fromCharCodes(data).trim();
        print("Received: $receivedData");

        if (receivedData.startsWith("BATTERY:")) {
          setState(() {
            batteryLevel = receivedData.split(":")[1] + "%";
          });
        } else if (receivedData.startsWith("CPU:")) {
          setState(() {
            cpuUsage = receivedData.split(":")[1] + "%";
          });
        } else if (receivedData.startsWith("TEMP:")) {
          setState(() {
            cpuTemp = receivedData.split(":")[1] + "°C";
          });
        }
      }).onDone(() {
        print("Disconnected");
      });

    } catch (error) {
      print("Error: $error");
    }
  }

  void _sendCommand(String command) {
    if (connection != null && connection!.isConnected) {
      connection!.output.add(Uint8List.fromList(command.codeUnits));
      connection!.output.allSent;
    }
  }

  @override
  void dispose() {
    connection?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Picar-X Control")),
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text("Battery: $batteryLevel", style: TextStyle(fontSize: 18)),
          Text("CPU Usage: $cpuUsage", style: TextStyle(fontSize: 18)),
          Text("CPU Temp: $cpuTemp", style: TextStyle(fontSize: 18)),
          SizedBox(height: 20),

          // Arrow Controls
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              IconButton(
                icon: Icon(Icons.arrow_upward, size: 50),
                onPressed: () => _sendCommand("FORWARD"),
              ),
            ],
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              IconButton(
                icon: Icon(Icons.arrow_back, size: 50),
                onPressed: () => _sendCommand("LEFT"),
              ),
              SizedBox(width: 20),
              IconButton(
                icon: Icon(Icons.arrow_forward, size: 50),
                onPressed: () => _sendCommand("RIGHT"),
              ),
            ],
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              IconButton(
                icon: Icon(Icons.arrow_downward, size: 50),
                onPressed: () => _sendCommand("BACKWARD"),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
