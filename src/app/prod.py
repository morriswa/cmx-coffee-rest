# Production Deployment Settings

from app.settings import *

from socket import gethostbyname, gethostname

# Add env specific settings
RUNTIME_ENVIRONMENT = "prod"
DEBUG = False

# Step 5.1)
# Security Setup
CORS_EXPOSE_HEADERS = ["authorization", "content-type", "content-length"]
CORS_ALLOW_HEADERS = CORS_EXPOSE_HEADERS
CORS_ALLOWED_ORIGINS = [
    'https://www.morriswa.org',
    'http://localhost:4200',
    'http://localhost:3000',
]
ALLOWED_HOSTS = [
    'www.morriswa.org',
    gethostbyname(gethostname())
]
CORS_ALLOW_METHODS = (
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
)
