import sqlite3
from flask import Flask, jsonify, render_template, request
import time
#import threading
#import serial


# Initialize Flask app
app = Flask(__name__)

# Sæt COM-porten til den hvor Arduino er tilsluttet
arduino_port = "COM5"
baud_rate = 115200
co2 = ""
temp = ""
humidity = ""


# Opret forbindelse til Arduino
#ser = serial.Serial(arduino_port, baud_rate, timeout=2)
time.sleep(2)  # vent på at Arduino resetter

lokaler_data = [
    {"klasse": "Nuværende placering", "co2": 1114, "temperatur": 22.22, "luftfugtighed": 66.23},
    {"klasse": "D2321", "co2": 1111, "temperatur": 22.55, "luftfugtighed": 55.12},
    {"klasse": "D2349", "co2":1004, "temperatur": 21.44, "luftfugtighed": 49.69}
]



'''def baggrundsopgave():
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    if line.__contains__("CO2 concentration [ppm]: "):
                        co2 = line[25:]
                        print(co2)
                        lokaler_data[0]["co2"] = co2
                    elif line.__contains__("Temperature [°C]: "):
                        temp = line[18:]
                        print(temp)
                        lokaler_data[0]["temperature"] = temp
                    elif line.__contains__("Relative Humidity [RH]: "):
                        humidity = line[24:]
                        print(humidity)
                        lokaler_data[0]["luftfugtighed"] = humidity
                    print(line)  # udskriver alt Arduino sender



    except KeyboardInterrupt:
        print("Afslutter...")
    finally:
        ser.close()'''


# Start baggrundstråden før Flask kører
#thread = threading.Thread(target=baggrundsopgave)
#thread.daemon = True  # gør tråden til daemon, så den stopper når appen stopper
#thread.start()

# Homescreen
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/data', methods=['POST'])
def receive_data():
    content = request.get_json(force=True)  # JSON fra ESP32
    print("Received:", content)

    # Opdater lokaler_data[0] med nye værdier
    lokaler_data[0]["co2"] = content.get("co2", 0)
    lokaler_data[0]["temperatur"] = content.get("temperature", 0.0)
    lokaler_data[0]["luftfugtighed"] = content.get("humidity", 0.0)

    return jsonify({"status": "ok", "received": content}), 200
# Lokaler
@app.route('/lokaler')
def lokaler():
    #conn = sqlite3.connect('items.db')
    #cursor = conn.cursor()
    #cursor.execute("SELECT klasse, sensor_id, tidspunkt, co2, temperature, luftfugtighed FROM items")
    #rows = cursor.fetchall()
    #conn.close()

    return render_template("lokaler.html", lokaler=lokaler_data)

# Varmest/koldest
@app.route('/varmest-koldest')
def varmest_koldest():
    #conn = sqlite3.connect('items.db')
    #cursor = conn.cursor()
    #cursor.execute("SELECT klasse, MAX(temperature), MIN(temperature) FROM items")
    #result = cursor.fetchone()
    #conn.close()

    #data = {
     #   "klasse": result[0],
      #  "max_temp": result[1],
       # "min_temp": result[2]
    #}

    return render_template("varmest-koldest.html")
    #return render_template("varmest-koldest.html",result=data)

# Anbefalinger
@app.route('/anbefalinger')
def anbefalinger():
    conn = sqlite3.connect('items.db')
    cursor = conn.cursor()
    cursor.execute("SELECT klasse, co2, temperature, luftfugtighed FROM items")
    rows = cursor.fetchall()
    conn.close()

    problemer = []
    for r in rows:
        problemer_i_lokale = []
        if r[1] > 1000:  # CO2 for højt
            problemer_i_lokale.append("For højt CO₂")
        if r[2] < 20:
            problemer_i_lokale.append("For koldt")
        if r[2] > 25:
            problemer_i_lokale.append("For varmt")
        if problemer_i_lokale:
            problemer.append((r[0], problemer_i_lokale))

    return jsonify(problemer)

if __name__ == "__main__":
    app.run(debug=True)