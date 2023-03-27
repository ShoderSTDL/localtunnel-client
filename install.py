from modules import scripts
import launch
import shutil
import sys
import subprocess
import os

node_version = "14.21.3"
node_executable = "node"
node_path = shutil.which(node_executable)

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

npm_executable = "npm"
npm_path = shutil.which(npm_executable)

if npm_path is not None:
    file_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    try:
        subprocess.run('npx pnpm install', shell=True, check=True, cwd=file_dir)
    except subprocess.CalledProcessError as e:
        raise (f'Error: An error occurred while installing the module.',e)