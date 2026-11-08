import os
import subprocess
import sys
import time
import httpx
from fastapi import FastAPI, Request, Response

app = FastAPI()

# 1. Tìm đúng đường dẫn thư mục assets của JupyterLab trên Vercel
lab_dir = os.path.abspath("share/jupyter/lab")
if not os.path.exists(lab_dir):
    for p in sys.path:
        candidate = os.path.join(p, "share", "jupyter", "lab")
        if os.path.exists(candidate):
            lab_dir = candidate
            break

# 2. Cấu hình biến môi trường
env = os.environ.copy()
env["HOME"] = "/tmp"
env["JUPYTER_CONFIG_DIR"] = "/tmp/.jupyter"
env["JUPYTER_DATA_DIR"] = "/tmp/.local/share/jupyter"
env["JUPYTER_RUNTIME_DIR"] = "/tmp/.local/share/jupyter/runtime"
env["JUPYTERLAB_DIR"] = lab_dir  # <-- Trỏ đúng thư mục giao diện web

os.makedirs("/tmp/work", exist_ok=True)

os.makedirs("/tmp/work", exist_ok=True)

# 2. Khởi chạy JupyterLab và ghi log ra /tmp/jupyter.log để theo dõi
log_file = open("/tmp/jupyter.log", "w")
jupyter_proc = subprocess.Popen(
    [
        sys.executable, "-m", "jupyterlab",  # <-- Sửa từ "jupyter", "lab" thành "jupyterlab"
        "--ip=127.0.0.1",
        "--port=8888",
        "--no-browser",
        "--allow-root",
        "--notebook-dir=/tmp/work",
        "--ServerApp.allow_origin=*",
        "--ServerApp.token=",
        "--ServerApp.password=",
        "--ServerApp.disable_check_xsrf=True"
    ],
    env=env,
    stdout=log_file,
    stderr=subprocess.STDOUT
)


# 3. Chuyển tiếp (Proxy) toàn bộ HTTP request vào cổng 8888
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy_jupyter(request: Request, path: str):
    target_url = f"http://127.0.0.1:8888/{path}"
    if request.query_params:
        target_url += f"?{request.query_params}"

    # Đợi tối đa 5 giây để JupyterLab mở cổng 8888 trong lần đầu tiên
    if jupyter_proc.poll() is None:
        for _ in range(10):
            try:
                async with httpx.AsyncClient() as check_client:
                    await check_client.get("http://127.0.0", timeout=0.5)
                    break
            except Exception:
                time.sleep(0.5)

    async with httpx.AsyncClient() as client:
        try:
            body = await request.body()
            headers = dict(request.headers)
            headers.pop("host", None)

            resp = await client.request(
                method=request.method,
                url=target_url,
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
            log_content = ""
            if os.path.exists("/tmp/jupyter.log"):
                with open("/tmp/jupyter.log", "r") as f:
                    log_content = f.read()[-1000:]
            return {
                "status": "Không thể kết nối tới JupyterLab",
                "error": str(e),
                "process_exit_code": jupyter_proc.poll(),
                "jupyter_log": log_content
            }
