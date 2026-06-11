from flask import Flask, request, redirect, render_template

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
    return render_template("login.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    username = request.args.get("user", "مستخدم")

    if request.method == "POST":
        msg = request.form.get("msg", "")
        if msg:
            messages.append((username, msg))

    return render_template("chat.html", messages=messages, current_user=username)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
