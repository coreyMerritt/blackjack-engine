python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0

