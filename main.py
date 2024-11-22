from fastapi import FastAPI
from datetime import datetime

app = FastAPI()


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# For local testing
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
