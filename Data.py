import serial
import time

# Sæt COM-porten til den hvor Arduino er tilsluttet
arduino_port = "COM5"
baud_rate = 115200
co2 = ""
temp = ""
humidity = ""


# Opret forbindelse til Arduino
ser = serial.Serial(arduino_port, baud_rate, timeout=2)
time.sleep(2)  # vent på at Arduino resetter

print("Læser data fra Arduino...")

try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if line:
                if line.__contains__("CO2 concentration [ppm]: "):
                    co2 = line[25:]
                    print(co2)
                elif line.__contains__("Temperature [°C]: "):
                    temp = line[18:]
                    print(temp)
                elif line.__contains__("Relative Humidity [RH]: "):
                    humidity = line[24:]
                    print(humidity)
                print(line)  # udskriver alt Arduino sender


except KeyboardInterrupt:
    print("Afslutter...")
finally:
    ser.close()

