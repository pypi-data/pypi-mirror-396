# Changelog

<!-- <START NEW CHANGELOG ENTRY> -->

## 1.0.14

- Fixed conda local environments where `argv[0]` is relative `python` instead of absolute path - now checks `resource_dir` for `.venv` pattern first
- Added GitHub CI/CD workflows for build, test, release automation
- Updated CI to use Python 3.10 to match package requirements
- Added screenshot and reference to sister extension in README

## 1.0.13

- Fixed navigation for local conda environments stored in `.venv` subdirectories
- Extended `.venv` detection to validate segment boundaries

## 1.0.12

- Fixed terminal opening in wrong location (now uses relative path)
- Improved `.venv` detection for conda local environments

## 1.0.11

- Added dynamic kernel provider support (`nb_conda_kernels`, `nb_venv_kernels`)
- Project-aware path resolution - navigates to project root for `.venv` environments
- Pinned Node.js to `>=22,<25` to avoid chalk incompatibility
- Added `skipLibCheck` to fix TypeScript build issues

## 1.0.0

- Initial release
- Right-click context menu on kernel launcher cards
- "Show in File Browser" command
- "Open Terminal at Location" command
- Support for conda and virtualenv environments

<!-- <END NEW CHANGELOG ENTRY> -->
