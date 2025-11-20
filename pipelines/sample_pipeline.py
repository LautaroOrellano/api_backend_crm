# pipelines/sample_pipeline.py
from ingestion.manual_ingestor import ingest_manual

def run_sample():
    sample = {
        "full_name": "Test Customer",
        "email": "test@example.com",
        "phone": "+541133445566",
        "source": "script",
        "notes": "pipeline test"
    }
    new_id = ingest_manual(sample)
    print("Inserted id:", new_id)

if __name__ == "__main__":
    run_sample()
