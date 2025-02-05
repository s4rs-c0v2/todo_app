from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

# Environment variables with defaults for Docker PostgreSQL image
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.environ.get("POSTGRES_DB", POSTGRES_USER)  # Defaults to user name
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "172.17.0.2")
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

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                is_done BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
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


@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        content = request.form["content"]
        cur.execute("INSERT INTO tasks (content) VALUES (%s)", (content,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    cur.execute(
        "SELECT id, content, is_done, created_at FROM tasks ORDER BY created_at DESC;"
    )
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", tasks=tasks)


@app.route("/update/<int:task_id>", methods=["POST"])
def update_task(task_id):
    is_done = "done" in request.form
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET is_done = %s WHERE id = %s", (is_done, task_id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
