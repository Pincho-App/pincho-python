"""Flask webhook example for Pincho.

This example demonstrates how to send notifications from a Flask web application
in response to webhook events (deployments, alerts, CI/CD events, etc.).

Requirements:
    pip install flask pincho

Usage:
    1. Set your token: export PINCHO_TOKEN="your_token"
    2. Run: python3 flask_webhook.py
    3. Test with:
       curl -X POST http://localhost:5000/webhook \
            -H "Content-Type: application/json" \
            -d '{"event": "deploy", "message": "v1.2.3 deployed"}'
"""

import os
from threading import Thread

from flask import Flask, jsonify, request

from pincho import Pincho
from pincho.exceptions import PinchoError

app = Flask(__name__)


def send_notification_async(title: str, message: str, **kwargs):
    """Send notification in background thread (non-blocking)."""

    def _send():
        try:
            with Pincho() as client:
                client.send(title, message, **kwargs)
        except PinchoError as e:
            # Log error but don't fail the webhook
            app.logger.error(f"Failed to send notification: {e}")

    thread = Thread(target=_send)
    thread.start()


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    """Handle incoming webhook and send notification.

    Expected JSON body:
        {
            "event": "deploy",
            "message": "v1.2.3 deployed to production",
            "type": "deployment",  # optional
            "tags": ["production"]  # optional
        }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body required"}), 400

    event = data.get("event", "unknown")
    message = data.get("message", "No details provided")

    # Construct notification
    title = f"Webhook: {event}"
    notification_type = data.get("type", "webhook")
    tags = data.get("tags", [])

    # Send notification (non-blocking)
    send_notification_async(title, message, type=notification_type, tags=tags)

    return jsonify({"status": "notification_queued", "event": event})


@app.route("/deploy", methods=["POST"])
def handle_deploy():
    """Specific handler for deployment notifications.

    Expected JSON body:
        {
            "version": "1.2.3",
            "environment": "production",
            "service": "api-server"
        }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body required"}), 400

    version = data.get("version", "unknown")
    environment = data.get("environment", "unknown")
    service = data.get("service", "unknown")

    title = f"Deploy: {service}"
    message = f"Version {version} deployed to {environment}"
    tags = [environment, service, f"v{version}"]

    send_notification_async(title, message, type="deployment", tags=tags)

    return jsonify(
        {
            "status": "deploy_notification_sent",
            "version": version,
            "environment": environment,
            "service": service,
        }
    )


@app.route("/alert", methods=["POST"])
def handle_alert():
    """Handle system alerts.

    Expected JSON body:
        {
            "severity": "critical",
            "service": "database",
            "message": "High CPU usage detected"
        }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body required"}), 400

    severity = data.get("severity", "info")
    service = data.get("service", "unknown")
    message = data.get("message", "Alert triggered")

    title = f"Alert [{severity.upper()}]: {service}"
    tags = [severity, service, "alert"]

    send_notification_async(title, message, type="alert", tags=tags)

    return jsonify({"status": "alert_sent", "severity": severity, "service": service})


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    # Verify token is configured
    if not os.getenv("PINCHO_TOKEN"):
        return jsonify({"status": "unhealthy", "error": "PINCHO_TOKEN not set"}), 500

    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    # Verify token is set
    if not os.getenv("PINCHO_TOKEN"):
        print("Error: PINCHO_TOKEN environment variable not set")
        print("Set it with: export PINCHO_TOKEN='your_token'")
        exit(1)

    print("Starting Flask webhook server...")
    print("Test endpoints:")
    print("  POST /webhook  - Generic webhook handler")
    print("  POST /deploy   - Deployment notifications")
    print("  POST /alert    - System alerts")
    print("  GET  /health   - Health check")
    print("\nExample:")
    print("  curl -X POST http://localhost:5000/deploy \\")
    print('       -H "Content-Type: application/json" \\')
    print('       -d \'{"version": "1.2.3", "environment": "production", "service": "api"}\'')
    print("")

    app.run(host="0.0.0.0", port=5000, debug=True)
