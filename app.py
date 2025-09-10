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

def epoch_to_datetime_api(epoch):
    """Converts epoch seconds (UTC) to YYYY-MM-DD-HH:MM:SS format."""
    dt = datetime.utcfromtimestamp(float(epoch))
    return dt.strftime('%Y-%m-%d-%H:%M:%S')

def datetime_to_epoch_api(datetime_str):
    """Converts YYYYMMDD-HHMMSS (UTC) to epoch seconds."""
    # Parse the format YYYYMMDD-HHMMSS
    dt = datetime.strptime(datetime_str, '%Y%m%d-%H%M%S')
    dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())

# Define response models for Swagger documentation
epoch_response = api_v1.model('EpochResponse', {
    'epoch': fields.Integer(description='Epoch timestamp', example=1609459200),
    'datetime': fields.String(description='Human-readable datetime in YYYY-MM-DD-HH:MM:SS format', example='2021-01-01-00:00:00'),
    'status': fields.String(description='Success status', example='success')
})

datetime_response = api_v1.model('DateTimeResponse', {
    'datetime': fields.String(description='Input datetime in YYYYMMDD-HHMMSS format', example='20210101-000000'),
    'epoch': fields.Integer(description='Converted epoch timestamp', example=1609459200),
    'status': fields.String(description='Success status', example='success')
})

error_response = api_v1.model('ErrorResponse', {
    'error': fields.String(description='Error message', example='Invalid format. Expected YYYYMMDD-HHMMSS'),
    'status': fields.String(description='Error status', example='error')
})

# JSON API Endpoints with Swagger documentation
@api_v1.route('/epoch/<int:epoch_time>')
class EpochToDateTime(Resource):
    @api_v1.doc('epoch_to_datetime')
    @api_v1.marshal_with(epoch_response, code=200)
    @api_v1.marshal_with(error_response, code=400)
    def get(self, epoch_time):
        """Convert epoch timestamp to YYYY-MM-DD-HH:MM:SS format
        
        This endpoint converts a Unix epoch timestamp to a human-readable datetime string.
        
        **Example:**
        - Input: 1609459200
        - Output: 2021-01-01-00:00:00
        """
        try:
            datetime_str = epoch_to_datetime_api(epoch_time)
            return {
                'epoch': epoch_time,
                'datetime': datetime_str,
                'status': 'success'
            }
        except Exception as e:
            api_v1.abort(400, error=str(e), status='error')

@api_v1.route('/datetime/<string:datetime_str>')
class DateTimeToEpoch(Resource):
    @api_v1.doc('datetime_to_epoch')
    @api_v1.marshal_with(datetime_response, code=200)
    @api_v1.marshal_with(error_response, code=400)
    def get(self, datetime_str):
        """Convert YYYYMMDD-HHMMSS format to epoch timestamp
        
        This endpoint converts a datetime string in YYYYMMDD-HHMMSS format to a Unix epoch timestamp.
        
        **Format:** YYYYMMDD-HHMMSS (e.g., 20210101-000000)
        
        **Example:**
        - Input: 20210101-000000
        - Output: 1609459200
        """
        try:
            # Validate format: YYYYMMDD-HHMMSS
            if not re.match(r'^\d{8}-\d{6}$', datetime_str):
                api_v1.abort(400, error='Invalid format. Expected YYYYMMDD-HHMMSS', status='error')
            
            epoch_time = datetime_to_epoch_api(datetime_str)
            return {
                'datetime': datetime_str,
                'epoch': epoch_time,
                'status': 'success'
            }
        except Exception as e:
            api_v1.abort(400, error=str(e), status='error')

# Curl-friendly API Endpoints with Swagger documentation
@curl_api.route('/epoch/<int:epoch_time>')
class CurlEpochToDateTime(Resource):
    @curl_api.doc('curl_epoch_to_datetime')
    def get(self, epoch_time):
        """Convert epoch timestamp to YYYY-MM-DD-HH:MM:SS format (curl-friendly)
        
        This endpoint returns a plain text response suitable for curl commands.
        
        **Example:**
        - Input: 1609459200
        - Output: 2021-01-01-00:00:00
        """
        try:
            datetime_str = epoch_to_datetime_api(epoch_time)
            return datetime_str
        except Exception as e:
            return f"Error: {e}"

@curl_api.route('/datetime/<string:datetime_str>')
class CurlDateTimeToEpoch(Resource):
    @curl_api.doc('curl_datetime_to_epoch')
    def get(self, datetime_str):
        """Convert YYYYMMDD-HHMMSS format to epoch timestamp (curl-friendly)
        
        This endpoint returns a plain text response suitable for curl commands.
        
        **Format:** YYYYMMDD-HHMMSS (e.g., 20210101-000000)
        
        **Example:**
        - Input: 20210101-000000
        - Output: 1609459200
        """
        try:
            # Validate format: YYYYMMDD-HHMMSS
            if not re.match(r'^\d{8}-\d{6}$', datetime_str):
                return f"Error: Invalid format. Expected YYYYMMDD-HHMMSS"
            
            epoch_time = datetime_to_epoch_api(datetime_str)
            return str(epoch_time)
        except Exception as e:
            return f"Error: {e}"

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
    import os
    # Use environment variable for port, default to 33081 for production
    port = int(os.environ.get('PORT', 33081))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host="127.0.0.1", port=port, debug=debug)

