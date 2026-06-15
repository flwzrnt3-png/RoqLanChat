from flask import Flask, render_template, request, redirect, session
import sqlite3, os, random, requests, datetime

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

    c.execute("""
    CREATE TABLE IF NOT EXISTS private_messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        message TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# تسجيل الدخول (login.html مطوّر)
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
            return redirect("/users")
        return "❌ البريد أو كلمة المرور غير صحيحة"

    return render_template("login.html")

# التسجيل (register.html مطوّر)
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

# قائمة المستخدمين (users.html قديم)
@app.route("/users")
def users():
    if "current_user" not in session:
        return redirect("/")
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT username, profile_pic, status FROM users WHERE email != ?", (session["current_user"],))
    users = c.fetchall()
    conn.close()
    return render_template("users.html", users=users, current_user=session["current_user"])

# المحادثة (chat.html قديم)
@app.route("/chat/<receiver>", methods=["GET","POST"])
def chat(receiver):
    if "current_user" not in session:
        return redirect("/")
    sender = session["current_user"]
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    if request.method == "POST":
        msg = request.form.get("msg","").strip()
        if msg:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute("INSERT INTO private_messages (sender,receiver,message,timestamp) VALUES (?,?,?,?)",
                      (sender,receiver,msg,timestamp))
            conn.commit()

    c.execute("SELECT sender,message,timestamp FROM private_messages WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) ORDER BY id ASC",
              (sender,receiver,receiver,sender))
    messages = c.fetchall()
    conn.close()
    return render_template("chat.html", messages=messages, current_user=sender, receiver=receiver)

# البروفايل (profile.html مطوّر)
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

# تسجيل خروج
@app.route("/logout")
def logout():
    session.pop("current_user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
