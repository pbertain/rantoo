from flask import Flask, render_template, request, jsonify, Blueprint
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
          prefix='/api',
          custom_css_url='/static/swagger-ui.css')

# Create namespaces
api_v1 = api.namespace('v1', description='JSON API endpoints')

# Add namespaces to API
api.add_namespace(api_v1)

# Create a separate blueprint for curl endpoints
curl_bp = Blueprint('curl', __name__, url_prefix='/curl')

def epoch_to_human(epoch):
    """Converts epoch seconds (UTC) to %a YYYY-MM-DD HH:MM:SS format."""
    dt = datetime.utcfromtimestamp(float(epoch))
    return dt.strftime('%a %Y-%m-%d %H:%M:%S')

def human_to_epoch(human_str):
    """Converts datetime string to epoch seconds (UTC). Supports multiple formats:
    - YYYY-MM-DD-HHMMSS (e.g., 2025-09-10-131100)
    - YYYYMMDDHHMMSS (e.g., 20250910131100)
    - YYYYMMDDHHMM (e.g., 202509101311) - seconds default to 00
    """
    # Remove any spaces that might have been URL-encoded
    human_str = human_str.replace('%20', ' ').strip()
    
    # Try different formats
    formats = [
        '%Y-%m-%d-%H%M%S',  # 2025-09-10-131100
        '%Y%m%d%H%M%S',     # 20250910131100
        '%Y%m%d%H%M',       # 202509101311 (seconds default to 00)
        '%m/%d/%Y %H:%M',   # 12/25/2023 14:30 (legacy format)
    ]
    
    for fmt in formats:
        try:
            if fmt == '%Y%m%d%H%M':  # Handle missing seconds
                dt = datetime.strptime(human_str, fmt)
                dt = dt.replace(second=0)  # Default seconds to 00
            else:
                dt = datetime.strptime(human_str, fmt)
            dt = dt.replace(tzinfo=timezone.utc)
            return int(dt.timestamp())
        except ValueError:
            continue
    
    raise ValueError(f"Unsupported datetime format. Supported formats: YYYY-MM-DD-HHMMSS, YYYYMMDDHHMMSS, YYYYMMDDHHMM, MM/DD/YYYY HH:MM")

# Define response models for Swagger documentation
datetime_response = api.model('DateTimeResponse', {
    'epoch': fields.Integer(description='Epoch timestamp in seconds'),
    'datetime': fields.String(description='Human-readable datetime in %a YYYY-MM-DD HH:MM:SS format'),
    'input': fields.String(description='Original input value')
})

epoch_response = api.model('EpochResponse', {
    'epoch': fields.Integer(description='Epoch timestamp in seconds'),
    'datetime': fields.String(description='Human-readable datetime in %a YYYY-MM-DD HH:MM:SS format'),
    'input': fields.String(description='Original input value')
})

# API v1 endpoints
@api_v1.route('/datetime/<path:datetime_str>')
class DateTimeConverter(Resource):
    @api_v1.doc('convert_datetime_to_epoch')
    @api_v1.marshal_with(epoch_response)
    def get(self, datetime_str):
        """Convert human-readable datetime to epoch timestamp.
        
        Supported formats:
        - YYYY-MM-DD-HHMMSS (e.g., 2025-09-10-131100)
        - YYYYMMDDHHMMSS (e.g., 20250910131100)
        - YYYYMMDDHHMM (e.g., 202509101311) - seconds default to 00
        - MM/DD/YYYY HH:MM (e.g., 12/25/2023 14:30) - legacy format
        """
        try:
            epoch = human_to_epoch(datetime_str)
            return {
                'epoch': epoch,
                'datetime': datetime_str,
                'input': datetime_str
            }
        except Exception as e:
            api_v1.abort(400, f"Invalid datetime format: {e}")

@api_v1.route('/epoch/<int:epoch_time>')
class EpochConverter(Resource):
    @api_v1.doc('convert_epoch_to_datetime')
    @api_v1.marshal_with(datetime_response)
    def get(self, epoch_time):
        """Convert epoch timestamp to human-readable datetime."""
        try:
            datetime_str = epoch_to_human(epoch_time)
            return {
                'epoch': epoch_time,
                'datetime': datetime_str,
                'input': str(epoch_time)
            }
        except Exception as e:
            api_v1.abort(400, f"Invalid epoch timestamp: {e}")

# Curl v1 endpoints (same functionality, different response format for curl)
@curl_bp.route('/v1/datetime/<path:datetime_str>')
def curl_datetime_converter(datetime_str):
    """Convert human-readable datetime to epoch timestamp (curl-friendly).
    
    Supported formats:
    - YYYY-MM-DD-HHMMSS (e.g., 2025-09-10-131100)
    - YYYYMMDDHHMMSS (e.g., 20250910131100)
    - YYYYMMDDHHMM (e.g., 202509101311) - seconds default to 00
    - MM/DD/YYYY HH:MM (e.g., 12/25/2023 14:30) - legacy format
    """
    try:
        epoch = human_to_epoch(datetime_str)
        return f"Epoch: {epoch}\nDatetime: {datetime_str}\nInput: {datetime_str}"
    except Exception as e:
        return f"Error: Invalid datetime format: {e}", 400

@curl_bp.route('/v1/epoch/<int:epoch_time>')
def curl_epoch_converter(epoch_time):
    """Convert epoch timestamp to human-readable datetime (curl-friendly)."""
    try:
        datetime_str = epoch_to_human(epoch_time)
        return f"Epoch: {epoch_time}\nDatetime: {datetime_str}\nInput: {epoch_time}"
    except Exception as e:
        return f"Error: Invalid epoch timestamp: {e}", 400

# Register the curl blueprint
app.register_blueprint(curl_bp)

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

