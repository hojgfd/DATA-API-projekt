import sqlite3
from flask import Flask, jsonify

# Initialize Flask app
app = Flask(__name__)

# Initialize database and create table if it doesn't exist
conn = sqlite3.connect('items.db')
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    klasse TEXT,
    sensor_id TEXT,
    tidspunkt TEXT,
    co2 REAL,
    temperature REAL,
    luftfugtighed REAL
)
""")

# Insert sample data if table is empty
cursor.execute("SELECT COUNT(*) FROM items")
count = cursor.fetchone()[0]
if count == 0:
    cursor.execute("""
        INSERT INTO items (klasse, sensor_id, tidspunkt, co2, temperature, luftfugtighed)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ("23HTCR", "luft01", "2025-08-27T12:15:00Z", 820, 22.3, 45.1))
    conn.commit()
conn.close()

# Define the GET /items endpoint
@app.route('/items', methods=['GET'])
def get_items():
    conn = sqlite3.connect('items.db')
    cursor = conn.cursor()
    cursor.execute("SELECT klasse, sensor_id, tidspunkt, co2, temperature, luftfugtighed FROM items")
    rows = cursor.fetchall()
    conn.close()

    items = []
    for row in rows:
        items.append({
            "klasse": row[0],
            "sensor_id": row[1],
            "tidspunkt": row[2],
            "mål": {
                "co2": row[3],
                "temperature": row[4],
                "luftfugtighed": row[5]
            }
        })
    return jsonify(items)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
