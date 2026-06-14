from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import random
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "ROVIQ_SECRET_KEY"

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
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ✉️ دالة إرسال البريد مع معالجة الأخطاء
def send_verification_email(to_email, code):
    try:
        msg = MIMEText(f"كود التحقق الخاص بك هو: {code}")
        msg["Subject"] = "كود التحقق من البريد"
        msg["From"] = "majdrhym573@gmail.com"
        msg["To"] = to_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("majdrhym573@gmail.com", "pwaoeityfmumzdem")  # استبدل APP_PASSWORD بكلمة مرور التطبيق
            server.send_message(msg)

        print("✅ Email sent successfully to:", to_email)

    except Exception as e:
        print("❌ Email send error:", e)   # يطبع الخطأ بالـ terminal
        # ما نخلي السيرفر ينهار، نرجع رسالة واضحة
        raise Exception("فشل إرسال البريد الإلكتروني، تأكد من إعدادات Gmail وكلمة مرور التطبيق.")


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("chat.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session["username"] = username
            return redirect(url_for("chat"))
        return "اسم المستخدم أو كلمة المرور غير صحيحة"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


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

        session["password"] = generate_password_hash(password)
        return redirect("/register-step4")

    return render_template("register_step3.html")


@app.route("/register-step4", methods=["GET", "POST"])
def register_step4():
    if "username" not in session:
        return redirect("/register")

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        session["email"] = email

        # توليد كود تحقق مكوّن من 6 أرقام
        code = str(random.randint(100000, 999999))
        session["verify_code"] = code

        send_verification_email(email, code)

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
            INSERT INTO users (username, email, password, birth_date, profile_pic)
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
        session["username"] = username
        return redirect(url_for("chat"))

    return render_template("verify.html")


@app.route("/resend-code")
def resend_code():
    if "email" not in session or "username" not in session:
        return redirect("/register")

    code = str(random.randint(100000, 999999))
    session["verify_code"] = code

    send_verification_email(session["email"], code)

    return redirect("/verify")


@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "username" not in session:
        return redirect("/")

    username = session["username"]

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    if request.method == "POST":
        msg = request.form.get("msg", "")
        if msg:
            c.execute("INSERT INTO messages (username, message) VALUES (?, ?)", (username, msg))
            conn.commit()

    c.execute("SELECT username, message, created_at FROM messages ORDER BY id ASC")
    messages = c.fetchall()
    conn.close()

    return render_template("chat.html", messages=messages, current_user=username)


@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect("/")

    username = session["username"]

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT username,email,birth_date,profile_pic FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    return render_template("profile.html", user=user)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
