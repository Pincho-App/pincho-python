"""Flask integration example for WirePusher SDK.

This example shows how to integrate WirePusher notifications into a Flask application.

Install Flask first: pip install flask
"""

import os
from flask import Flask, jsonify, request
from wirepusher import WirePusher
from wirepusher.exceptions import WirePusherError

app = Flask(__name__)

# Get credentials from environment variables
TOKEN = os.getenv("WIREPUSHER_TOKEN", "wpt_your_token_here")
USER_ID = os.getenv("WIREPUSHER_USER_ID", "your_user_id_here")


@app.route("/")
def index():
    """Root endpoint."""
    return jsonify({
        "service": "WirePusher Flask Example",
        "endpoints": {
            "/notify": "POST - Send a notification",
            "/deploy": "POST - Simulate deployment with notification"
        }
    })


@app.route("/notify", methods=["POST"])
def notify():
    """Send a custom notification.

    Request body:
    {
        "title": "Notification Title",
        "message": "Notification message",
        "type": "optional-type",
        "tags": ["tag1", "tag2"]
    }
    """
    data = request.get_json()

    if not data or "title" not in data or "message" not in data:
        return jsonify({"error": "Missing required fields: title and message"}), 400

    try:
        with WirePusher(token=TOKEN, user_id=USER_ID) as client:
            response = client.send(
                title=data["title"],
                message=data["message"],
                type=data.get("type"),
                tags=data.get("tags"),
            )

        return jsonify({
            "success": True,
            "status": response.status,
            "message": response.message
        })

    except WirePusherError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/deploy", methods=["POST"])
def deploy():
    """Simulate a deployment process with notifications.

    Request body:
    {
        "version": "v1.2.3",
        "environment": "production"
    }
    """
    data = request.get_json() or {}
    version = data.get("version", "unknown")
    environment = data.get("environment", "staging")

    try:
        with WirePusher(token=TOKEN, user_id=USER_ID) as client:
            # Deployment started notification
            client.send(
                title="Deployment Started",
                message=f"Deploying {version} to {environment}",
                type="deployment",
                tags=["deploy", environment, "started"],
            )

            # Simulate deployment (in reality, this would be your actual deployment logic)
            # For now, we'll just send a success notification
            client.send(
                title="Deployment Complete",
                message=f"{version} successfully deployed to {environment}",
                type="deployment",
                tags=["deploy", environment, "success"],
            )

        return jsonify({
            "success": True,
            "version": version,
            "environment": environment,
            "status": "deployed"
        })

    except WirePusherError as e:
        # Send failure notification
        try:
            with WirePusher(token=TOKEN, user_id=USER_ID) as client:
                client.send(
                    title="Deployment Failed",
                    message=f"Failed to deploy {version}: {str(e)}",
                    type="deployment",
                    tags=["deploy", environment, "failed"],
                )
        except Exception:
            pass  # Don't fail if failure notification fails

        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Starting Flask server...")
    print("Try these curl commands:")
    print()
    print('curl -X POST http://localhost:5000/notify \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"title":"Test","message":"Hello from Flask!"}\'')
    print()
    print('curl -X POST http://localhost:5000/deploy \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"version":"v1.2.3","environment":"production"}\'')
    print()

    app.run(debug=True, port=5000)
