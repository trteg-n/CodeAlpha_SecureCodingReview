
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from pathlib import Path

app = Flask(__name__)

# Intentionally hardcoded demonstration secret
app.secret_key = "employeehub-demo-secret"

DATABASE = Path(__file__).resolve().parent / "employees.db"


# Database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Initialise database
def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'employee'
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT NOT NULL,
            position TEXT NOT NULL
        )
    """)

    if conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0] == 0:
        employees = [
            ("Sarah Ahmed", "IT", "sarah@example.com", "Security Analyst"),
            ("James Wilson", "HR", "james@example.com", "HR Manager"),
            ("Aisha Ali", "Finance", "aisha@example.com", "Accountant"),
            ("Daniel Smith", "IT", "daniel@example.com", "Network Engineer"),
            ("Maya Hassan", "Marketing", "maya@example.com", "Marketing Officer")
        ]

        conn.executemany("""
            INSERT INTO employees (name, department, email, position)
            VALUES (?, ?, ?, ?)
        """, employees)

    conn.commit()
    conn.close()


# Home page
@app.route("/")
def index():
    return render_template("index.html")


# Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        conn = get_db()

        try:
            conn.execute("""
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
            """, (username, email, password))

            conn.commit()
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            error = "Username already exists."

        finally:
            conn.close()

    return render_template("register.html", error=error)


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        conn = get_db()

        user = conn.execute("""
            SELECT * FROM users
            WHERE username = ? AND password = ?
        """, (username, password)).fetchone()

        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect(url_for("dashboard"))

        error = "Invalid username or password."

    return render_template("login.html", error=error)


# Dashboard
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    employee_count = conn.execute(
        "SELECT COUNT(*) FROM employees"
    ).fetchone()[0]

    department_count = conn.execute(
        "SELECT COUNT(DISTINCT department) FROM employees"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        employee_count=employee_count,
        department_count=department_count
    )


# Employee search
@app.route("/search")
def search():
    if "user_id" not in session:
        return redirect(url_for("login"))

    query = request.args.get("q", "")
    conn = get_db()

    employees = conn.execute("""
        SELECT * FROM employees
        WHERE name LIKE ? OR department LIKE ?
    """, (f"%{query}%", f"%{query}%")).fetchall()

    conn.close()

    return render_template(
        "search.html",
        employees=employees,
        query=query
    )


# User profile
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    if request.method == "POST":
        email = request.form.get("email", "")

        conn.execute(
            "UPDATE users SET email = ? WHERE id = ?",
            (email, session["user_id"])
        )

        conn.commit()

    user = conn.execute("""
        SELECT id, username, email, role
        FROM users WHERE id = ?
    """, (session["user_id"],)).fetchone()

    conn.close()

    return render_template("profile.html", user=user)


# Administrator panel
@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return "Access denied", 403

    conn = get_db()

    users = conn.execute("""
        SELECT id, username, email, role FROM users
    """).fetchall()

    conn.close()

    return render_template("admin.html", users=users)


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# Start application
if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
