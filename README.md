# FastAPI Setup Guide

## 1. Create a virtual environment
```bash
python3.12 -m venv .venv
```
## 2. Activate the virtual environment
```bash
source .venv/bin/activate
```

## 3. Install FastAPI
```bash
pip install fastapi[standard]
```
## 4. Run FastApi App
```bash
uvicorn app.app:app --host 0.0.0.0 --port 8000

```
