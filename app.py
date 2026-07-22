from flask import Flask, send_from_directory, render_template
import os
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    app.run(port=5000, debug=True)