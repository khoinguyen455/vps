import os
import subprocess

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
