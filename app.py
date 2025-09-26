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

def init_db():
    conn = sqlite3.connect("items.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            klasse TEXT,
            tidspunkt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            co2 INTEGER,
            temperatur REAL,
            luftfugtighed REAL
        )
    """)
    conn.commit()
    conn.close()



# Homescreen
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/data', methods=['POST'])
def receive_data():
    content = request.get_json(force=True)

    co2 = content.get("co2", 0)
    temperature = content.get("temperature", 0.0)
    humidity = content.get("humidity", 0.0)

    # Opdater lokaler_data[0] (så din nuværende visning virker)
    lokaler_data[0]["co2"] = co2
    lokaler_data[0]["temperatur"] = temperature
    lokaler_data[0]["luftfugtighed"] = humidity

    # GEM i databasen (historik)
    conn = sqlite3.connect("items.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO sensor_data (klasse, co2, temperatur, luftfugtighed)
        VALUES (?, ?, ?, ?)
    """, ("Nuværende placering", co2, temperature, humidity))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok", "received": content}), 200

@app.route('/historik')
def historik():
    conn = sqlite3.connect("items.db")
    c = conn.cursor()
    c.execute("""
        SELECT strftime('%Y-%m-%d %H:%M:00', tidspunkt) as minut,
               AVG(co2),
               AVG(temperatur),
               AVG(luftfugtighed)
        FROM sensor_data
        GROUP BY minut
        ORDER BY minut DESC
    """)
    rows = c.fetchall()
    conn.close()

    return render_template("historik.html", data=rows)


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

    # sortér efter temperatur
    lokaler_sorted = sorted(lokaler_data, key=lambda x: x["temperatur"], reverse=True)

    varmest = lokaler_sorted[0]
    koldest = lokaler_sorted[-1]

    return render_template(
        "varmest-koldest.html",
        lokaler=lokaler_sorted,
        varmest=varmest,
        koldest=koldest
    )
    #return render_template("varmest-koldest.html",result=data)

# Anbefalinger
@app.route('/anbefalinger')
def anbefalinger_side():
    # Saml alle lokaler der ikke opfylder anbefalinger
    lokaler_problemer = []
    for l in lokaler_data:
        problemer = []
        if l["co2"] > 1000:
            problemer.append("For højt CO₂")
        if l["temperatur"] < 20:
            problemer.append("For koldt")
        if l["temperatur"] > 25:
            problemer.append("For varmt")
        if problemer:
            lokaler_problemer.append({**l, "problemer": problemer})

    return render_template("anbefalinger.html", lokaler=lokaler_problemer)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
