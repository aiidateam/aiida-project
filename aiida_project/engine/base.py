import subprocess


class BaseEngine(object):

    def __init__(self, project_path):
        self.project_path = project_path
        self._venv_path = None
        self._venv_name = None

    @property
    def venv_path(self):
        return self._venv_path

    @property
    def venv_name(self):
        return self._venv_name

    def create(self, name, python=None):
        pass

    def install(self, path):
        install_command = []
        install_command.append((self.venv_path.join('bin', 'pip').strpath))
        install_command.extend(['install', '-e', path.strpath])
        subprocess.check_call(install_command, cwd=self.project_path.strpath)

    def add_activate_script(self, path):
        pass

    def add_deactivate_script(self, path):
        pass

