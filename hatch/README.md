# pychub-hatch-plugin

This pychub plugin is part of the pychub-build-plugins project. If you are here,
you should already be familiar with pychub. If not, please read the pychub
documentation. You can find it on [github](https://github.com/Steve973/pychub),
or on [pypi](https://pypi.org/project/pychub/). The information located in those
locations will describe the operation of pychub. This document will describe
how to use pychub in a `pyproject.toml` file when building with hatch.

## Prerequisites

You should already have a `pyproject.toml` file that builds a wheel of your
project with the hatch build backend. Once you have completed that, you can
continue by adding the `pychub-hatch-plugin` to your `pyproject.toml` file.

## Using the Plugin

Usage of the plugin is straightforward, and only requires the addition of the
plugin to your `pyproject.toml` file, and the standard `pychub` configuration.

### Adding the Plugin To Your `pyproject.toml` File

Add the build hooks header to your `pyproject.toml` file so that the pychub
plugin can operate on the wheel building phase:

```toml
[tool.hatch.build.targets.wheel.hooks.pychub]
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
test = "hatch"
```

### Plugin Execution

Once you have configured the plugin, you can run `hatch build` and the plugin
will execute. Your `dist` directory will contain the wheel and the `pychub`
file.
