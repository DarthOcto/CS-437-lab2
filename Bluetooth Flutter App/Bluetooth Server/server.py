from bluedot.btcomm import BluetoothServer
import psutil
import time
from robot_hat import utils
from picarx import Picarx

px = Picarx()

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

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_c = int(f.read()) / 1000.0
            return f"TEMP:{temp_c:.1f}"
    except:
        return "TEMP:Unknown"

def data_received(data):
    print(f"Received: {data}")

    if data == "FORWARD":
        px.set_dir_servo_angle(0)
        px.forward(30)
        #time.sleep(1)
        #px.stop()

    elif data == "BACKWARD":
        px.set_dir_servo_angle(0)
        px.backward(30)
        #time.sleep(1)
        #px.stop()

    elif data == "LEFT":
        px.set_dir_servo_angle(-30)
        #time.sleep(0.5)

    elif data == "RIGHT":
        px.set_dir_servo_angle(30)
        #time.sleep(0.5)

# Start Bluetooth server
server = BluetoothServer(data_received)

print("Bluetooth Server Started - Waiting for connection...")

# **Main Loop to Send System Info Periodically**
while True:
    if server.client_connected:
        try:
            server.send(get_battery_level() + "\n")
            time.sleep(1)
            server.send(get_cpu_usage() + "\n")
            time.sleep(1)
            server.send(get_cpu_temp() + "\n")
        except Exception as e:
            print(f"Error sending system info: {e}")
    else:
        print("No client connected. Waiting...")
    
    time.sleep(5)  # Wait before retrying


