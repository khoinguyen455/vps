import subprocess
import sys
import urllib.request
import os

def setup_pip():
    """Kiểm tra và tự động cài đặt pip nếu hệ thống chưa có."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("-> Đã có sẵn pip.")
    except subprocess.CalledProcessError:
        print("-> Chưa có pip. Đang tiến hành cài đặt...")
        try:
            subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True)
            print("-> Cài đặt pip thành công qua ensurepip.")
        except Exception:
            print("-> Đang tải get-pip.py để cài đặt...")
            urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", "get-pip.py")
            subprocess.run([sys.executable, "get-pip.py"], check=True)
            os.remove("get-pip.py")
            print("-> Cài đặt pip thành công.")

def install_and_run_jupyter():
    setup_pip()
    
    print("-> Đang cài đặt JupyterLab (vui lòng đợi)...")
    # Thêm --break-system-packages để tránh lỗi trên các bản Linux/Arch mới (PEP 668)
    install_cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "jupyterlab"]
    try:
        subprocess.run(install_cmd, check=True)
    except subprocess.CalledProcessError:
        subprocess.run(install_cmd + ["--break-system-packages"], check=True)

    print("-> Đang khởi chạy ngầm JupyterLab ở cổng 8080...")
    run_cmd = [
        sys.executable, "-m", "jupyter", "lab",
        "--ip=0.0.0.0",
        "--port=8080",
        "--no-browser",
        "--allow-root",
        "--ServerApp.allow_origin=*",
        "--ServerApp.token=",
        "--ServerApp.password=",
        "--ServerApp.disable_check_xsrf=True"
    ]

    with open("jupyter.log", "w") as log_file:
        process = subprocess.Popen(
            run_cmd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
    print(f"-> Hoàn tất! JupyterLab đang chạy ngầm (PID: {process.pid}). Log lưu tại jupyter.log")

if __name__ == "__main__":
    install_and_run_jupyter()
