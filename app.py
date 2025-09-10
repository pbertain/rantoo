from flask import Flask, render_template, request, jsonify
from flask_restx import Api, Resource, fields
from datetime import datetime, timezone
import re

app = Flask(__name__)

# Initialize Flask-RESTX API for Swagger documentation
api = Api(app, 
          version='1.0', 
          title='Rantoo Epoch Converter API',
          description='API for converting between epoch time and human-readable datetime',
          doc='/api/docs/',
          prefix='/api')

# Create namespaces
api_v1 = api.namespace('v1', description='JSON API endpoints')
curl_api = api.namespace('curl', description='Curl-friendly API endpoints', path='/curl')

# Add namespaces to API
api.add_namespace(api_v1)
api.add_namespace(curl_api)

def epoch_to_human(epoch):
    """Converts epoch seconds (UTC) to MM/DD/YYYY HH:MM."""
    dt = datetime.utcfromtimestamp(float(epoch))
    return dt.strftime('%m/%d/%Y %H:%M')

def human_to_epoch(human_str):
    """Converts MM/DD/YYYY HH:MM (UTC) to epoch seconds."""
    dt = datetime.strptime(human_str, '%m/%d/%Y %H:%M')
    dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())

@app.route("/health")
def health():
    """Health check endpoint for load balancers and monitoring."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}, 200

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

@app.route("/health")
def health():
    """Health check endpoint for load balancers and monitoring."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}, 200

if __name__ == "__main__":
    import os
    # Use environment variable for port, default to 33081 for production
    port = int(os.environ.get('PORT', 33081))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host="127.0.0.1", port=port, debug=debug)

