# datasourcelib

Minimal package scaffold for sync strategies (full, incremental, time-range, daily, on-demand).
Run API:
pip install -e .
uvicorn datasourcelib.api.routes:app --reload