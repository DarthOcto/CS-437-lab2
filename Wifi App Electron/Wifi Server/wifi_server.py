import socket
import psutil
from robot_hat import utils
from picarx import Picarx
import time

px = Picarx()

HOST = "192.168.1.135"  # IP address of your Raspberry Pi
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

# Function to get the CPU temperature
def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_c = int(f.read()) / 1000.0
            return f"{temp_c:.1f}"
    except:
        return "Unknown"
        
# Calculate battery %
def battery_percentage(voltage):
    min_voltage = 6.0  # Fully discharged (3.0V per cell)
    max_voltage = 8.4  # Fully charged (4.2V per cell)

    voltage = max(min_voltage, min(voltage, max_voltage))

    percentage = ((voltage - min_voltage) / (max_voltage - min_voltage)) * 100

    return round(percentage, 2)
    
def get_battery_level():
    battery = battery_percentage(utils.get_battery_voltage())
    return f"BATTERY:{battery}" if battery else "BATTERY:Unknown"
    
def get_cpu_usage():
    return f"CPU:{psutil.cpu_percent()}"

# Set up the socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    print(f"Server listening on {HOST}:{PORT}...")

    try:
        while True:
            client, client_info = s.accept()
            print("Server received connection from: ", client_info)

            # Handle incoming data
            data = client.recv(1024)  # Receive data (maximum of 1024 bytes)
            if data != b"":
                print(f"Received data: {data}")

                # Check if it's a movement command or CPU temperature request
                command = data.decode("utf-8").strip()

                if command == "87":
                    print("Moving UP")
                    # Handle 'W' key (move up)
                    px.set_dir_servo_angle(0)
                    px.forward(30)
                    #time.sleep(1)
                    #px.stop()
                    client.sendall(b"DIR:Up")
                elif command == "83":
                    print("Moving DOWN")
                    # Handle 'S' key (move down)
                    px.set_dir_servo_angle(0)
                    px.backward(30)
                    #px.stop()
                    client.sendall(b"DIR:Down")
                elif command == "65":
                    print("Moving LEFT")
                    # Handle 'A' key (move left)
                    px.set_dir_servo_angle(-30)
                    #time.sleep(0.5)
                    client.sendall(b"DIR:Left")
                elif command == "68":
                    print("Moving RIGHT")
                    # Handle 'D' key (move right)
                    px.set_dir_servo_angle(30)
                    #time.sleep(0.5)
                    client.sendall(b"DIR:Right")
                elif command == "GET_TEMP":
                    temp = get_cpu_temperature()
                    if temp is not None:
                        print(f"Sending CPU temperature: TEMP:{temp}")
                        client.sendall(f"TEMP:{temp}".encode("utf-8"))
                    else:
                        client.sendall(b"Error: Could not get CPU temperature\n")
                elif command == "GET_BATT":
                    batt = get_battery_level()
                    print(f"Sending Battery Level: {batt}")
                    client.sendall(f"{batt}".encode("utf-8"))
                elif command == "GET_CPU":
                    cpu = get_cpu_usage()
                    print(f"Sending CPU Usage: {cpu}")
                    client.sendall(f"{cpu}".encode("utf-8"))
                elif command == "KILL":
                    px.stop()
                    client.sendall("KILL".encode("utf-8"))
                else:
                    print("Unknown command")
                    client.sendall(b"Unknown command\n")
                    
            

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
        s.close()
        print("Server socket closed")
