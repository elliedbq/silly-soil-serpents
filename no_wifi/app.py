from flask import Flask, render_template
import threading
import motion

app = Flask(__name__)
motion_thread = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start_forward", methods=["POST"])
def start_forward():
    global motion_thread
    if not motion.running:
        motion.running = True
        motion_thread = threading.Thread(
            target=motion.serpentine_loop, daemon=True
        )
        motion_thread.start()
    return "Started serpentine"


@app.route("/start_sidewinding", methods=["POST"])
def start_sidewinding():
    global motion_thread
    if not motion.running:
        motion.running = True
        motion_thread = threading.Thread(
            target=motion.sidewinding_loop, daemon=True
        )
        motion_thread.start()
    return "Started sidewinding"


@app.route("/stop", methods=["POST"])
def stop():
    motion.running = False
    return "Stopped motion"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)
