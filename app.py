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
          prefix='/api',
          doc=False) # Custom /api/docs/ route handles documentation

# Create namespaces
api_v1 = api.namespace('v1', description='JSON API endpoints (v1)')

# Add namespaces to API
api.add_namespace(api_v1)

def epoch_to_human(epoch):
    """Converts epoch seconds (UTC) to formatted datetime string."""
    dt = datetime.fromtimestamp(float(epoch), tz=timezone.utc)
    return dt.strftime('%a %Y-%m-%d %H:%M:%S')

def human_to_epoch(human_str):
    """Converts various datetime formats to epoch seconds."""
    # Handle YYYY-MM-DD-HHMMSS format
    if re.match(r'^\d{4}-\d{2}-\d{2}-\d{6}$', human_str):
        dt = datetime.strptime(human_str, '%Y-%m-%d-%H%M%S')
        dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    
    # Handle YYYYMMDDHHMMSS format
    elif re.match(r'^\d{14}$', human_str):
        dt = datetime.strptime(human_str, '%Y%m%d%H%M%S')
        dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    
    # Handle YYYYMMDDHHMM format (no seconds) - default to 00 seconds
    elif re.match(r'^\d{12}$', human_str):
        # Parse as YYYYMMDDHHMM and set seconds to 00
        dt = datetime.strptime(human_str, '%Y%m%d%H%M')
        dt = dt.replace(second=0, tzinfo=timezone.utc)
        return int(dt.timestamp())
    
    # Handle legacy MM/DD/YYYY HH:MM format
    elif re.match(r'^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}$', human_str):
        dt = datetime.strptime(human_str, '%m/%d/%Y %H:%M')
        dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    
    else:
        raise ValueError("Invalid datetime format. Supported formats: YYYY-MM-DD-HHMMSS, YYYYMMDDHHMMSS, YYYYMMDDHHMM, MM/DD/YYYY HH:MM")

# Define response models for Swagger documentation
epoch_response = api_v1.model('EpochResponse', {
    'epoch': fields.Integer(description='Epoch timestamp', example=1757509860),
    'datetime': fields.String(description='Human readable datetime', example='Wed 2025-09-10 13:11:00'),
    'input': fields.String(description='Original input', example='1757509860')
})

datetime_response = api_v1.model('DateTimeResponse', {
    'epoch': fields.Integer(description='Epoch timestamp', example=1757509860),
    'datetime': fields.String(description='Human readable datetime', example='Wed 2025-09-10 13:11:00'),
    'input': fields.String(description='Original input', example='2025-09-10-131100')
})

error_response = api_v1.model('ErrorResponse', {
    'message': fields.String(description='Error message', example='Invalid datetime format')
})

# JSON API endpoints
@api_v1.route('/epoch/<int:epoch_time>')
class EpochToDateTime(Resource):
    @api_v1.doc('epoch_to_datetime', description='Convert epoch time to human readable datetime')
    @api_v1.marshal_with(epoch_response)
    def get(self, epoch_time):
        """Convert epoch time to human readable datetime"""
        try:
            human_time = epoch_to_human(epoch_time)
            return {
                'epoch': epoch_time,
                'datetime': human_time,
                'input': str(epoch_time)
            }
        except Exception as e:
            api.abort(400, message=str(e))

@api_v1.route('/datetime/<string:datetime_str>')
class DateTimeToEpoch(Resource):
    @api_v1.doc('datetime_to_epoch', description='Convert human readable datetime to epoch time')
    @api_v1.marshal_with(datetime_response)
    def get(self, datetime_str):
        """Convert human readable datetime to epoch time"""
        try:
            epoch_time = human_to_epoch(datetime_str)
            return {
                'epoch': epoch_time,
                'datetime': datetime_str,  # Return original input format
                'input': datetime_str
            }
        except Exception as e:
            api.abort(400, message=str(e))

# Curl-friendly API endpoints (plain text) - direct routes for proper functionality
@app.route('/curl/v1/epoch/<int:epoch_time>')
def curl_epoch_to_datetime(epoch_time):
    """Convert epoch time to human readable datetime (plain text)"""
    try:
        human_time = epoch_to_human(epoch_time)
        return f"Epoch:     {epoch_time}\nDatetime:  {human_time}\nInput:     {epoch_time}\n\n"
    except Exception as e:
        return f"Error: {str(e)}\n\n", 400

@app.route('/curl/v1/datetime/<string:datetime_str>')
def curl_datetime_to_epoch(datetime_str):
    """Convert human readable datetime to epoch time (plain text)"""
    try:
        epoch_time = human_to_epoch(datetime_str)
        return f"Epoch:     {epoch_time}\nDatetime:  {datetime_str}\nInput:     {datetime_str}\n\n"
    except Exception as e:
        return f"Error: {str(e)}\n\n", 400

