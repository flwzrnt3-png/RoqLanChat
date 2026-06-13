from flask import Flask, render_template, request, redirect, session
from flask_mail import Mail, Message
import sqlite3
import random
import os

app = Flask(__name__)

app.secret_key = "ROVIQ_SECRET_KEY_2026"

# ------------------------
# Gmail Settings
# ------------------------

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True

app.config["MAIL_USERNAME"] = "roviq.support@gmail.com"

app.config["MAIL_PASSWORD"] = "cgmi gaiz tsvm nxah"

mail = Mail(app)

# ------------------------
# Folders
# ------------------------

os.makedirs("static/profiles", exist_ok=True)

# ------------------------
# Database
# ------------------------

def init_db():

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        display_name TEXT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        birth_date TEXT,
        profile_pic TEXT,
        bio TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS verification_codes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        code TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        message TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()
@app.route("/register", methods=["GET", "POST"])
def register_step1():

    if request.method == "POST":

        username = request.form.get("username", "").strip()

        conn = sqlite3.connect("chat.db")
        c = conn.cursor()

        c.execute(
            "SELECT id FROM users WHERE username=?",
            (username,)
        )

        exists = c.fetchone()

        conn.close()

        if exists:
            return "اسم المستخدم مستخدم مسبقاً"

        session["username"] = username

        return redirect("/register-step2")

    return render_template("register_step1.html")


@app.route("/register-step2", methods=["GET", "POST"])
def register_step2():

    if "username" not in session:
        return redirect("/register")

    if request.method == "POST":

        birth_date = request.form.get("birth_date", "")

        session["birth_date"] = birth_date

        return redirect("/register-step3")

    return render_template("register_step2.html")
    @app.route("/register-step3", methods=["GET", "POST"])
def register_step3():

    if "username" not in session:
        return redirect("/register")

    if request.method == "POST":

        password = request.form.get("password", "")

        session["password"] = password

        return redirect("/register-step4")

    return render_template("register_step3.html")


@app.route("/register-step4", methods=["GET", "POST"])
def register_step4():

    if "username" not in session:
        return redirect("/register")

    if request.method == "POST":

        email = request.form.get("email", "").strip()

        code = str(random.randint(100000, 999999))

        session["email"] = email
        session["verify_code"] = code

        try:

            msg = Message(
                "ROVIQ Verification Code",
                sender=app.config["MAIL_USERNAME"],
                recipients=[email]
            )

            msg.body = f"Your verification code is: {code}"

            mail.send(msg)

        except Exception as e:

            return f"خطأ بإرسال الكود: {e}"

        return redirect("/verify")

    return render_template("register_step4.html")
    @app.route("/verify", methods=["GET", "POST"])
def verify():

    if "verify_code" not in session:
        return redirect("/register")

    if request.method == "POST":

        code = request.form.get("code", "").strip()

        if code != session["verify_code"]:
            return "كود التحقق غير صحيح"

        conn = sqlite3.connect("chat.db")
        c = conn.cursor()

        try:

            c.execute(
                """
                INSERT INTO users
                (
                    username,
                    email,
                    password,
                    birth_date,
                    full_name,
                    profile_pic
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session["username"],
                    session["email"],
                    session["password"],
                    session["birth_date"],
                    "",
                    ""
                )
            )

            conn.commit()

        except Exception as e:

            conn.close()
            return f"خطأ: {e}"

        conn.close()

        username = session["username"]

        session.clear()

        return redirect(f"/chat?user={username}")

    return render_template("verify.html")


@app.route("/profile/<username>")
def profile(username):

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute(
        """
        SELECT
        username,
        email,
        birth_date,
        full_name,
        profile_pic
        FROM users
        WHERE username=?
        """,
        (username,)
    )

    user = c.fetchone()

    conn.close()

    if not user:
        return "المستخدم غير موجود"

    return render_template(
        "profile.html",
        user=user
        )
