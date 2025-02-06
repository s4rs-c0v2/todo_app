from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Required for Flask-SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Environment variables with defaults for Docker PostgreSQL image
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.environ.get("POSTGRES_DB", POSTGRES_USER)
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "db")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")

DB_CONFIG = {
    "dbname": POSTGRES_DB,
    "user": POSTGRES_USER,
    "password": POSTGRES_PASSWORD,
    "host": POSTGRES_HOST,
    "port": POSTGRES_PORT,
}

def create_tables():
    """Create tables if they don't exist"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                is_done BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Tables created/verified")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Initialize database on app start
create_tables()

def get_db_connection():
    """Get connection to database"""
    return psycopg2.connect(**DB_CONFIG)

def get_all_tasks():
    """Get all tasks and return them as a list of dictionaries"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, content, is_done, created_at FROM tasks ORDER BY created_at DESC")
    tasks = [{
        'id': task[0],
        'content': task[1],
        'is_done': task[2],
        'created_at': task[3].isoformat()
    } for task in cur.fetchall()]
    cur.close()
    conn.close()
    return tasks

def broadcast_tasks():
    """Broadcast updated tasks to all connected clients"""
    tasks = get_all_tasks()
    socketio.emit('tasks_updated', {'tasks': tasks})

@app.route("/")
def index():
    tasks = get_all_tasks()
    return render_template("index.html", tasks=tasks)

@app.route("/add_task", methods=["POST"])
def add_task():
    content = request.form.get("content")
    if content:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (content) VALUES (%s)", (content,))
        conn.commit()
        cur.close()
        conn.close()
        broadcast_tasks()
    return jsonify({"status": "success"})

@app.route("/update/<int:task_id>", methods=["POST"])
def update_task(task_id):
    is_done = request.form.get("done") == "true"
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET is_done = %s WHERE id = %s", (is_done, task_id))
    conn.commit()
    cur.close()
    conn.close()
    broadcast_tasks()
    return jsonify({"status": "success"})

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    broadcast_tasks()
    return jsonify({"status": "success"})

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    broadcast_tasks()

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
