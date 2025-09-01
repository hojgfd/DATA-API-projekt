import sqlite3
from flask import Flask, jsonify, render_template

# Initialize Flask app
app = Flask(__name__)

# Homescreen
@app.route('/')
def home():
    return render_template("home.html")


# Lokaler
@app.route('/lokaler')
def lokaler():
    conn = sqlite3.connect('items.db')
    cursor = conn.cursor()
    cursor.execute("SELECT klasse, sensor_id, tidspunkt, co2, temperature, luftfugtighed FROM items")
    rows = cursor.fetchall()
    conn.close()

    return render_template("lokaler.html", rows=rows)

# Varmest/koldest
@app.route('/varmest-koldest')
def varmest_koldest():
    conn = sqlite3.connect('items.db')
    cursor = conn.cursor()
    cursor.execute("SELECT klasse, MAX(temperature), MIN(temperature) FROM items")
    result = cursor.fetchone()
    conn.close()

    return f"🌡️ {result[0]}: varmest {result[1]}°C, koldest {result[2]}°C"

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
