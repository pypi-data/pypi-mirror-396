# jupyterlab_expand_selection

[![Github Actions Status](/workflows/Build/badge.svg)](/actions/workflows/build.yml)

A JupyterLab extension that introduces expand/shrink selection commands

JupyterLab extension wrapping [codemirror-expand-selection](https://www.npmjs.com/package/codemirror-expand-selection).
Inspired by Emacs' **expand-region** and **expreg**, this extension provides commands to expand and shrink selections in CodeMirror editors inside JupyterLab.

## Features

This extension adds the following commands, configurable via JupyterLab's **Advanced Keyboard Shortcuts Editor**:

- `jupyterlab-expand-selection:expand-selection`
  Expand the current selection to a larger syntactic unit.

- `jupyterlab-expand-selection:shrink-selection`
  Shrink the current selection back to a smaller unit.

- `jupyterlab-expand-selection:swap-anchor-head`
  Swap the anchor and head of the current selection.

## Usage

1. Open JupyterLab.
2. Go to Settings → Advanced Settings Editor → Keyboard Shortcuts.
3. Add keybindings for the provided commands. For example:

```json
{
  "shortcuts": [
    {
      "command": "jupyterlab-expand-selection:expand-selection",
      "keys": ["Ctrl Alt Space"],
      "selector": ".jp-Notebook .cm-content"
    },
    {
      "command": "jupyterlab-expand-selection:shrink-selection",
      "keys": ["Ctrl Alt Shift Space"],
      "selector": ".jp-Notebook .cm-content"
    },
    {
      "command": "jupyterlab-expand-selection:swap-anchor-head",
      "keys": ["Ctrl T"],
      "selector": ".jp-Notebook .cm-content"
    }
  ]
}
```

## Requirements

- JupyterLab >= 4.0.0

## Install

To install the extension, execute:

```bash
pip install jupyterlab-expand-selection
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall jupyterlab_expand_selection
```

## Contributing

### Development install

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of
[yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use
`yarn` or `npm` in lieu of `jlpm` below.

```bash
# Clone the repo to your local environment
# Change directory to the jupyterlab_expand_selection directory

# Set up a virtual environment and install package in development mode
python -m venv .venv
source .venv/bin/activate
pip install --editable "."

# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite

# Rebuild extension Typescript source after making changes
# IMPORTANT: Unlike the steps above which are performed only once, do this step
# every time you make a change.
jlpm build
```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Development uninstall

```bash
pip uninstall jupyterlab_expand_selection
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `jupyterlab-expand-selection` within that folder.

### Packaging the extension

See [RELEASE](RELEASE.md)

## License

BSD 3-Clause License
