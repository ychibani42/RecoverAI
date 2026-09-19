import os

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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


async def _proxy(url: str, request: Request) -> Response:
    body = await request.body()
    try:
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
    except httpx.HTTPError:
        return JSONResponse(
            status_code=503,
            content={"detail": "ai service unavailable"},
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


@app.api_route("/cases/{path:path}", methods=["GET", "POST"])
async def proxy_cases(path: str, request: Request) -> Response:
    """Forwards clinical case requests to the ai service."""
    return await _proxy(f"{AI_SERVICE_URL}/cases/{path}", request)


@app.api_route("/patients", methods=["GET"])
async def proxy_patients(request: Request) -> Response:
    """Forwards the historical patients dataset request to the ai service."""
    return await _proxy(f"{AI_SERVICE_URL}/patients", request)


@app.api_route("/images/{path:path}", methods=["GET"])
async def proxy_images(path: str, request: Request) -> Response:
    """Forwards x-ray image requests to the ai service's static file mount."""
    return await _proxy(f"{AI_SERVICE_URL}/images/{path}", request)


def run(host: str = "127.0.0.1", port: int = 8000):
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run()
