from modules.shared import cmd_opts
import subprocess
import re
import time
import select

def is_valid_url(url):
    p= re.compile(r'^https?://[\w\-]+(\.[\w\-]+)+(:\d+)?(/[\w\-./?%&=]*)?$')
    return p.match(url) != None

if cmd_opts.localtunnel:
    timeout = 5
    track_text = "your url is"
    port = cmd_opts.port if cmd_opts.port is not None else 7860
    host = cmd_opts.localtunnel_host if cmd_opts.localtunnel_host is not None else "https://localtunnel.me"

    if is_valid_url(host) is False:
        raise ValueError("Invalid URL format for localtunnel host")

    argv = ["npx","localtunnel","--port", str(port), "--host", host]
    process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    start_time = time.monotonic()
    while True:
        ready, _, _ = select.select([process.stdout], [], [], timeout)
        if not ready:
            process.terminate()
            raise TimeoutError(f"localtunnel failed to connect to {host}")

        output = process.stdout.readline().decode().strip()
        if track_text in output:
            connected_url = output.split("your url is: ")[-1].strip()
            print(f"localtunnel connected to {host}")
            print(f"localtunnel is running at {connected_url}")
            break

    if process.returncode is not None:
        if process.returncode != 0:
            process.terminate()
            raise RuntimeError(f"Failed to start localtunnel: {process.stderr.readline().decode()}")
        else:
            process.terminate()
            raise RuntimeError(f"localtunnel process has been terminated")