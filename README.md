python3.12 -m venv .venv
source .venv/bin/activate
pip install fastapi[standard]
uvicorn app.app:app --host 0.0.0.0 --port 8000
