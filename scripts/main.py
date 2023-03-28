from modules.shared import cmd_opts
from modules import scripts
import subprocess
import re
import json
import os
import shutil
import sys
import launch

def install():
    node_version = "14.21.3"
    node_executable = "node"
    node_path = shutil.which(node_executable)
    npm_executable = "npm"
    npm_path = shutil.which(npm_executable)

    if node_path is None:
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            if not launch.is_installed("nodeenv"):
                launch.run_pip("install nodeenv", "requirements for localtunnel")

            cmd = ["nodeenv", "-p", "-n", node_version]
            subprocess.run(cmd)

            node_cmd = os.path.join(sys.prefix, "bin", "node")
            node_version_cmd = [node_cmd, "-v"]
            result = subprocess.run(node_version_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode != 0:
                raise RuntimeError(f"Failed to install Node.js v{node_version}")

        else:
            print("To use localtunnel, Node.js version 14 or higher must be installed")

    if npm_path is not None:
        file_dir = scripts.basedir()
        try:
            subprocess.run('npx pnpm@7.30.5 install', shell=True, check=True, cwd=file_dir)
        except subprocess.CalledProcessError as e:
            raise (f'Error: An error occurred while installing the module.',e)


def is_valid_url(url):
    p= re.compile(r'^https?://([\w\-]+(\.[\w\-]+)*|localhost)(:\d+)?(/[^\s\\]*)?$')
    return p.match(url) != None

if cmd_opts.localtunnel:
    install()
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