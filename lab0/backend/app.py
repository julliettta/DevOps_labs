from flask import Flask, request, jsonify, render_template
import psycopg2

app = Flask(__name__)

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
    return jsonify([{"id": r[0], "text": r[1]} for r in rows])

@app.route("/notes", methods=["POST"])
def add_note():
    data = request.get_json()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO notes (text) VALUES (%s)", (data["text"],))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "ok"}), 201

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)