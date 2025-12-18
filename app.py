from flask import Flask, render_template
import threading
import motion

app = Flask(__name__)

# ======================
# Routes
# ======================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start_serpentine", methods=["POST"])
def start_serpentine():
    if not motion.motor_running:
        motion.motor_running = True
        threading.Thread(
            target=motion.serpentine_loop,
            daemon=True
        ).start()
    return "Started serpentine"


@app.route("/start_sidewinding", methods=["POST"])
def start_sidewinding():
    if not motion.motor_running:
        motion.motor_running = True
        threading.Thread(
            target=motion.sidewinding_loop,
            daemon=True
        ).start()
    return "Started sidewinding"


@app.route("/lower_sensor", methods=["POST"])
def lower_sensor():
    threading.Thread(
        target=motion.lower_sensor,
        daemon=True
    ).start()
    return "Lowered sensor"


@app.route("/raise_sensor", methods=["POST"])
def raise_sensor():
    threading.Thread(
        target=motion.raise_sensor,
        daemon=True
    ).start()
    return "Raised sensor"


@app.route("/stop", methods=["POST"])
def stop():
    motion.motor_running = False
    return "Stopped motor motion"


# ======================
# Run Flask
# ======================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
