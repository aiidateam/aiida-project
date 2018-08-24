import subprocess
import click
import py

from aiida_project.commands.main import main
from aiida_project.engine import get_engine


EMPTY_CONFIG = """{
    "profiles": {}
}"""

ACTIVATE_AIIDA_SH = """cd {path}
export AIIDA_PATH={path}

if test -x "$(command -v verdi)"
then
    eval "$(_VERDI_COMPLETE=source-bash verdi)"
    verdi profile list &> /dev/null && verdi daemon start
fi
"""

DEACTIVATE_AIIDA_SH = 'unset AIIDA_PATH'


def clone_pypackage(project_path, repo, branch=None):
    clone_command = ['git', 'clone', '--single-branch']
    if branch:
        clone_command.extend(['-b', branch])
    clone_command.append('https://github.com/{}'.format(repo))
    subprocess.call(clone_command, cwd=project_path.strpath)


@main.command()
@click.argument('name')
@click.option('--engine', default='virtualenv', type=click.Choice(['virtualenv', 'wrapper', 'conda']), help='virtualenv engine')
@click.option('--core-branch', 'branch')
@click.option('--plugin', 'plugins', multiple=True, help='plugin specifier <github_user>/<repo>:<branch>')
@click.option('--python', type=click.Path(file_okay=True, exists=True, dir_okay=False))
def create(name, engine, branch, plugins, python):
    """Create a new AiiDA project named NAME."""
    current_dir = py.path.local('.')
    project_path = current_dir.join(name)

    project_path.ensure_dir()
    config_path = project_path.join('.aiida')
    config_path.ensure_dir()
    config_file = config_path.join('config.json')
    config_file.write(EMPTY_CONFIG)

    activate_script = project_path.join('activate_aiida.sh')
    activate_script.write(ACTIVATE_AIIDA_SH.format(path=project_path.strpath))

    deactivate_script = project_path.join('deactivate_aiida.sh')
    deactivate_script.write(DEACTIVATE_AIIDA_SH)

    venv = get_engine(engine, project_path)
    venv.create('aiida-{}'.format(name), python=python)

    clone_pypackage(project_path, 'aiidateam/aiida_core', branch=branch)
    venv.install(project_path.join('aiida_core'))

    for plugin in plugins:
        repo_branch = plugin.split(':')
        repo = repo_branch[0]
        branch = repo_branch[1] if len(repo_branch) > 1 else None
        clone_pypackage(project_path, repo, branch=branch)
        venv.install(project_path.join(repo.split('/')[1]))

    venv.add_activate_script(activate_script)
    venv.add_deactivate_script(deactivate_script)
