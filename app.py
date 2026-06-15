from flask import Flask, render_template, request, redirect, session
import sqlite3, os, random, requests

app = Flask(__name__)
app.secret_key = "ROVIQ_SECRET_KEY"

BOT_TOKEN = "8961109826:AAHgJgLP4R6YDo1L_2BYQ8w3G_NabLQrHTg"
CHAT_ID = "8947556088"

os.makedirs("static/profiles", exist_ok=True)

# تهيئة قاعدة البيانات
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
        profile_pic TEXT,
        status TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# صفحة تسجيل الدخول
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect("chat.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?",(email,password))
        user = c.fetchone()
        conn.close()

        if user:
            session["current_user"] = email
            return redirect("/profile")
        return "❌ البريد أو كلمة المرور غير صحيحة"

    return render_template("login.html")

# صفحة التسجيل
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        birth_date = request.form.get("birth_date")

        conn = sqlite3.connect("chat.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username,email,password,birth_date,profile_pic,status) VALUES (?,?,?,?,?,?)",
                  (username,email,password,birth_date,"",""))
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("register.html")

# صفحة البروفايل
@app.route("/profile", methods=["GET","POST"])
def profile():
    if "current_user" not in session:
        return redirect("/")
    email = session["current_user"]

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?",(email,))
    user = c.fetchone()

    if request.method == "POST":
        status = request.form.get("status","").strip()
        file = request.files.get("profile_pic")
        pic_path = user[5]  # profile_pic
        if file:
            pic_path = f"static/profiles/{email}.png"
            file.save(pic_path)
        c.execute("UPDATE users SET status=?, profile_pic=? WHERE email=?",(status,pic_path,email))
        conn.commit()
    conn.close()
    return render_template("profile.html", user=user)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
