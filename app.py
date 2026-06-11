from flask import Flask, request, redirect, render_template
import sqlite3

app = Flask(__name__)

SECRET_CODE = "1111"

def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

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
        code = request.form.get("code", "")

        if code == SECRET_CODE and username:
            return redirect(f"/chat?user={username}")

    return render_template("login.html")


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

    c.execute(
        "SELECT username, message FROM messages ORDER BY id ASC"
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
