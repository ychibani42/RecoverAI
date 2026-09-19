import os

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

AI_SERVICE_URL = os.environ.get("AI_SERVICE_URL", "http://localhost:8001")

app = FastAPI(title="recovery-ia-backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.api_route("/cases/{path:path}", methods=["GET", "POST"])
async def proxy_cases(path: str, request: Request) -> Response:
    """Forwards clinical case requests to the ai service."""
    url = f"{AI_SERVICE_URL}/cases/{path}"
    body = await request.body()
    async with httpx.AsyncClient(timeout=60) as client:
        upstream = await client.request(
            request.method,
            url,
            params=request.query_params,
            content=body,
            headers={
                k: v
                for k, v in request.headers.items()
                if k.lower() not in {"host", "content-length"}
            },
        )
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers={
            k: v
            for k, v in upstream.headers.items()
            if k.lower() not in {"content-length", "transfer-encoding", "connection"}
        },
    )


def run(host: str = "127.0.0.1", port: int = 8000):
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run()
