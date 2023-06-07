# AiiDA-Project

Tool for managing AiiDA "projects" - Python environments tailored to AiiDA with separated project directories.

| ❗️ This package is still in the early stages of development and we will most likely break the API regularly in new 0.X versions. Be sure to pin the version when installing this package in scripts.|
|---|


## Installation

The package can be installed globally with `pipx`:

```console
pipx install aiida-project
```
```console
  installed package aiida-project 0.4.0, installed using Python 3.9.16
  These apps are now globally available
    - aiida-project
done! ✨ 🌟 ✨
```

See the [`pipx` installation instructions](https://pypa.github.io/pipx/installation/) if you haven't already installed `pipx`.

## Usage

After installing `aiida-project`, run the `init` command to get started:

```console
aiida-project init
```
```console
👋 Hello there! Which shell are you using? (zsh detected) [bash/zsh/fish]: zsh

✨🚀 AiiDA-project has been initialised! 🚀✨

Info: For the changes to take effect, run the following command:

    source /Users/mbercx/.zshrc

or simply open a new terminal.
```

This will also add the `cda` function to your shell startup file, so you can easily switch projects.
Note that you'll have to source your e.g. `.zshrc` file for this function to be accessible!

### `create`

After initialising, you can create new projects with their own virtual environment and project directory using the `create` command.
The latest version of `aiida-core` will also be installed automatically, along with any plugins you specify with the `--plugin` option:

```console
aiida-project create firstproject --plugin aiida-quantumespresso
```
```console
✨ Creating the project directory and environment using the Python binary:
   /opt/homebrew/Cellar/python@3.11/3.11.3/Frameworks/Python.framework/Versions/3.11/bin/python3.11
🔧 Adding the AiiDA environment variables to the activate script.
✅ Success: Project created.
💾 Installing the latest release of the AiiDA core module.
💾 Installing `aiida-quantumespresso` from the PyPI.
```

You can then activate the project using the `cda` command described above:

```console
cda firstproject
```

Next to activating the Python virtual environment, this will also change the directory to the one for the project.
`aiida-project` automatically sets up a directory structure, which we intend to be made configurable globally:

```console
(firstproject) ~/project/firstproject$ tree -a
.
├── .aiida
│   ├── access
│   ├── config.json
│   └── daemon
│       └── log
├── code
└── setup
    ├── code
    ├── computer
    └── profile

9 directories, 1 file
```

### `destroy`

Projects can be cleaned up by using `aiida-project destroy`.
First `deactivate` the environment:

```console
deactivate firstproject
```

Next you can run the `destroy` command:

```console
aiida-project destroy firstproject
```
```console
❗️ Are you sure you want to delete the entire firstproject project? This cannot be undone! [y/N]: y
Succes: Project with name firstproject has been destroyed.
```

This will remove both the virtual environment, as well as the whole project folder:

```console
~/project$ tree -a
.
└── .aiida_projects
    ├── conda
    └── virtualenv

3 directories, 0 files
```

## Other features

### `virtualenvwrapper` integration

If you are already using `virtualenvwrapper`, the virtual environments will be installed in the same directory as the one used by `virtualenvwrapper` (i.e. `$WORKON_HOME`).
So you can then also use the

```console
aiida@prnmarvelsrv3:~$ workon firstproject
```

### Environment configuration

Automatically sets some typical AiiDA UNIX environment variables, like AIIDA_PATH and the shell completion (`bash`/`zsh` for now, `fish` support coming soon!):

```console
$ echo $AIIDA_PATH
/Users/mbercx/project/firstproject
```

## Future goals

* For now it just installs AiiDA and plugins, but in the future we want it to be able to also automatically set up the AiiDA database, repository and default profile.

```console
(firstproject) aiida@prnmarvelsrv3:~/project/firstproject$ verdi status
 ✔ version:     AiiDA v2.3.0
 ✔ config:      /home/aiida/project/firstproject/.aiida
 ⏺ profile:     no profile configured yet
Report: Configure a profile by running `verdi quicksetup` or `verdi setup`.
```

* Projects are pydantic data models, and are stored as JSON in the .aiida_projects directory. Over time it should be possible to completely regenerate a project based on this file, but that’s still a work in progress:

```console
(firstproject) aiida@prnmarvelsrv3:~/project/firstproject$ cd ..
(firstproject) aiida@prnmarvelsrv3:~/project$ tree -a .aiida_projects/
.aiida_projects/
├── conda
└── virtualenv
    └── firstproject.json

2 directories, 1 file
```
