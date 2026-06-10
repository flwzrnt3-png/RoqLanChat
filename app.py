from flask import Flask, request, redirect

app = Flask(__name__)

messages = []
SECRET_CODE = "1111"

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username", "")
        code = request.form.get("code", "")

        if code == SECRET_CODE and username:
            return redirect(f"/chat?user={username}")

    return """
    <html dir="rtl">
    <body style="font-family:Arial;text-align:center;margin-top:80px;">
        <h1>❤️ RoqLan Chat</h1>

        <form method="post">
            <input name="username" placeholder="اسم المستخدم"><br><br>

            <input name="code" type="password" placeholder="الكود السري"><br><br>

            <button type="submit">دخول</button>
        </form>

    </body>
    </html>
    """

@app.route("/chat", methods=["GET", "POST"])
def chat():

    username = request.args.get("user", "مستخدم")

    if request.method == "POST":
        msg = request.form.get("msg", "")

        if msg:
            messages.append((username, msg))

    chat_html = ""

    for user, text in messages:
        chat_html += f"""
        <div style="
            background:white;
            padding:10px;
            margin:10px;
            border-radius:10px;">
            <b>{user}</b><br>
            {text}
        </div>
        """

    return f"""
    <html dir="rtl">
    <body style="background:#f2f2f2;font-family:Arial;">

        <h2 style="text-align:center;">
        ❤️ RoqLan Chat
        </h2>

        {chat_html}

        <form method="post">
            <input name="msg" placeholder="اكتب رسالة">
            <button type="submit">إرسال</button>
        </form>

    </body>
    </html>
    """

app.run(host="0.0.0.0", port=5000)

