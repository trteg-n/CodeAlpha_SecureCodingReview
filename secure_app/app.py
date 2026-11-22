import re
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
import sqlite3
from pathlib import Path

app = Flask(__name__)

# Load the secret key securely from an environment variable
app.secret_key = os.environ["FLASK_SECRET_KEY"]

# Secure session configuration
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=15),
    SESSION_REFRESH_EACH_REQUEST=True
)

# Enable global CSRF protection
csrf = CSRFProtect(app)
# Enable rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://"
)

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

# Server-side input validation
def valid_username(username):
    return bool(re.fullmatch(r"[A-Za-z0-9_]{3,30}", username))


def valid_email(email):
    return len(email) <= 254 and bool(
        re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
    )


def valid_password(password):
    return 15 <= len(password) <= 128

# Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        # Validate registration inputs
        if not valid_username(username):
            error = "Username must contain 3-30 letters, numbers or underscores."
            return render_template("register.html", error=error)
        
        if not valid_email(email):
            error = "Please enter a valid email address."
            return render_template("register.html", error=error)
        
        if not valid_password(password):
            error = "Password must contain 15-128 characters."
            return render_template("register.html", error=error)
        password_hash = generate_password_hash(password, method="scrypt")
        conn = get_db()

        try:
            conn.execute("""
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
            """, (username, email, password_hash))

            conn.commit()
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            error = "Username already exists."

        finally:
            conn.close()

    return render_template("register.html", error=error)


# Login
@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute",
               methods=["POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        # Validate login inputs
        if not valid_username(username) or not password or len(password) > 128:
            error = "Invalid username or password."
            return render_template("login.html", error=error)
        conn = get_db()

        user = conn.execute("""
        SELECT * FROM users
        WHERE username = ?
        """, (username,)).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):
    # Clear existing session data before authentication
            session.clear()
            session.permanent = True
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

    query = request.args.get("q", "").strip()

    # Validate search input
    if len(query) > 100:
        return render_template(
            "search.html",
            employees=[],
            query="",
            error="Search input must not exceed 100 characters."
        ), 400

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
# User profile
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    error = None
    conn = get_db()

    if request.method == "POST":
        email = request.form.get("email", "").strip()

        # Validate email before updating the database
        if not valid_email(email):
            error = "Please enter a valid email address."
        else:
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

    return render_template(
        "profile.html",
        user=user,
        error=error
    )

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


# Secure logout
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))
    


# Start application
if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)