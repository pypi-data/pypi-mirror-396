# jupyterlab_launcher_navigate_to_kernel_extension

[![GitHub Actions](https://github.com/stellarshenson/jupyterlab_launcher_navigate_to_kernel_extension/actions/workflows/build.yml/badge.svg)](https://github.com/stellarshenson/jupyterlab_launcher_navigate_to_kernel_extension/actions/workflows/build.yml)
[![npm version](https://img.shields.io/npm/v/jupyterlab_launcher_navigate_to_kernel_extension.svg)](https://www.npmjs.com/package/jupyterlab_launcher_navigate_to_kernel_extension)
[![PyPI version](https://img.shields.io/pypi/v/jupyterlab-launcher-navigate-to-kernel-extension.svg)](https://pypi.org/project/jupyterlab-launcher-navigate-to-kernel-extension/)
[![Total PyPI downloads](https://static.pepy.tech/badge/jupyterlab-launcher-navigate-to-kernel-extension)](https://pepy.tech/project/jupyterlab-launcher-navigate-to-kernel-extension)
[![JupyterLab 4](https://img.shields.io/badge/JupyterLab-4-orange.svg)](https://jupyterlab.readthedocs.io/en/stable/)
[![Brought To You By KOLOMOLO](https://img.shields.io/badge/Brought%20To%20You%20By-KOLOMOLO-00ffff?style=flat)](https://kolomolo.com)
[![Donate PayPal](https://img.shields.io/badge/Donate-PayPal-blue?style=flat)](https://www.paypal.com/donate/?hosted_button_id=B4KPBJDLLXTSA)

Right-click on any kernel launcher card to navigate to its project directory or open a terminal there. Intended to help navigate around a busy workspace with many projects. Similar to [jupyterlab_terminal_show_in_file_browser_extension](https://github.com/stellarshenson/jupyterlab_terminal_show_in_file_browser_extension).

![](.resources/screenshot.png)

## Features

- **Show in File Browser** - Navigate to the kernel's project root
- **Open Terminal at Location** - Open terminal at the kernel's project directory
- **Project-aware navigation** - For `.venv` environments, navigates to project root (one level up from `.venv`)
- **Dynamic kernel support** - Works with `nb_conda_kernels` and `nb_venv_kernels` providers

## Requirements

- JupyterLab >= 4.0.0

## Install

```bash
pip install jupyterlab-launcher-navigate-to-kernel-extension
```

## Uninstall

```bash
pip uninstall jupyterlab_launcher_navigate_to_kernel_extension
```
