import json
import os
import shutil
import subprocess
import tempfile
import uuid

import hcs_cli.cmds.dev.util.log as log
from hcs_cli.cmds.dev.util.log import fail
from hcs_cli.support.exec_util import exec


def check_ssh_access():
    print("🔐 Checking SSH access to GitHub...")
    result = subprocess.run(["ssh", "-T", "git@github.com"], capture_output=True, text=True)
    cmd = "ssh -T git@github.com"
    exec(cmd, log_error=False, raise_on_error=False, inherit_output=True).stdout
    if result.returncode != 1 and result.returncode != 0:
        fail(
            "SSH access to GitHub failed. Please follow instructions at https://docs.github.com/en/authentication/connecting-to-github-with-ssh before proceeding."
        )
    log.good("SSH access confirmed.")


class _RepoReader:
    def __init__(self, git_url: str):
        # url = "https://github.com/euc-eng/horizonv2-sg.nightly-tests.git"
        # url =     "git@github.com:euc-eng/horizonv2-sg.nightly-tests.git"
        if git_url.startswith("https://github.com/"):
            git_url = "git@github.com:" + git_url[len("https://github.com/") :]
        self.git_url = git_url
        self.temp_dir = None

    def __enter__(self):
        # Generate a unique temporary directory name (but don't create it)
        unique_id = str(uuid.uuid4())[:8]
        self.temp_dir = os.path.join(tempfile.gettempdir(), f"repo_reader_{unique_id}")
        cmd = f"git clone --filter=blob:none --no-checkout --depth=1 {self.git_url} {self.temp_dir}"
        exec(cmd, log_error=True, raise_on_error=False, inherit_output=True).stdout

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def get(self, file_path: str, branch: str = "master", format: str = "auto"):
        # Use git show to get file content without needing to checkout
        cmd = f"git show {branch}:{file_path}"
        result = exec(cmd, log_error=True, raise_on_error=False, inherit_output=False, cwd=self.temp_dir)

        if result.returncode != 0:
            raise FileNotFoundError(f"File {file_path} not found in branch {branch}")

        content = result.stdout

        if format == "auto":
            if file_path.endswith(".json"):
                format = "json"
            elif file_path.endswith(".properties"):
                format = "properties"
            else:
                format = "text"

        if format == "json":
            return json.loads(content)
        elif format == "properties":
            props = {}
            for line in content.split("\n"):
                line = line.strip()
                if "=" in line:
                    key, value = line.split("=", 1)
                    props[key.strip()] = value.strip()
            return props
        elif format == "text":
            return content
        else:
            raise ValueError(f"Unsupported format: {format}")


def repo(git_url: str) -> _RepoReader:
    return _RepoReader(git_url)
