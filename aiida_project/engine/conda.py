import json
import os
import subprocess

import py  # type: ignore

from aiida_project.engine.base import BaseEngine


class CondaEngine(BaseEngine):
    def __init__(self, project_path):
        super().__init__(project_path)
        self.conda_info = json.loads(
            subprocess.check_output(["conda", "info", "-a", "--json"])
        )

    @property
    def conda_path(self):
        return py.path.local(self.conda_info["conda_prefix"])

    @property
    def venv_path(self):
        for path in self.conda_info["envs_dirs"]:
            env_collection_path = py.path.local(path)
            env_path = env_collection_path.join(self.venv_name)
            if env_path.exists():
                return env_path
        return None

    def create(self, name, python=None):
        self._venv_name = name
        if not self.venv_path:
            conda_command = ["conda", "create", "-y", "-n", name, "python=2"]
            subprocess.check_call(conda_command)

    def add_activate_script(self, path):
        activate_d_path = self.venv_path.join("etc", "conda", "activate.d")
        activate_d_path.ensure_dir()
        os.symlink(path.strpath, activate_d_path.join(path.basename).strpath)

    def add_deactivate_scritp(self, path):
        deactivate_d_path = self.venv_path.join("etc", "conda", "deactivate.d")
        deactivate_d_path.ensure_dir()
        os.symlink(path.strpath, deactivate_d_path.join(path.basename).strpath)
