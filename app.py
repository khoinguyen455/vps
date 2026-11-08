import os
import re
import stat
import subprocess
import tarfile
import time
import urllib.request
from fastapi import FastAPI

app = FastAPI()

SSHX_BIN = "/tmp/sshx"
SSHX_LOG = "/tmp/sshx.log"
sshx_proc = None

def start_sshx():
    global sshx_proc
    # 1. Dùng trực tiếp thư viện chuẩn Python để tải và giải nén vào /tmp
    if not os.path.exists(SSHX_BIN):
        url = "https://amazonaws.com"
        tar_path = "/tmp/sshx.tar.gz"
        urllib.request.urlretrieve(url, tar_path)
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall("/tmp")
        os.chmod(SSHX_BIN, os.stat(SSHX_BIN).st_mode | stat.S_IEXEC)

    # 2. Chạy file thực thi sshx
    if sshx_proc is None or sshx_proc.poll() is not None:
        env = os.environ.copy()
        env["HOME"] = "/tmp"
        log_file = open(SSHX_LOG, "w")
        sshx_proc = subprocess.Popen(
            [SSHX_BIN],
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT
        )

@app.get("/")
def home():
    start_sshx()
    
    # Đợi tối đa 8 giây để lấy đường link terminal
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

    raw_log = open(SSHX_LOG).read() if os.path.exists(SSHX_LOG) else "Không có log"
    return {
        "status": "Đang tải hoặc gặp lỗi",
        "exit_code": sshx_proc.poll(),
        "log": raw_log
    }
@app.get("/whoami")
def check_whoami():
    try:
        user = subprocess.check_output(["whoami"], text=True).strip()
        uid_info = subprocess.check_output(["id"], text=True).strip()
        os_info = subprocess.check_output(["uname", "-a"], text=True).strip()
        return {
            "whoami": user,
            "id": uid_info,
            "os": os_info,
            "cwd": os.getcwd(),
            "can_write_root": os.access("/", os.W_OK),
            "can_write_tmp": os.access("/tmp", os.W_OK)
        }
    except Exception as e:
        return {"error": str(e)}

