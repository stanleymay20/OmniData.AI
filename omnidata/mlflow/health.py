"""
Health check endpoint for MLflow
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Health check endpoint for MLflow."""
    return jsonify({
        "status": "healthy",
        "service": "mlflow",
        "version": "2.0.0"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 