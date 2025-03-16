import serial
import time
import os

SERIAL_PORT = "COM10"  # Change this to match your CNC port
BAUD_RATE = 115200

# 🔹 Full Path to Your G-code Files
GCODE_DIRECTORY = r"location of the gcode file"

def send_gcode_file(file_name):
    file_path = os.path.join(GCODE_DIRECTORY, file_name)

    if not os.path.exists(file_path):
        print(f" Error: {file_path} not found!")
        return

    print(f" Sending {file_name} to CNC...")

    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            time.sleep(2)  # Allow connection to stabilize
            # 🔹 Wake up GRBL
            ser.write(b"\r\n\r\n")  
            time.sleep(2)  # Allow GRBL to initialize
            ser.flushInput()  # Clear startup buffer
    
            # ✅ **Set current position as origin**
            ser.write(b"G92 X0 Y0 Z0\n")
            time.sleep(0.5)  # Allow processing time
            print(" Set current position as origin (G92 X0 Y0 Z0)")

            with open(file_path, "r") as file:
                for line in file:
                    gcode_line = line.strip()
                    if not gcode_line:
                        continue  
                    while True:
                        ser.write(b"?\n")  
                        time.sleep(0.5)
                        response = ser.readline().decode().strip()
                        print(f"🔄 GRBL Status: {response}")
                        if "ok" in response or "Idle" in response:
                            break  

                    if gcode_line.startswith("G4 P"):
                        gcode_line = f"G4 P{round(float(gcode_line.split('P')[1]), 2)}"

                    if gcode_line.startswith("G1Z"):
                        try:
                            # Extract the Z-value correctly
                            z_value = float(gcode_line.split("Z")[1].split(" ")[0])

                            # Convert Z movement from gcode files so that it moved according to our machine, change the values according to your machine
                            if z_value < 0:
                                gcode_line = "G1 Z-5  F1000"  # Pen up
                            else:
                                gcode_line = "G1 Z5  F1000"  # Pen down

                        except ValueError:
                            print(f" Error parsing Z command: {gcode_line}")
                            continue  
                    executed = False
                    retries = 5  # Maximum retries per command
                    while not executed and retries > 0:
                        ser.write((gcode_line + "\n").encode()) 
                        time.sleep(0.1)  # Allow processing time

                        response = ""
                        response_wait_time = 3  # Seconds to wait before retrying
                        start_time = time.time()

                        while time.time() - start_time < response_wait_time:
                            response = ser.readline().decode().strip()
                            if response:
                                print(f"🔹 Sent: {gcode_line}, Response: {response}")
                                if "ok" in response.lower():
                                    executed = True
                                    break  

                        if not executed:
                            print(f" No response for {gcode_line}, retrying ({retries} left)...")
                            retries -= 1
                            time.sleep(0.2)  # Small wait before retrying

                    if not executed:
                        print(f"❌ Error: {gcode_line} did not execute after multiple retries!")

            print(" CNC Execution Complete!")

    except Exception as e:
        print(f" Error communicating with CNC: {e}")
