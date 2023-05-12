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

# Changelog

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
