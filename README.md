# Lyftr-Backend-Assignment---Dikshant-Grover
HMAC-Verified Message ServiceA high-performance FastAPI service designed to ingest, validate, and store incoming webhooks. This project features secure HMAC-SHA256 signature verification to ensure data integrity and authenticity.

FeaturesSecure Webhooks: Mandatory HMAC-SHA256 signature validation.
Persistent Storage: Automatic SQLite database management with Docker volume mapping.
Health & Monitoring: Built-in endpoints for readiness checks and message metrics.
Structured Logging: JSON-formatted logs for better observability in production.

 Tech StackLanguage:
 Python 3.12.5Framework: 
 FastAPI (Asynchronous API)
 Database: SQLite (Local persistent storage)
 Containerization: Docker & Docker ComposeTesting: Pytest & HTTPX
 
 Initial SetupClone and Navigate:PowerShell cd C:\Users\grove\Downloads\App
Environment Configuration:Create a .env file in the root directory:Ini, TOMLWEBHOOK_SECRET=your_secret_key_here
DATABASE_URL=sqlite:///./data/messages.db
LOG_LEVEL=INFO

 How to Run
A: Using Docker This handles all dependencies and database paths automatically.
PowerShellmake up or
docker compose up -d --build
Access the API at http://localhost:8000Option 

B: Local DevelopmentInstall Dependencies:PowerShellpip install -r requirements.txt
Start Server:PowerShell$env:PYTHONPATH="."
uvicorn main:app --reload

 Testing & ValidationRun the automated test suite to verify security and endpoint logic: 
 PowerShell : # Run locally
$env:PYTHONPATH="."
pytest

# Run inside Docker
make test
API EndpointsEndpointMethodDescription/webhookPOSTReceive message (Requires X-Signature)/messagesGETRetrieve stored messages/metricsGETView message statistics/health/readyGETSystem readiness check
