import os
from werkzeug.utils import secure_filename
from flask import Flask, request, redirect, render_template, url_for
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
try:
    c.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT")
except:
    pass
    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
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

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        conn = sqlite3.connect("chat.db")
        c = conn.cursor()

        c.execute(
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
def register():

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        conn = sqlite3.connect("chat.db")
        c = conn.cursor()

        try:

            c.execute(
                "INSERT INTO users (username,password) VALUES (?,?)",
                (username, password)
            )

            conn.commit()

        except:

            conn.close()
            return "اسم المستخدم موجود مسبقاً"

        conn.close()

        return redirect("/")

    return render_template("register.html")


@app.route("/chat", methods=["GET", "POST"])
def chat():

    username = request.args.get("user", "مستخدم")

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    if request.method == "POST":

        msg = request.form.get("msg", "")

        if msg:

            c.execute(
                "INSERT INTO messages (username,message) VALUES (?,?)",
                (username, msg)
            )

            conn.commit()

    c.execute(
        "SELECT username,message FROM messages ORDER BY id ASC"
    )

    messages = c.fetchall()

    conn.close()

    return render_template(
        "chat.html",
        messages=messages,
        current_user=username
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
