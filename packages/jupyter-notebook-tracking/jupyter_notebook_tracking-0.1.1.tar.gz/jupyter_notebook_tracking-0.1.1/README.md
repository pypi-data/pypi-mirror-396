# Jupyter Notebook Tracking

A juypterlab extension to record who edited the notebook, when and for how long.

Suitable for Juypterhub deployments, as it looks for JUPYTERHUB_USER.

Tracking data is updated on each notebook save, then stored under the `metadata.tracking` key in the notebook's JSON:

Example:
```
    total_edit_time_seconds: 270
    last_edit_by: mary
    editors:
        tom: 120
        mary: 150
    history:
        - bytes: 6796
          edit_time_seconds: 100
          timestamp: "YYYY-MM-DDTHH:mm:ss.nnnZ"
          user: tom
        - bytes: 7980
          edit_time_seconds: 20
          timestamp: "YYYY-MM-DDTHH:mm:ss.nnnZ"
          user: tom
        - bytes: 12900
          edit_time_seconds: 150
          timestamp: "YYYY-MM-DDTHH:mm:ss.nnnZ"
          user: mary
```

## Requirements

- JupyterLab >= 4.0.0

## Install

To install the extension, execute:

```bash
pip install jupyter_notebook_tracking
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall jupyter_notebook_tracking
```

## Contributing

### Development install

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of
[yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use
`yarn` or `npm` in lieu of `jlpm` below.

```bash
# Clone the repo to your local environment
# Change directory to the jupyter_notebook_tracking directory

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
pip uninstall jupyter_notebook_tracking
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `jupyter_notebook_tracking` within that folder.

### Packaging the extension

See [RELEASE](RELEASE.md)
