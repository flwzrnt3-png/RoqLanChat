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
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <title>RoqLan Chat</title>

        <style>
        body{
            margin:0;
            font-family:Arial;
            background:linear-gradient(135deg,#4b0082,#ff1493);
            height:100vh;
            display:flex;
            justify-content:center;
            align-items:center;
        }

        .box{
            background:white;
            width:320px;
            padding:25px;
            border-radius:25px;
            text-align:center;
            box-shadow:0 0 25px rgba(0,0,0,.3);
        }

        h1{
            color:#4b0082;
        }

        input{
            width:90%;
            padding:12px;
            margin:10px;
            border:none;
            border-radius:12px;
            background:#f0f0f0;
        }

        button{
            width:95%;
            padding:12px;
            border:none;
            border-radius:12px;
            background:#ff1493;
            color:white;
            font-size:18px;
            cursor:pointer;
        }
        </style>
    </head>

    <body>

    <div class="box">

        <h1>❤️ RoqLan Chat</h1>

        <form method="post">

            <input
            name="username"
            placeholder="اسم المستخدم">

            <input
            name="code"
            type="password"
            placeholder="الكود السري">

            <button type="submit">
            دخول
            </button>

        </form>

    </div>

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

        if user == username:

            color = "#8a2be2"
            align = "right"

        else:

            color = "#ff1493"
            align = "left"

        chat_html += f"""
        <div style="text-align:{align};margin:15px;">

            <div style="
            display:inline-block;
            background:{color};
            color:white;
            padding:12px;
            border-radius:20px;
            max-width:70%;">

            <b>{user}</b><br>
            {text}

            </div>

        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>

    <title>RoqLan Chat</title>

    <style>

    body{{
        margin:0;
        background:#170024;
        font-family:Arial;
    }}

    .header{{
        background:#4b0082;
        color:white;
        text-align:center;
        padding:15px;
        font-size:24px;
        font-weight:bold;
    }}

    .messages{{
        height:75vh;
        overflow-y:auto;
        padding:10px;
    }}

    .bottom{{
        position:fixed;
        bottom:0;
        width:100%;
        background:white;
        padding:10px;
    }}

    .msginput{{
        width:75%;
        padding:12px;
        border-radius:20px;
        border:1px solid #ccc;
    }}

    .sendbtn{{
        padding:12px 20px;
        border:none;
        border-radius:20px;
        background:#ff1493;
        color:white;
    }}

    </style>

    </head>

    <body>

    <div class="header">
    ❤️ RoqLan Chat
    </div>

    <div class="messages">
    {chat_html}
    </div>

    <div class="bottom">

        <form method="post">

            <input
            class="msginput"
            name="msg"
            placeholder="اكتب رسالة...">

            <button
            class="sendbtn"
            type="submit">

            إرسال

            </button>

        </form>

    </div>

    </body>
    </html>
    """

app.run(host="0.0.0.0", port=5000)
