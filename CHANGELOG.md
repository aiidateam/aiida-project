# Changelog

## v0.7.0

The most exciting improvement in this release is the switch to using `uv` in the `venv` projects, which makes creating new projects _a lot_ faster (in a jiffy! 🚀).
We still install `pip` in every project environment, so this change should not affect usage/user experience.
Since `uv` is used in a lot of our CI's and we only use basic features, we don't expect any issues, but please do report any problems you encounter.

Next to this, `aiida-core` and the selected packages via the `-p` option of the `create` command are installed in one go, improving dependency resolution robustness.
Moreover, quite a few new checks are added to make sure the user doesn't override existing projects, and any errors encountered during the project creation or package installation steps are now properly reported back to the user.

### 👌 Improvements

* CLI: Correct help callback [[98f672d](https://github.com/aiidateam/aiida-project/commit/98f672dcce66e25aa586eb8a91f73e9834cef77f)]
* CLI: use `sys.exit` instead of `return` for errors [[96b149c](https://github.com/aiidateam/aiida-project/commit/96b149c1c53b05615f5806695ba54c266e6303e0)]
* Fix init command with empty shell default [[488869a](https://github.com/aiidateam/aiida-project/commit/488869a78bac2e28d53dc2d7a51cf74dccb51a4e)]
* `create`: install packages together [[da3b72b](https://github.com/aiidateam/aiida-project/commit/da3b72be6c3a94299c4173c217520d7a3f01d190)]
* `VenvProject`: switch to `uv` [[fa35979](https://github.com/aiidateam/aiida-project/commit/fa3597967d8541af8d6296600e3892cb67e7b578)]
* `create`: add additional checks and error handling [[5edce0b](https://github.com/aiidateam/aiida-project/commit/5edce0b577091c9365a9fabaa0246e2844bab652)]

### 📚 Documentation

* `README.md`: Fix link to `pipx` installation [[e246d6f](https://github.com/aiidateam/aiida-project/commit/e246d6ffba31c302a91662e07d5966494971e04b)]

### 🔧 Maintenance

* CI: Add "Create and Destroy" job [[9bf803b](https://github.com/aiidateam/aiida-project/commit/9bf803bf1c081a4d191cfc8854f28bfc1b3854ec)]
* CI: Add pre-commit job [[aa4a752](https://github.com/aiidateam/aiida-project/commit/aa4a752e59a4569e0f48af3947723ebba9f3b966)]
* pre-commit: (properly) switch to Ruff [[8ec5948](https://github.com/aiidateam/aiida-project/commit/8ec59486da2ee9d0436f9741e95a205cc0ee126c)]
* Typing: enable `strict` mypy checking [[d59eed4](https://github.com/aiidateam/aiida-project/commit/d59eed4d88ef57a2fdae826271731eb857b519f1)]
* `.gitignore`: add `.vscode` [[c732c5d](https://github.com/aiidateam/aiida-project/commit/c732c5df1b9e8402835eab410d7586a1f85f654f)]

### 📦 Update dependencies

* Python support: drop v3.8, fix v3.9 and add v3.12 & v3.13 [[07e7cfc](https://github.com/aiidateam/aiida-project/commit/07e7cfcb45879a20f5d73d1fd76ae596d32ae899)]
* `dev`: switch `pre-commit` pin to lower bound `>=3.4` [[f1c2ff1](https://github.com/aiidateam/aiida-project/commit/f1c2ff131e03d9dde8768780dc8476511dc27ba7)]
* Update mypy and fix its configuration [[025c3a8](https://github.com/aiidateam/aiida-project/commit/025c3a8366119ac0427b9f4468ecf7d21647fdbc)]
* Remove `py` dependency [[f3bbd05](https://github.com/aiidateam/aiida-project/commit/f3bbd054f2ff3ab862f132bb63dfec90911e9c97)]
* Add `dev` Dependency group [[1856eae](https://github.com/aiidateam/aiida-project/commit/1856eaed051f5a8cc4474d3d18a1d5595f4971c1)]
* 📦 `typer`: remove `all` extra and bump version [[16687a6](https://github.com/aiidateam/aiida-project/commit/16687a678b4dab1a38099e2662272770bba015aa)]

## v0.6.0

### ✨ New features

* Add `fish` support [[d6a299c](https://github.com/aiidateam/aiida-project/commit/d6a299c86603d5860b5d2b7bfa205237686f6651)]

### 🐛 Bug fixes

* Fix `init_lines` string of `zsh`/`bash` [[71dbc6b](https://github.com/aiidateam/aiida-project/commit/71dbc6b30a9ba94456dfa332d08efc491a15e6f7)]
* Refactor `project` subpackage  [[612a917](https://github.com/aiidateam/aiida-project/commit/612a91734ea1dc582b5bb9e9eb254b65f4cee92d)]

### 📚 Documentation

* Tidy up `CHANGELOG.md` [[418ed4b](https://github.com/aiidateam/aiida-project/commit/418ed4b77bb9f1854afeddc218b8240dc325a0b1)]

### ⬆️ Update dependencies

* Upgrade to `pydantic~=2.7`  [[32bebfb](https://github.com/aiidateam/aiida-project/commit/32bebfb9cfbf3d557d2b335a44b6af3bc5eb700e)]

## v0.5.1

Patch release with a small fix related to a change in the `activate` scripts of `venv` for Python 3.10.

### 🐛 Bug fixes

* Fix `append_deactivate_text` for `venv` [[20302b1](https://github.com/aiidateam/aiida-project/commit/20302b1c88aaadcb6352a61635c7887cf68058b2)]

## v0.5.0

The most important change in this release, and a breaking one, is the switch from using `virtualenv` to `venv`.
The main motivation here is that `venv` is part of the standard library since Python 3.3, and hence doesn't require an extra dependency that offers little extra benefits.
This means that when updating to version `0.5.0` from `<=0.4.0`, you will need to move the project directory for `virtualenv` projects to `venv`:

```console
❯ mv $aiida_project_dir/.aiida_projects/virtualenv $aiida_project_dir/.aiida_projects/venv
```

New features and improvements include:

* Install plugins directly from GitHub repositories:

    ```console
    ❯ aiida-project create --plugin git@github.com:bastonero/aiida-vibroscopy.git vibro
    ```

* The `--python` option now tries to resolve the path to the provided Python version instead of requiring a full path.
  The full path to the Python binary is now also shown during project creation:

    ```console
    ❯ aiida-project create --python 3.9 aiida
    ✨ Creating the project directory and environment using the Python binary:
    /opt/homebrew/Cellar/python@3.9/3.9.16/Frameworks/Python.framework/Versions/3.9/bin/python3.9
    ```

### ‼️ Breaking changes

* Switch from `virtualenv` to  `venv` [[bf7b619](https://github.com/aiidateam/aiida-project/commit/bf7b6198edf5a3fe69672019b5d61488e42e4693)]

### ✨ New features

* Allow plugin installs from GitHub repository [[892c685](https://github.com/aiidateam/aiida-project/commit/892c685959d3f0cc72afaccaf7bba6258564cba5)]

### 👌 Improvements

* Improve `init` and `create` messaging [[2b57b99](https://github.com/aiidateam/aiida-project/commit/2b57b9965881c6ea39237aeab5fe6c013effba42)]
* CLI: improve `create --python` versatility [[d16c4e9](https://github.com/aiidateam/aiida-project/commit/d16c4e9f7e81895a56cb8c97a660977870cf3b47)]

### 🐛 Bug fixes

* CLI: Fix typo in `create --python` option [[f856612](https://github.com/aiidateam/aiida-project/commit/f856612a126939ad73595d2a6e45e9814422e075)]

### 📚 Documentation

* Update `README.md` [[8f3d5ea](https://github.com/aiidateam/aiida-project/commit/8f3d5eac99a99d8aa9faa800bce09ee6d7ad1578)]

### ⬆️ Update dependencies

* Dependencies: update `pydantic` dependency [[2564715](https://github.com/aiidateam/aiida-project/commit/25647151ff1520fa021b7d7a96c5016173862799)]

## v0.4.0

The entire CLI has been converted into `typer` for clearer and richer output.
A new `aiida-project init` command has also been added, which allows the user to specify the shell they are using and sets up the (currently default) configuration in the `$HOME/.aiida_project.env` file:

```console
❯ aiida-project init
👋 Hello there! Which shell are you using? (zsh detected) [bash/zsh/fish]: zsh
✨🚀 AiiDA-project has been initialised! 🚀✨
```

### ✨ New features

* CLI: Add `init` command [[ea53b83](https://github.com/aiidateam/aiida-project/commit/ea53b83898c4512464a51af96b68048fd5ccecbd)]

### 👌 Improvements

* CLI: Switch to using `typer` [[048deac](https://github.com/aiidateam/aiida-project/commit/048deac75691537f0ccfae6d1ff2cc2fa3194a91)]

### 📚 Documentation

* Update `README.md` with warning and basic usage [[8aca30c](https://github.com/aiidateam/aiida-project/commit/8aca30c32de0351d19534c9bf6673683c178ea6d)]

### 🔧 Maintenance

* Devops: Add `update_changelog.py` script [[fbb4af9](https://github.com/aiidateam/aiida-project/commit/fbb4af9287c82e7517f5732eb6238b258c22d708)]

### ❓ Other

* Provide error message for disabled `conda` engine [[979cf91](https://github.com/aiidateam/aiida-project/commit/979cf91eda4cb024ede8412c1eef7c9274849735)]

## 0.3.0

Major overhaul of the entire package, the details of which can be found in [the corresponding commit message](https://github.com/aiidateam/aiida-project/commit/a799ddc0763ca12ed179c821125bef6a4acb116d).
Also added the `aiida-project destroy` command to remove project folders as well as their Python environments.


### ‼️ Breaking changes

* [Overhaul entire package for `virtualenv`](https://github.com/aiidateam/aiida-project/commit/a799ddc0763ca12ed179c821125bef6a4acb116d)

### ✨ New features

* [Create default directory structure](https://github.com/aiidateam/aiida-project/commit/ceeda2f64c59366616db00d5d51b323087924f41)
* [Add the `aiida-project destroy` command](https://github.com/aiidateam/aiida-project/commit/260303e0dada0a8ace5c76c6ccb8539aece69614)

### 🔧 Maintenance

* [MAINTAIN: Update linting settings](https://github.com/aiidateam/aiida-project/commit/8fbc7de818820445acc31631e59af258395796fd)
* [MAINTAIN: Add `.pre-commit-config.yaml`](https://github.com/aiidateam/aiida-project/commit/938fce0a52c8f393adae9327785ff4fbeea0b4a2)

---

## 0.2.0

Only one change in this pre-alpha version:

* 🔧 MAINTAIN: addition of an automated GitHub workflow to streamline the release process.

---

## 0.1.0

This is the original version version developed by @DropD, fixed so it can be installed and the basic features are operational.
