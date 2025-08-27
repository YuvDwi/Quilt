GITHUB_APP_ID = "your_app_id_here"
PRIVATE_KEY_PATH = "path/to/your/private-key.pem"
INSTALLATION_ID = "your_installation_id_here"

GITHUB_APP_NAME = "Your App Name"
GITHUB_APP_DESCRIPTION = "Description of what your app does"

WEBHOOK_SECRET = "your_webhook_secret_here"
WEBHOOK_URL = "https://your-domain.com/webhook"

REQUIRED_PERMISSIONS = {
    "issues": "write",
    "contents": "write",
    "pull_requests": "write",
    "metadata": "read"
}

SUBSCRIBE_TO_EVENTS = [
    "issues",
    "pull_request",
    "push",
    "create",
    "delete"
]
