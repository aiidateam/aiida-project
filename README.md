# AiiDA-Project

Tool for managing AiiDA "projects" - Python environments tailored to AiiDA with separated project directories.

| ❗️ This package is still in the early stages of development and we will most likely break the API regularly in new 0.X versions. Be sure to pin the version when installing this package in scripts.|
|---|


## Usage


1. Easy to install globally via `pipx`:

```console
aiida@prnmarvelsrv3:~$ pipx install aiida-project
  installed package aiida-project 0.3.0, Python 3.8.10
  These binaries are now globally available
    - aiida-project
done! ✨ 🌟 ✨
```

2. Create projects with their own virtual environment, and immediately install `aiida-core` and the plugins you need:

```console
aiida@prnmarvelsrv3:~$ aiida-project create firstproject --plugins aiida-quantumespresso
✨ Creating the project environment and directory.
🔧 Adding the AiiDA environment variables to the activate script.
✅ Success! Project created.
💾 Installing the latest release of the AiiDA core module.
💾 Installing aiida-quantumespresso
```

3. Supports virtualenv for now, integrated with virtualenvwrapper (`conda`/`mamba` support coming soon!):

```console
aiida@prnmarvelsrv3:~$ workon firstproject
```

4. Automatically sets some typical AiiDA UNIX environment variables, like AIIDA_PATH and the shell completion (bash for now, `zsh`/`fish` support coming soon!):

```console
(firstproject) aiida@prnmarvelsrv3:~$ cd $AIIDA_PATH
```

5. Automatically sets up a well-organised directory structure, which can be configured globally:

```console
(firstproject) aiida@prnmarvelsrv3:~/project/firstproject$ tree -a
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

6. For now it just installs AiiDA and plugins, but in the future we want it to be able to also automatically set up the AiiDA database, repository and default profile.

```console
(firstproject) aiida@prnmarvelsrv3:~/project/firstproject$ verdi status
 ✔ version:     AiiDA v2.3.0
 ✔ config:      /home/aiida/project/firstproject/.aiida
 ⏺ profile:     no profile configured yet
Report: Configure a profile by running `verdi quicksetup` or `verdi setup`.
```

7. Projects are pydantic data models, and are stored as JSON in the .aiida_projects directory. Over time it should be possible to completely regenerate a project based on this file, but that’s still a work in progress:

```console
(firstproject) aiida@prnmarvelsrv3:~/project/firstproject$ cd ..
(firstproject) aiida@prnmarvelsrv3:~/project$ tree -a .aiida_projects/
.aiida_projects/
├── conda
└── virtualenv
    └── firstproject.json

2 directories, 1 file
```

8. Projects can be cleaned up by using `aiida-project destroy`:

```console
(firstproject) aiida@prnmarvelsrv3:~/project$ aiida-project destroy firstproject
Are you sure you want to delete the entire firstproject project? This cannot be undone! [y/N]: y
(firstproject) aiida@prnmarvelsrv3:~/project$ tree -a
.
└── .aiida_projects
    ├── conda
    └── virtualenv

3 directories, 0 files
```
