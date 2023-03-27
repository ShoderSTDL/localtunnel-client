from modules.shared import cmd_opts
from modules import scripts
import subprocess
import re
import json
import os

def is_valid_url(url):
    p= re.compile(r'^https?://([\w\-]+(\.[\w\-]+)*|localhost)(:\d+)?(/[^\s\\]*)?$')
    return p.match(url) != None

if cmd_opts.localtunnel:
    port = cmd_opts.port if cmd_opts.port is not None else 7860
    host = cmd_opts.localtunnel_host if cmd_opts.localtunnel_host is not None else "https://localtunnel.me"

    if is_valid_url(host) is False:
        raise ValueError("Invalid URL format for localtunnel host")

    nodejs = os.path.join(scripts.basedir(),"localtunnel.js")

    argv = ["node", nodejs, "--port", str(port), "--host", host]
    process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()

    if process.returncode is not None and process.returncode == 0:
        data = stdout.decode("utf-8")
        json_string = re.search(r'\{.*\}', data).group()

        output_dict = json.loads(json_string)
        pid = output_dict["pid"]
        version = output_dict["version"]
        connected_url = output_dict["url"]

        print(f"localtunnel-{version}")
        print(f"localtunnel connected to {host}")
        print(f"localtunnel is running at {connected_url}")
    else:
        process.terminate()
        error_message = stderr.decode().strip()
        print("Failed to start localtunnel")
        raise RuntimeError(error_message)