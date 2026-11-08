import os
import subprocess
import sys
import httpx
from fastapi import FastAPI, Request, Response

app = FastAPI()

# Khởi chạy ngầm JupyterLab ở cổng nội bộ 8888 nếu chưa chạy
subprocess.Popen(
    [
        sys.executable, "-m", "jupyter", "lab",
        "--ip=127.0.0.1",
        "--port=8888",
        "--no-browser",
        "--allow-root",
        "--ServerApp.allow_origin=*",
        "--ServerApp.token=",
        "--ServerApp.password=",
        "--ServerApp.disable_check_xsrf=True"
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

# Chuyển tiếp (Proxy) toàn bộ HTTP request vào JupyterLab
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy_jupyter(request: Request, path: str):
    url = f"http://127.0.0{path}"
    if request.query_params:
        url += f"?{request.query_params}"

    async with httpx.AsyncClient() as client:
        try:
            body = await request.body()
            headers = dict(request.headers)
            headers.pop("host", None)

            resp = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                timeout=30.0
            )
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=dict(resp.headers)
            )
        except Exception as e:
            return {"status": "JupyterLab đang khởi động, vui lòng F5 lại sau 5 giây...", "error": str(e)}
