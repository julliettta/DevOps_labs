import os
from flask import Flask, request, jsonify, render_template
import psycopg2

app = Flask(__name__)
INSTANCE_ID = os.environ.get("INSTANCE_ID", "unknown")

def get_conn():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="lab0",
        user="postgres",
        password="pass"
    )

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.after_request
def add_instance_header(response):
    response.headers["X-Instance-Id"] = INSTANCE_ID
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/notes", methods=["GET"])
def get_notes():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, text FROM notes ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({
        "instance": INSTANCE_ID,
        "notes": [{"id": r[0], "text": r[1]} for r in rows]
    })

@app.route("/notes", methods=["POST"])
def add_note():
    data = request.get_json()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO notes (text) VALUES (%s)", (data["text"],))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "ok", "instance": INSTANCE_ID}), 201

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    init_db()
    app.run(debug=True, port=port, host="0.0.0.0")