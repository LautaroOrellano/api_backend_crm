# main.py
from pipelines.sample_pipeline import run_sample
from db import connection as db_conn

if __name__ == "__main__":
    db_conn.init_pool()
    run_sample()