from flask import Flask, render_template, request, redirect, session
from flask_mail import Mail, Message
import sqlite3
import random
import os

app = Flask(__name__)

app.secret_key = "ROVIQ_SECRET_KEY"

# Gmail Settings
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "roviq.support@gmail.com"
app.config["MAIL_PASSWORD"] = "valfdjavqhqwtfyi"

mail = Mail(app)

os.makedirs("static/profiles", exist_ok=True)


def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        birth_date TEXT,
        profile_pic TEXT
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


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        try:

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO users
        (username, email, password, birth_date, profile_pic)
        VALUES (?, ?, ?, ?, ?)
    """, (
        session["username"],
        session["email"],
        session["password"],
        session["birth_date"],
        ""
    ))

    conn.commit()
    conn.close()

except Exception as e:

    return f"DATABASE ERROR: {e}"
        

            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = c.fetchone()
        conn.close()

        if user:
            return redirect(f"/chat?user={username}")

        return "اسم المستخدم أو كلمة المرور غير صحيحة"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register_step1():
    if request.method == "POST":

        username = request.form.get("username", "").strip()

        conn = sqlite3.connect("chat.db")
        c = conn.cursor()

        c.execute("SELECT id FROM users WHERE username=?", (username,))
        user = c.fetchone()

        conn.close()

        if user:
            return "اسم المستخدم مستخدم مسبقاً"

        session["username"] = username
        return redirect("/register-step2")

    return render_template("register_step1.html")


@app.route("/register-step2", methods=["GET", "POST"])
def register_step2():
    if "username" not in session:
        return redirect("/register")

    if request.method == "POST":
        session["birth_date"] = request.form.get("birth_date")
        return redirect("/register-step3")

    return render_template("register_step2.html")


@app.route("/register-step3", methods=["GET", "POST"])
def register_step3():
    if "username" not in session:
        return redirect("/register")

    if request.method == "POST":

        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            return "كلمتا المرور غير متطابقتين"

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

    session["verify_code"] = "123456"
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

        c.execute("""
            INSERT INTO users
            (username, email, password, birth_date, profile_pic)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session["username"],
            session["email"],
            session["password"],
            session["birth_date"],
            ""
        ))

        conn.commit()
        conn.close()

        username = session["username"]
        session.clear()

        return redirect(f"/chat?user={username}")

    return render_template("verify.html")


@app.route("/chat", methods=["GET", "POST"])
def chat():
    username = request.args.get("user", "مستخدم")

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    if request.method == "POST":

        msg = request.form.get("msg", "")

        if msg:
            c.execute(
                "INSERT INTO messages (username, message) VALUES (?, ?)",
                (username, msg)
            )
            conn.commit()

    c.execute("SELECT username, message FROM messages ORDER BY id ASC")
    messages = c.fetchall()

    conn.close()

    return render_template(
        "chat.html",
        messages=messages,
        current_user=username,
        profile_pic=""
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
