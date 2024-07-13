#!/usr/bin/env python3
"""API Route configuration.
"""
from os import getenv
from flask import Flask, jsonify, request
from api.v1.views import app_views
from models import storage
from flask_cors import CORS
from api.v1.auth.session_db_auth import SessionDBAuth

app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

auth = None
auth_type = getenv('AUTH_TYPE')

if auth_type == "session_db_auth":
    auth = SessionDBAuth()

@app.before_request
def before_request():
    """Filter each request through authentication."""
    if auth is None:
        pass
    elif not auth.require_auth(request.path, ['/api/v1/status/',
                                              '/api/v1/unauthorized/',
                                              '/api/v1/forbidden/',
                                              '/api/v1/auth_session/login/']):
        pass
    elif not auth.authorization_header(request) and \
            not auth.session_cookie(request):
        return jsonify({"error": "Unauthorized"}), 401
    elif not auth.current_user(request):
        return jsonify({"error": "Forbidden"}), 403

@app.teardown_appcontext
def teardown_db(exception):
    """Close storage on teardown."""
    storage.close()

@app.errorhandler(404)
def not_found(error):
    """Handles 404 errors."""
    return jsonify({"error": "Not found"}), 404

if __name__ == "__main__":
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    app.run(host=host, port=int(port))
