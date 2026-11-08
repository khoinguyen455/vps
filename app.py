import os
import re
import subprocess
import time
from fastapi import FastAPI

app = FastAPI()

SSHX_LOG = "/tmp/sshx.log"
sshx_proc = None

def run_sshx_command():
    global sshx_proc
    if sshx_proc is None or sshx_proc.poll() is not None:
        env = os.environ.copy()
        env["HOME"] = "/tmp"
        env["TMPDIR"] = "/tmp"
        
        log_file = open(SSHX_LOG, "w")
        # Chạy trực tiếp câu lệnh shell bạn yêu cầu
        sshx_proc = subprocess.Popen(
            "curl -sSf https://sshx.io/get | sh -s run",
            shell=True,
            executable="/bin/sh",
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT
        )

@app.get("/")
def home():
    run_sshx_command()
    
    # Chờ tối đa 8 giây để script tải xong và in ra link sshx
    for _ in range(16):
        if os.path.exists(SSHX_LOG):
            with open(SSHX_LOG, "r") as f:
                content = f.read()
                match = re.search(r"https://sshx\.io/s/[a-zA-Z0-9#_-]+", content)
                if match:
                    return {
                        "status": "Đã mở terminal thành công",
                        "sshx_url": match.group(0)
                    }
        time.sleep(0.5)

    # Nếu quá 8 giây chưa thấy link, trả về log thực tế để kiểm tra
    raw_log = open(SSHX_LOG).read() if os.path.exists(SSHX_LOG) else "Không có log"
    return {
        "status": "Đang tải hoặc gặp lỗi",
        "exit_code": sshx_proc.poll(),
        "log": raw_log
    }
