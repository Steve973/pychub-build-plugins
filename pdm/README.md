# pychub-pdm-plugin

This pychub plugin is part of the pychub-build-plugins project. If you are here,
you should already be familiar with pychub. If not, please read the pychub
documentation. You can find it on [github](https://github.com/Steve973/pychub),
or on [pypi](https://pypi.org/project/pychub/). The information located in those
locations will describe the operation of pychub. This document will describe
how to use pychub in a `pyproject.toml` file when building with pdm.

## Prerequisites

You should already have a `pyproject.toml` file that builds a wheel of your
project with the pdm build backend. Once you have completed that, you can
continue by adding the `pychub-pdm-plugin` to your `pyproject.toml` file.

## Using the Plugin

Usage of the plugin is straightforward, and only requires the addition of the
plugin to your `pyproject.toml` file, and the standard `pychub` configuration.

### Adding the Plugin To Your `pyproject.toml` File

Amend your `[build-system]` section so that the `requires` array includes the
plugin name:

```toml
[build-system]
requires = ["pdm-backend", "pychub-pdm-plugin"]
build-backend = "pdm.backend"
```

### Configuring the Plugin

Add the `pychub` configuration to your `pyproject.toml` file according to the
`pychub` documentation. Here is an example:

```toml
[tool.pychub.package]
name = "test-proj"
version = "0.0.1"
wheel = "dist/test_pkg-0.0.1-py3-none-any.whl"
includes = [
  "includes/README.md::docs/",
  "includes/test.cfg::conf/",
  "includes/info.txt::etc/other.txt",
  "includes/test.txt"
]

[tool.pychub.package.scripts]
pre  = ["scripts/pre_script.sh"]
post = ["scripts/post_script.sh"]

[tool.pychub.package.metadata]
maintainer = "you@example.com"
test = "pdm"
```

### Plugin Execution

Once you have configured the plugin, you can run `pdm build` and the plugin
will execute. Your `dist` directory will contain the wheel and the `pychub`
file.
