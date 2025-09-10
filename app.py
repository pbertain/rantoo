from flask import Flask, render_template, request
from datetime import datetime, timezone

app = Flask(__name__)

def epoch_to_human(epoch):
    """Converts epoch seconds (UTC) to MM/DD/YYYY HH:MM."""
    dt = datetime.utcfromtimestamp(float(epoch))
    return dt.strftime('%m/%d/%Y %H:%M')

def human_to_epoch(human_str):
    """Converts MM/DD/YYYY HH:MM (UTC) to epoch seconds."""
    dt = datetime.strptime(human_str, '%m/%d/%Y %H:%M')
    dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    direction = None
    input_value = ''
    if request.method == "POST":
        direction = request.form.get("direction")
        input_value = request.form.get("input_value")
        try:
            if direction == "epoch_to_human":
                result = epoch_to_human(input_value)
            else:
                result = human_to_epoch(input_value)
        except Exception as e:
            result = f"Error: {e}"
    return render_template("index.html", result=result, direction=direction, input_value=input_value)

if __name__ == "__main__":
    # Listen on TCP/33081, all interfaces
    app.run(host="0.0.0.0", port=33081, debug=True)