@app.route("/api/docs/")
def swagger_ui():
    """Custom Swagger UI with snazzy styling"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rantoo Epoch Converter API</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
        <link rel="stylesheet" type="text/css" href="/static/swagger-ui.css" />
        <style>
            html {{
                box-sizing: border-box;
                overflow: -moz-scrollbars-vertical;
                overflow-y: scroll;
            }}
            *, *:before, *:after {{
                box-sizing: inherit;
            }}
            body {{
                margin:0;
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 25%, #8e44ad 75%, #9b59b6 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
        <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
        <script>
            window.onload = function() {{
                // Custom Swagger spec that includes both JSON and CURL endpoints
                const customSpec = {{
                    "swagger": "2.0",
                    "info": {{
                        "title": "Rantoo Epoch Converter API",
                        "version": "1.0",
                        "description": "API for converting between epoch time and human-readable datetime"
                    }},
                    "basePath": "/",
                    "tags": [
                        {{"name": "v1", "description": "JSON API endpoints (v1)"}},
                        {{"name": "curl/v1", "description": "CURL endpoints (v1)"}}
                    ],
                    "paths": {{
                        "/v1/epoch/{{epoch_time}}": {{
                            "get": {{
                                "tags": ["v1"],
                                "summary": "Convert epoch time to human readable datetime",
                                "description": "Convert epoch time to human readable datetime",
                                "parameters": [
                                    {{
                                        "name": "epoch_time",
                                        "in": "path",
                                        "required": true,
                                        "type": "integer",
                                        "description": "Epoch timestamp"
                                    }}
                                ],
                                "responses": {{
                                    "200": {{
                                        "description": "Success",
                                        "schema": {{
                                            "type": "object",
                                            "properties": {{
                                                "epoch": {{"type": "integer", "example": 1757509860}},
                                                "datetime": {{"type": "string", "example": "Wed 2025-09-10 13:11:00"}},
                                                "input": {{"type": "string", "example": "1757509860"}}
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                        }},
                        "/v1/datetime/{{datetime_str}}": {{
                            "get": {{
                                "tags": ["v1"],
                                "summary": "Convert human readable datetime to epoch time",
                                "description": "Convert human readable datetime to epoch time",
                                "parameters": [
                                    {{
                                        "name": "datetime_str",
                                        "in": "path",
                                        "required": true,
                                        "type": "string",
                                        "description": "Datetime string in various formats"
                                    }}
                                ],
                                "responses": {{
                                    "200": {{
                                        "description": "Success",
                                        "schema": {{
                                            "type": "object",
                                            "properties": {{
                                                "epoch": {{"type": "integer", "example": 1757509860}},
                                                "datetime": {{"type": "string", "example": "Wed 2025-09-10 13:11:00"}},
                                                "input": {{"type": "string", "example": "2025-09-10-131100"}}
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                        }},
                        "/curl/v1/epoch/{{epoch_time}}": {{
                            "get": {{
                                "tags": ["curl/v1"],
                                "summary": "Convert epoch time to human readable datetime (plain text)",
                                "description": "Convert epoch time to human readable datetime (plain text)",
                                "parameters": [
                                    {{
                                        "name": "epoch_time",
                                        "in": "path",
                                        "required": true,
                                        "type": "integer",
                                        "description": "Epoch timestamp"
                                    }}
                                ],
                                "responses": {{
                                    "200": {{
                                        "description": "Success",
                                        "schema": {{
                                            "type": "string",
                                            "example": "Epoch:     1757509860\\nDatetime:  Wed 2025-09-10 13:11:00\\nInput:     1757509860\\n\\n"
                                        }}
                                    }}
                                }}
                            }}
                        }},
                        "/curl/v1/datetime/{{datetime_str}}": {{
                            "get": {{
                                "tags": ["curl/v1"],
                                "summary": "Convert human readable datetime to epoch time (plain text)",
                                "description": "Convert human readable datetime to epoch time (plain text)",
                                "parameters": [
                                    {{
                                        "name": "datetime_str",
                                        "in": "path",
                                        "required": true,
                                        "type": "string",
                                        "description": "Datetime string in various formats"
                                    }}
                                ],
                                "responses": {{
                                    "200": {{
                                        "description": "Success",
                                        "schema": {{
                                            "type": "string",
                                            "example": "Epoch:     1757509860\\nDatetime:  2025-09-10-131100\\nInput:     2025-09-10-131100\\n\\n"
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                }};
                
                const ui = SwaggerUIBundle({{
                    spec: customSpec,
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    plugins: [
                        SwaggerUIBundle.plugins.DownloadUrl
                    ],
                    layout: "StandaloneLayout",
                    tryItOutEnabled: true,
                    requestInterceptor: (req) => {{
                        console.log('API Request:', req);
                        return req;
                    }},
                    responseInterceptor: (res) => {{
                        console.log('API Response:', res);
                        return res;
                    }}
                }});
            }};
        </script>
    </body>
    </html>
    """

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

if __name__ == "__main__":
    import os
    # Use environment variable for port, default to 33081 for production
    port = int(os.environ.get('PORT', 33081))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host="127.0.0.1", port=port, debug=debug)