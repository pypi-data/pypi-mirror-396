# Transformers App

The Transformers App repo acts as a plugin for the `transformers serve` cli command in `transformers`. It completes
the command by adding an "App-like" behaviour:

- The command can be launched as a daemon independently of a Python runtime
- It adds a tray icon to manage it from the taskbar
- It contributes a `settings` page from which different features may be enabled.

## Installation

> [!NOTE] At the time of writing, the app is MacOS-only.


### Custom installation in editable mode

In case you'd like to clone the repo and do modifications yourself, this is the way to go.

This app depends from the `app` branch on the `transformers` repository. You can install it as such:

```shell
pip install git+https://github.com/huggingface/transformers@app
```

or by cloning the repository in case you want to modify `transformers` yourself:

```shell
git clone https://github.com/huggingface/transformers
cd transformers
git checkout app
```

Once installed, you can install this repository as well, either from its