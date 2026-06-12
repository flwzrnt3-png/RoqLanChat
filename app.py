from flask import Flask, request, redirect, render_template
import sqlite3
import os

app = Flask(__name__)

os.makedirs("static/profiles", exist_ok=True)

def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        full_name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        birth_date TEXT,
        profile_pic TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        message TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS private_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
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
        profile_pic = request.files.get("profile_pic")

        filename = ""

        if profile_pic and profile_pic.filename:

            filename = profile_pic.filename

            profile_pic.save(
                os.path.join("static/profiles", filename)
            )

        conn = sqlite3.connect("chat.db")
        c = conn.cursor()

        try:

            c.execute(
                "INSERT INTO users (username,password,profile_pic) VALUES (?,?,?)",
                (username, password, filename)
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

    c.execute(
        "SELECT profile_pic FROM users WHERE username=?",
        (username,)
    )

    user_data = c.fetchone()

    profile_pic = ""

    if user_data:
        profile_pic = user_data[0]

    conn.close()

    return render_template(
        "chat.html",
        messages=messages,
        current_user=username,
        profile_pic=profile_pic
    )

@app.route("/private", methods=["GET", "POST"])
def private_chat():

    sender = request.args.get("user", "")
    receiver = request.args.get("to", "")

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    if request.method == "POST":

        msg = request.form.get("msg", "")

        if msg:

            c.execute(
                "INSERT INTO private_messages (sender,receiver,message) VALUES (?,?,?)",
                (sender, receiver, msg)
            )

            conn.commit()

    c.execute("""
    SELECT sender,receiver,message
    FROM private_messages
    WHERE
    (sender=? AND receiver=?)
    OR
    (sender=? AND receiver=?)
    ORDER BY id ASC
    """, (sender, receiver, receiver, sender))

    messages = c.fetchall()

    conn.close()

    return render_template(
        "private.html",
        messages=messages,
        sender=sender,
        receiver=receiver
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000
