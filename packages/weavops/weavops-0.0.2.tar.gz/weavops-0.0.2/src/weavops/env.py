import os

HOST = os.getenv("WEAVOPS_HOST", "0.0.0.0")

PORT = int(os.getenv("WEAVOPS_PORT", "8000"))
